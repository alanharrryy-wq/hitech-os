from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from code_atlas.intelligence import AuthorityRequirementError, IntelligenceRequest, resolve_intelligence_context

from .authority_pack import build_authority_pack
from .change_studio import compose_change_model
from .contracts import ContractError, normalize_repo_path, path_matches_scope, sha256_json
from .policy import validate_policy_pack
from .verification import verify_change

PREPARATION_SCHEMA = "code_atlas_change_preparation.v1"


def _sha_lock(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text.startswith("sha256:") and len(text) == 71:
        return text
    if len(text) == 64 and all(ch in "0123456789abcdef" for ch in text):
        return "sha256:" + text
    return sha256_json(value)


def _validated_policy(policy: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if policy is None:
        return None
    return validate_policy_pack(policy)


def _is_mutable_graph_path(value: Any, mutable_scope: Sequence[str]) -> bool:
    if not mutable_scope or not isinstance(value, str) or not value.strip() or value.startswith("reason:"):
        return False
    try:
        return path_matches_scope(value, mutable_scope)
    except ContractError:
        return False


def _stable_evidence_digest(context: Mapping[str, Any], mutable_scope: Sequence[str]) -> str:
    """Lock evidence outside the explicitly authorized mutable scope.

    A legitimate edit to an allowed target must not invalidate its own authority
    pack merely because that file also appears as repository evidence. Everything
    outside allowedScope remains locked and any drift there fails closed.
    """
    graph = deepcopy((context.get("graphs") or {}).get("evidenceGraph") or {})
    nodes = [
        node for node in graph.get("nodes") or []
        if not _is_mutable_graph_path(node.get("id") if isinstance(node, Mapping) else None, mutable_scope)
    ]
    edges = [
        edge for edge in graph.get("edges") or []
        if isinstance(edge, Mapping)
        and not _is_mutable_graph_path(edge.get("from"), mutable_scope)
        and not _is_mutable_graph_path(edge.get("to"), mutable_scope)
    ]
    stable_graph = {
        "nodes": nodes,
        "edges": edges,
        "edgeCount": len(edges),
        "mutableScopeExcluded": sorted(set(mutable_scope)),
        "rule": "LOCK_EVIDENCE_OUTSIDE_EXPLICIT_ALLOWED_SCOPE",
    }
    return sha256_json(stable_graph)


def _repository_snapshot(
    context: Mapping[str, Any],
    policy_digest: str | None,
    mutable_scope: Sequence[str] | None = None,
) -> dict[str, Any]:
    portable = context.get("snapshot") or {}
    repository = portable.get("repository") or {}
    remote = repository.get("remote")
    repo_name = Path(str(context.get("repoRoot") or "repository")).name or "repository"
    repository_identity_seed = {"remote": remote} if remote else {"repoName": repo_name}
    repository_identity = "repo:" + sha256_json(repository_identity_seed).split(":", 1)[1]
    head = repository.get("head")
    tree = repository.get("tree")
    profile = context.get("profile") or {}
    profile_version = str(profile.get("version") or profile.get("id") or "generic-v1")
    scanner_version = str(portable.get("scannerVersion") or "code_atlas_universal_intelligence.v1")
    mutable = tuple(dict.fromkeys(normalize_repo_path(path) for path in (mutable_scope or [])))
    return {
        "repositoryIdentity": repository_identity,
        "commitIdentity": str(head or ("snapshot:" + str(portable.get("snapshotDigest") or "unknown"))),
        "treeIdentity": str(tree or ("inventory:" + str(portable.get("inventoryDigest") or "unknown"))),
        "gitCommitTreeAvailable": bool(head and tree),
        "authorityDigest": _sha_lock(portable.get("authorityDigest")),
        "policyDigest": policy_digest,
        "evidenceDigest": _stable_evidence_digest(context, mutable),
        "evidenceLockExcludedScope": list(mutable),
        "toolVersion": scanner_version,
        "profileVersion": profile_version,
        "snapshotDigest": portable.get("snapshotDigest"),
    }


def _authority_references(authorities: Mapping[str, Any], required: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in authorities.get("candidates") or []:
        path = str(candidate.get("path") or "")
        state = str(candidate.get("state") or "CANDIDATE")
        if path not in required and state not in {"AUTHORITATIVE", "CONFLICTED"}:
            continue
        rows.append({
            "path": path,
            "state": state,
            "sha256": candidate.get("contentSha256"),
            "whySelected": list(candidate.get("whySelected") or []),
            "doesNotProve": list(candidate.get("doesNotProve") or []),
        })
    return rows


def _target_rows(context: Mapping[str, Any], targets: Sequence[str]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    inventory = context.get("inventory") or {}
    by_path = {
        str(row.get("path")): row
        for row in inventory.get("files") or []
        if isinstance(row, Mapping) and row.get("path")
    }
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    unknowns: list[str] = []
    for target in targets:
        row = by_path.get(target)
        if not row or not row.get("exists"):
            rows.append({
                "path": target,
                "reason": "explicitly nominated target is not present in the captured repository inventory",
                "supportLevel": "UNKNOWN",
                "evidenceReferences": [],
            })
            blockers.append(f"nominated target not found: {target}")
            continue
        digest = row.get("contentSha256") or row.get("fileSha256")
        if row.get("sensitiveName") or not digest:
            rows.append({
                "path": target,
                "reason": "target exists but content evidence is intentionally unavailable or unreadable",
                "supportLevel": "UNKNOWN",
                "evidenceReferences": [],
            })
            blockers.append(f"target lacks safe content evidence: {target}")
            unknowns.append(f"target content evidence unavailable: {target}")
            continue
        rows.append({
            "path": target,
            "reason": "explicitly nominated target exists in the canonical repository inventory",
            "supportLevel": "SUPPORTED",
            "evidenceReferences": [{
                "kind": "repository-file",
                "path": target,
                "sha256": digest,
                "inventorySource": inventory.get("inventorySource"),
            }],
        })
    return rows, blockers, unknowns


def _required_evidence(policy: Mapping[str, Any] | None) -> tuple[list[str], list[str], list[dict[str, Any]]]:
    if not policy:
        return [], [], []
    checks = list(dict.fromkeys(str(x) for x in policy.get("requiredTests") or []))
    evidence = list(dict.fromkeys(
        [str(x) for x in policy.get("domainEvidenceRequirements") or []]
        + [f"review:{x}" for x in policy.get("requiredReviews") or []]
    ))
    rows = (
        [{"id": item, "kind": "check", "status": "PENDING"} for item in checks]
        + [{"id": item, "kind": "evidence", "status": "PENDING"} for item in evidence]
    )
    return checks, evidence, rows


def _blocked_without_pack(
    *,
    decision: str,
    reason_codes: list[str],
    context: Mapping[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    return {
        "schemaVersion": PREPARATION_SCHEMA,
        "decision": decision,
        "reasonCodes": reason_codes,
        "error": error,
        "repositorySnapshot": _repository_snapshot(context, None) if context else None,
        "portableSnapshot": (context or {}).get("snapshot") if context else None,
        "changeModel": None,
        "authorityPack": None,
        "readOnly": True,
        "certifiable": False,
        "productionCertified": False,
    }


def prepare_change(
    repo_root: str | Path,
    *,
    change_request: str,
    target_paths: Sequence[str] | None = None,
    output_root: str | Path | None = None,
    profile_path: str | Path | None = None,
    policy: Mapping[str, Any] | None = None,
    domain: str = "",
    intent: str = "VERIFY",
    additional_allowed_scope: Sequence[str] | None = None,
    workers: int = 18,
) -> dict[str, Any]:
    if not isinstance(change_request, str) or not change_request.strip():
        raise ContractError("change_request must be a non-empty string")
    normalized_policy = _validated_policy(policy)
    required_authorities = tuple((normalized_policy or {}).get("requiredAuthorities") or [])
    targets = tuple(dict.fromkeys(normalize_repo_path(path) for path in (target_paths or [])))
    explicit_extra_scope = tuple(dict.fromkeys(normalize_repo_path(path) for path in (additional_allowed_scope or [])))
    allowed_scope = list(dict.fromkeys([*targets, *explicit_extra_scope]))

    request = IntelligenceRequest(
        intent=intent,
        domain=domain,
        required_authorities=required_authorities,
        changed_paths=targets,
        semantic_query=change_request,
        fail_on_missing_authority=True,
        workers=workers,
    )
    try:
        context = resolve_intelligence_context(
            repo_root,
            output_root,
            profile_path=profile_path,
            request=request,
        )
    except AuthorityRequirementError as exc:
        result = _blocked_without_pack(
            decision="BLOCKED",
            reason_codes=["REQUIRED_AUTHORITY_MISSING"],
            error=str(exc),
        )
        result["domain"] = domain
        result["intent"] = intent
        return result

    policy_digest = (normalized_policy or {}).get("policyDigest")
    repository_snapshot = _repository_snapshot(context, policy_digest, allowed_scope)
    if not targets:
        result = _blocked_without_pack(
            decision="UNKNOWN",
            reason_codes=["EXPLICIT_EVIDENCE_SUPPORTED_TARGET_REQUIRED"],
            context=context,
        )
        result["repositorySnapshot"] = repository_snapshot
        result["domain"] = domain
        result["intent"] = intent
        return result

    primary_targets, blockers, unknowns = _target_rows(context, targets)
    protected_scope = list((normalized_policy or {}).get("protectedPaths") or [])
    protected_overlap = sorted(
        path for path in allowed_scope if any(path_matches_scope(path, [protected]) for protected in protected_scope)
    )
    if protected_overlap:
        blockers.append("allowed scope intersects protected policy scope: " + ", ".join(protected_overlap))

    authorities = context.get("authorities") or {}
    required_set = set(required_authorities)
    required_conflicted = sorted(
        str(row.get("path"))
        for row in authorities.get("candidates") or []
        if row.get("path") in required_set and row.get("state") == "CONFLICTED"
    )
    if required_conflicted:
        blockers.append("required authority conflicted: " + ", ".join(required_conflicted))
    authority_refs = _authority_references(authorities, required_set)

    graphs = context.get("graphs") or {}
    impact = graphs.get("changeImpact") or {}
    related_targets = [
        {
            "path": path,
            "reason": "static transitive reverse-dependency impact; informational, not authorization",
            "supportLevel": "INFERRED",
            "evidenceReferences": [{"kind": "change-impact", "impactRule": impact.get("impactRule")}],
        }
        for path in impact.get("impacted") or []
        if path not in targets
    ]
    required_checks, required_evidence_ids, required_rows = _required_evidence(normalized_policy)
    if not repository_snapshot["gitCommitTreeAvailable"]:
        blockers.append("git commit/tree identity is required before issuing an authority pack")

    provenance = [{
        "source": "code_atlas.intelligence.resolve_intelligence_context",
        "contextSchemaVersion": context.get("schemaVersion"),
        "snapshotDigest": (context.get("snapshot") or {}).get("snapshotDigest"),
        "requestDigest": authorities.get("requestDigest"),
        "authorityDigest": repository_snapshot.get("authorityDigest"),
        "evidenceDigest": repository_snapshot.get("evidenceDigest"),
        "evidenceLockExcludedScope": repository_snapshot.get("evidenceLockExcludedScope"),
        "semanticRetrievalIsProof": False,
        "derivedIndexAuthoritative": False,
    }]
    facts = [
        {
            "kind": "repository-target",
            "path": row["path"],
            "supportLevel": row["supportLevel"],
            "evidenceReferences": row["evidenceReferences"],
        }
        for row in primary_targets
    ]
    inferences = [{
        "kind": "static-change-impact",
        "rule": impact.get("impactRule"),
        "impactedPaths": list(impact.get("impacted") or []),
        "owners": list(impact.get("owners") or []),
        "doesNotProve": list(impact.get("doesNotProve") or []),
    }]
    change_model = compose_change_model(
        normalized_intent=change_request,
        repository_snapshot=repository_snapshot,
        primary_targets=primary_targets,
        related_targets=related_targets,
        impact_radius=impact,
        protected_scope=protected_scope,
        authority_references=authority_refs,
        facts=facts,
        inferences=inferences,
        unknowns=unknowns,
        contradictions=[f"required authority conflict: {path}" for path in required_conflicted],
        required_evidence=required_rows,
        blockers=blockers,
        provenance=provenance,
    )

    authority_pack = None
    if change_model["decision"] == "PASS":
        target_evidence = [ref for row in primary_targets for ref in row.get("evidenceReferences") or []]
        authority_pack = build_authority_pack(
            repository_identity=repository_snapshot["repositoryIdentity"],
            commit_identity=repository_snapshot["commitIdentity"],
            tree_identity=repository_snapshot["treeIdentity"],
            request_digest=str(authorities.get("requestDigest") or "unknown"),
            normalized_task=change_request,
            allowed_scope=allowed_scope,
            protected_scope=protected_scope,
            required_checks=required_checks,
            required_evidence=required_evidence_ids,
            forbidden_operations=list((normalized_policy or {}).get("forbiddenOperations") or []),
            stop_conditions=[
                "required authority becomes missing or conflicted",
                "authority/policy/evidence compatibility lock changes outside allowed scope",
                "protected scope mutation",
                "out-of-scope mutation",
            ],
            unknowns=list(change_model.get("unknowns") or []),
            evidence_references=[*target_evidence, *authority_refs],
            tool_version=repository_snapshot["toolVersion"],
            profile_version=repository_snapshot["profileVersion"],
            authority_resolution={
                "missing": list(authorities.get("missingRequired") or []),
                "conflicted": required_conflicted,
            },
            authority_digest=repository_snapshot.get("authorityDigest"),
            policy_digest=repository_snapshot.get("policyDigest"),
            evidence_digest=repository_snapshot.get("evidenceDigest"),
        )

    return {
        "schemaVersion": PREPARATION_SCHEMA,
        "decision": change_model["decision"],
        "reasonCodes": list(change_model.get("blockers") or []) + list(change_model.get("unknowns") or []),
        "domain": domain,
        "intent": intent,
        "repositorySnapshot": repository_snapshot,
        "portableSnapshot": context.get("snapshot"),
        "coverage": context.get("coverage"),
        "requiredAuthorities": list(required_authorities),
        "policyDigest": policy_digest,
        "changeModel": change_model,
        "authorityPack": authority_pack,
        "readOnly": True,
        "certifiable": False,
        "productionCertified": False,
    }


def verify_prepared_change(
    preparation: Mapping[str, Any],
    repo_root: str | Path,
    *,
    changed_paths: Sequence[str],
    produced_evidence: list[Any] | None = None,
    output_root: str | Path | None = None,
    profile_path: str | Path | None = None,
    policy: Mapping[str, Any] | None = None,
    contradictions: list[str] | None = None,
    new_unknowns: list[str] | None = None,
    agent_session: Mapping[str, Any] | None = None,
    workers: int = 18,
) -> dict[str, Any]:
    if not isinstance(preparation, Mapping):
        raise ContractError("preparation must be an object")
    pack = preparation.get("authorityPack")
    if not isinstance(pack, Mapping):
        return {
            "schemaVersion": "code_atlas_change_verification.v1",
            "decision": str(preparation.get("decision") or "BLOCKED"),
            "findings": [{"code": "NO_AUTHORITY_PACK", "reasonCodes": list(preparation.get("reasonCodes") or [])}],
            "certifiable": False,
            "productionCertified": False,
        }

    normalized_policy = _validated_policy(policy)
    request = IntelligenceRequest(
        intent="VERIFY",
        domain=str(preparation.get("domain") or ""),
        required_authorities=tuple(preparation.get("requiredAuthorities") or []),
        changed_paths=tuple(normalize_repo_path(path) for path in changed_paths),
        fail_on_missing_authority=True,
        workers=workers,
    )
    try:
        context = resolve_intelligence_context(
            repo_root,
            output_root,
            profile_path=profile_path,
            request=request,
        )
    except AuthorityRequirementError as exc:
        return {
            "schemaVersion": "code_atlas_change_verification.v1",
            "decision": "BLOCKED",
            "packId": pack.get("packId"),
            "findings": [{"code": "REQUIRED_AUTHORITY_MISSING", "detail": str(exc)}],
            "certifiable": False,
            "productionCertified": False,
        }

    current_snapshot = _repository_snapshot(
        context,
        (normalized_policy or {}).get("policyDigest"),
        list(pack.get("allowedScope") or []),
    )
    report = verify_change(
        authority_pack=pack,
        change_manifest={"changedPaths": [normalize_repo_path(path) for path in changed_paths]},
        current_snapshot=current_snapshot,
        produced_evidence=produced_evidence,
        contradictions=contradictions,
        new_unknowns=new_unknowns,
        agent_session=agent_session,
    )
    report["universalContext"] = {
        "schemaVersion": context.get("schemaVersion"),
        "snapshotDigest": (context.get("snapshot") or {}).get("snapshotDigest"),
        "coverage": context.get("coverage"),
        "evidenceLockExcludedScope": current_snapshot.get("evidenceLockExcludedScope"),
        "semanticRetrievalIsProof": False,
        "derivedIndexAuthoritative": False,
    }
    report.pop("reportDigest", None)
    report["reportDigest"] = sha256_json(report)
    return report
