from __future__ import annotations

from typing import Any, Iterable, Mapping

from .authority_pack import validate_authority_pack
from .contracts import (
    VERIFY_SCHEMA,
    ContractError,
    decision_precedence,
    normalize_repo_path,
    path_matches_scope,
    require_nonempty_string,
    sha256_json,
    utc_now_iso,
)
from .unknown_obligations import build_unknown_obligation, normalize_unknown_obligations


def _evidence_ids(produced: Iterable[Any]) -> set[str]:
    result: set[str] = set()
    for item in produced:
        if isinstance(item, str):
            result.add(item.strip())
        elif isinstance(item, Mapping):
            value = item.get("id") or item.get("evidenceId") or item.get("checkId")
            if isinstance(value, str) and value.strip():
                result.add(value.strip())
    return {value for value in result if value}


def verify_change(
    *,
    authority_pack: Mapping[str, Any],
    change_manifest: Mapping[str, Any],
    current_snapshot: Mapping[str, Any],
    produced_evidence: list[Any] | None = None,
    contradictions: list[str] | None = None,
    new_unknowns: list[str] | None = None,
    agent_session: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pack = validate_authority_pack(authority_pack)
    if not isinstance(change_manifest, Mapping):
        raise ContractError("change_manifest must be an object")
    if not isinstance(current_snapshot, Mapping):
        raise ContractError("current_snapshot must be an object")

    findings: list[dict[str, Any]] = []
    unknown_obligations: list[dict[str, Any]] = []
    blocking = False
    uncertain = False

    for key, pack_field in (
        ("repositoryIdentity", "repositoryIdentity"),
        ("commitIdentity", "commitIdentity"),
        ("treeIdentity", "treeIdentity"),
    ):
        actual = require_nonempty_string(current_snapshot.get(key), f"current_snapshot.{key}")
        if actual != pack[pack_field]:
            blocking = True
            findings.append({"code": "STALE_SNAPSHOT", "field": key, "expected": pack[pack_field], "actual": actual})

    compatibility_locks = pack.get("compatibilityLocks", {}) or {}
    for lock_name in ("authorityDigest", "policyDigest", "evidenceDigest"):
        expected_lock = compatibility_locks.get(lock_name)
        if expected_lock is not None:
            actual_lock = current_snapshot.get(lock_name)
            if actual_lock != expected_lock:
                blocking = True
                findings.append({"code": "COMPATIBILITY_LOCK_MISMATCH", "field": lock_name, "expected": expected_lock, "actual": actual_lock})

    for version_name, pack_field in (("toolVersion", "toolVersion"), ("profileVersion", "profileVersion")):
        if version_name in current_snapshot and current_snapshot.get(version_name) != pack.get(pack_field):
            blocking = True
            findings.append({"code": "VERSION_MISMATCH", "field": version_name, "expected": pack.get(pack_field), "actual": current_snapshot.get(version_name)})

    changed_raw = change_manifest.get("changedPaths", [])
    if not isinstance(changed_raw, list):
        raise ContractError("change_manifest.changedPaths must be a list")
    changed_paths = [normalize_repo_path(path) for path in changed_raw]

    out_of_scope: list[str] = []
    protected_mutations: list[str] = []
    file_compliance: list[dict[str, Any]] = []
    for path in changed_paths:
        allowed = path_matches_scope(path, pack["allowedScope"])
        protected = path_matches_scope(path, pack["protectedScope"])
        if not allowed:
            out_of_scope.append(path)
        if protected:
            protected_mutations.append(path)
        file_compliance.append({"path": path, "allowed": allowed, "protected": protected})

    if out_of_scope:
        blocking = True
        findings.append({"code": "OUT_OF_SCOPE_CHANGE", "paths": sorted(set(out_of_scope))})
    if protected_mutations:
        blocking = True
        findings.append({"code": "PROTECTED_SCOPE_MUTATION", "paths": sorted(set(protected_mutations))})

    evidence_ids = _evidence_ids(produced_evidence or [])
    missing_checks = sorted(set(pack["requiredChecks"]) - evidence_ids)
    missing_evidence = sorted(set(pack["requiredEvidence"]) - evidence_ids)
    if missing_checks:
        blocking = True
        findings.append({"code": "MISSING_REQUIRED_CHECKS", "ids": missing_checks})
    if missing_evidence:
        blocking = True
        findings.append({"code": "MISSING_REQUIRED_EVIDENCE", "ids": missing_evidence})

    if contradictions:
        uncertain = True
        obligations = [
            build_unknown_obligation(
                code="CONTRADICTORY_EVIDENCE",
                source="verify.contradictions",
                reason=str(item),
            )
            for item in contradictions
        ]
        unknown_obligations.extend(obligations)
        findings.append({"code": "CONTRADICTORY_EVIDENCE", "items": list(contradictions), "unknownObligations": obligations})
    if new_unknowns:
        uncertain = True
        obligations = [
            build_unknown_obligation(
                code="NEW_UNKNOWN",
                source="verify.newUnknowns",
                reason=str(item),
            )
            for item in new_unknowns
        ]
        unknown_obligations.extend(obligations)
        findings.append({"code": "NEW_UNKNOWNS", "items": list(new_unknowns), "unknownObligations": obligations})
    if pack.get("unknowns"):
        uncertain = True
        obligations = [
            build_unknown_obligation(
                code="PACK_UNKNOWN",
                source="authority_pack.unknowns",
                reason=str(item),
            )
            for item in pack["unknowns"]
        ]
        unknown_obligations.extend(obligations)
        findings.append({"code": "PACK_UNKNOWNS_REMAIN", "items": list(pack["unknowns"]), "unknownObligations": obligations})

    if agent_session is not None:
        session_pack = agent_session.get("packId") if isinstance(agent_session, Mapping) else None
        if session_pack != pack["packId"]:
            blocking = True
            findings.append({"code": "AGENT_SESSION_PACK_MISMATCH", "expected": pack["packId"], "actual": session_pack})

    decision = decision_precedence("BLOCKED" if blocking else "PASS", "UNKNOWN" if uncertain else "PASS")
    report = {
        "schemaVersion": VERIFY_SCHEMA,
        "decision": decision,
        "packId": pack["packId"],
        "packChecksum": pack["checksum"],
        "repositoryIdentity": pack["repositoryIdentity"],
        "currentSnapshot": dict(current_snapshot),
        "fileCompliance": file_compliance,
        "findings": findings,
        "unknownObligations": normalize_unknown_obligations(unknown_obligations),
        "missingChecks": missing_checks,
        "missingEvidence": missing_evidence,
        "outOfScopeMutations": sorted(set(out_of_scope)),
        "protectedBoundaryViolations": sorted(set(protected_mutations)),
        "doesNotProve": [
            "absence of runtime regressions not covered by produced evidence",
            "production readiness unless separately certified",
            "correctness outside the authority pack scope",
        ],
        "generatedAt": utc_now_iso(),
        "certifiable": False,
        "productionCertified": False,
    }
    report["reportDigest"] = sha256_json(report)
    return report
