#!/usr/bin/env python3
"""Fail-closed source verifier for PRISMA Change Intelligence Cloud Center V1."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

BASE_HEAD = "d14effee1a1223cc772247ea9d7ec8547dc15c78"
CONFIG_PATH_LITERAL = "/internal/config/change_intelligence_cloud.json"
REPOSITORY_PROJECTION_PROFILE = "ci-cloud-repository-registry-adapter-p1-v1"
REPOSITORY_CONNECTED_STATUS = "SOURCE_VERIFIED_READ_ONLY"
ANALYSIS_RUN_CONNECTED_STATUS = "SOURCE_VERIFIED_READ_ONLY"
ANALYSIS_RUN_PROFILE = "ci-cloud-analysis-run-projection-p2-v2"
ANALYSIS_RUN_HEAD = "28b0821d4a3c2b07041a0c4dfe18004f4f7d52ab"
ANALYSIS_RUN_TREE = "f02a5c495d982155d18febc0b81d8a11c0201144"
ANALYSIS_RUN_AUTHORITY_RUN = 32865050216
ANALYSIS_RUN_AUTHORITY_ARTIFACT = 9569864211
ANALYSIS_RUN_AUTHORITY_ARTIFACT_DIGEST = "sha256:677d5e2d93d9a5b23c5cc683e9572645bdd2763f575752af2c628dcb1df9d4ed"
ANALYSIS_RUN_AUTHORITY_REQUEST_DIGEST = "bb146156461837525776f6f40e637a1215ba38581759da4ebb448aea97a08769"
ANALYSIS_RUN_EVIDENCE_RUN = 32865503690
ANALYSIS_RUN_EVIDENCE_ARTIFACT = 9569959132
ANALYSIS_RUN_EVIDENCE_ARTIFACT_DIGEST = "sha256:cd8cd3b5f35a81e9608c0d8aae42fde76a9a822122d292a6a19c2a4973cf0868"
ANALYSIS_RUN_ENGINE_ARTIFACT_SHA256 = "2630c723aaa6d2f692218cb30648020fd41a5eade35d10f4d49129d0c5304103"
ANALYSIS_RUN_REQUEST_DIGEST = "08e828680e7a1afdb26d37cf44e23f2a9fd718249c7011095644b9e9da9e0460"
ANALYSIS_RUN_SNAPSHOT_DIGEST = "7a2893d86119ad6d49bc7bb3bdff08689a6abcbb2c77343399a9cc671bc08913"
ANALYSIS_RUN_ENGINE_STATUS = "PASS_UNIVERSAL_INTELLIGENCE_SOURCE_READY"

AUTHORITY_EVIDENCE_CONNECTED_STATUS = "SOURCE_VERIFIED_READ_ONLY"
AUTHORITY_EVIDENCE_PROFILE = "ca-cloud-authority-evidence-p3-v4"
AUTHORITY_EVIDENCE_HEAD = "0916227707aa65b673195d554297bf8f8565d356"
AUTHORITY_EVIDENCE_TREE = "ad0ff1770eadaee0e5ae717ba7c806da029f9287"
AUTHORITY_EVIDENCE_REPOSITORY_IDENTITY = "repo:7a9a5f159e04eb0c42438ec4a49112c7eafe9340ab2cbd377e68b0a0bbf4f722"
AUTHORITY_EVIDENCE_AUTHORITY_RUN = 32878086011
AUTHORITY_EVIDENCE_AUTHORITY_ARTIFACT = 9574731927
AUTHORITY_EVIDENCE_AUTHORITY_ARTIFACT_DIGEST = "sha256:001102f110e7075607c80fe5ab5b1343d88ee356e85fb08a88c32708d0118e9e"
AUTHORITY_EVIDENCE_AUTHORITY_REQUEST_DIGEST = "9113cb140ae64b2cc3e524908d365b8d7ed9144168a860e6909faca0558cdd74"
AUTHORITY_EVIDENCE_GATE_RUN = 32878629219
AUTHORITY_EVIDENCE_GATE_ARTIFACT = 9574892311
AUTHORITY_EVIDENCE_GATE_ARTIFACT_DIGEST = "sha256:fde3bd4996cdf77e14637343975379a89ebb2de05d02711b9359d720bbdca4b7"
AUTHORITY_EVIDENCE_RUN = 32878380486
AUTHORITY_EVIDENCE_ARTIFACT = 9574817118
AUTHORITY_EVIDENCE_ARTIFACT_DIGEST = "sha256:bf000fac916bc40034d2531a894ee855047c74cf5fb8db1dfe8f3770b73e8995"
AUTHORITY_PACK_ID = "cap.5bc981d182e326a6b684"
AUTHORITY_PACK_CHECKSUM = "sha256:9d225fc13e27a44dd33224112d8c7b7101e3c3ace529a970cdde42fae6874d3b"
AUTHORITY_PACK_REQUEST_DIGEST = "15b6696219f49020620d2f94bdb8aecf9e7dbf5d5a9035cb44dc97ebba95873c"
AUTHORITY_LOCK_DIGEST = "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
EVIDENCE_LOCK_DIGEST = "sha256:7c8470e667d6e89d8c7ebfb6922139a8d7b23c3788a800f70916f7c3c3f80981"
VERIFICATION_REPORT_DIGEST = "sha256:31b36c5d7c19e790d625d104d5de0230339659d71b92e303ef50e35560ee8efa"
EVIDENCE_BUNDLE_MANIFEST_DIGEST = "sha256:06167e8f02653ad82f0c410d39a5a5455be2bb201c305e7860bb404df07d4a20"

ENTITLEMENT_CONNECTED_STATUS = "SOURCE_MAPPED_NOT_GRANTED"
ENTITLEMENT_PROFILE = "ca-cloud-entitlements-p4-v2"
ENTITLEMENT_HEAD = "c388cffd0c926295619d71a583876e5b66f37ceb"
ENTITLEMENT_TREE = "b68b47e1056a527bfa0097ab010c6a4184464703"
ENTITLEMENT_AUTHORITY_RUN = 32923210520
ENTITLEMENT_AUTHORITY_ARTIFACT = 9590560387
ENTITLEMENT_AUTHORITY_ARTIFACT_DIGEST = "sha256:ecced7dc954259787e5198002297e8c4fffd050f133f6646fff38c9fc4c6f88c"
ENTITLEMENT_COMPOSED_SHA256 = "e737962f1aa137c7d7ceb3294fbc19eda7238412c39dcd2a11bf9b17fe20c957"
ENTITLEMENT_AUTHORITY_REQUEST_DIGEST = "d9af6c2505490a0dfb9581bf6e426c5a921887f32ce056f68e259f01ee4ebc14"
ENTITLEMENT_GATE_RUN = 32923389474
ENTITLEMENT_GATE_ARTIFACT = 9590600727
ENTITLEMENT_GATE_ARTIFACT_DIGEST = "sha256:9af868f16239fa98864d4441b6eaafd7731c185e5768db2ab0de8d4a3bf324e4"
ENTITLEMENT_SOURCE_PATH = "apps/terminal-de-venta-system/shared/licensing/customer-setup-contract.ts"
ENTITLEMENT_SOURCE_BLOB = "7bac39a02a7ffaed20f5a725a1c216da07087adf"
ENTITLEMENT_PLAN_FEATURES = {
    "TABLET_SOLO": ["pos.local_sale", "catalog.local", "cash.local"],
    "TABLET_PRO": ["pos.local_sale", "returns", "outbox.visible", "mobile.supervision"],
    "TABLET_PC_MANAGED": ["pos.local_sale", "pc.backoffice", "sync.audit", "mobile.supervision"],
    "TABLET_PC_MOBILE_MANAGED": ["pos.local_sale", "pc.backoffice", "mobile.companion", "customer.setup"],
}

REL = {
    "main_html": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.html"),
    "main_js": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.js"),
    "main_css": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.css"),
    "ci_html": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/change_intelligence_center.html"),
    "ci_style_js": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/change_intelligence_center_style.js"),
    "ci_js": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/change_intelligence_center.js"),
    "ci_config": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/config/change_intelligence_cloud.json"),
    "contract": Path("apps/terminal-de-venta-system/docs/productization/PRISMA_CHANGE_INTELLIGENCE_CLOUD_CENTER_VERTICAL_CONTRACT.md"),
    "verifier": Path("apps/terminal-de-venta-system/tools/verify-cloud-center-change-intelligence-01.py"),
    "runtime_verifier": Path("apps/terminal-de-venta-system/tools/verify-cloud-center-change-intelligence-runtime-01.mjs"),
    "workflow": Path(".github/workflows/change-intelligence-cloud-authority.yml"),
}

ALLOWED_DIFF = {
    REL[key].as_posix()
    for key in ("main_html", "ci_html", "ci_style_js", "ci_js", "ci_config", "contract", "verifier", "runtime_verifier", "workflow")
}
CANONICAL_CLOUD_CENTER_READ_ONLY = {
    REL["main_html"].as_posix(),
    REL["main_css"].as_posix(),
    REL["main_js"].as_posix(),
}
FORBIDDEN_REPOSITORY_FIELD_KEYS = {
    "accesstoken",
    "admintoken",
    "authorizationheader",
    "checkoutpath",
    "cloneurl",
    "credential",
    "credentials",
    "headers",
    "localpath",
    "password",
    "privatekey",
    "rawheaders",
    "secret",
    "secretpath",
    "sourcecontent",
    "sshurl",
    "token",
}


def repo_root() -> Path:
    for candidate in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (candidate / ".git").exists() and (candidate / "apps").exists():
            return candidate
    raise RuntimeError("REPO_ROOT_NOT_FOUND")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(root: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return p.returncode, p.stdout.strip()


def resolve_diff_base(root: Path) -> tuple[str | None, str]:
    """Resolve the effective current PR base without reinterpreting authority provenance."""
    if os.environ.get("GITHUB_EVENT_NAME", "").strip() == "pull_request":
        code, parent = git(root, "rev-parse", "HEAD^1")
        if code == 0 and re.fullmatch(r"[0-9a-fA-F]{40}", parent):
            return parent, "github_pr_merge_first_parent"

    base_ref = os.environ.get("GITHUB_BASE_REF", "").strip()
    candidates: list[str] = []
    if base_ref:
        candidates.extend((f"origin/{base_ref}", base_ref))
    candidates.extend(("origin/main", "main"))

    seen: set[str] = set()
    for ref in candidates:
        if not ref or ref in seen:
            continue
        seen.add(ref)
        code, _ = git(root, "cat-file", "-e", f"{ref}^{{commit}}")
        if code == 0:
            return ref, "git_ref"
    return None, "unavailable"


def normalized_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def forbidden_repository_fields(value: Any, prefix: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if normalized_key(key) in FORBIDDEN_REPOSITORY_FIELD_KEYS:
                findings.append(path)
            findings.extend(forbidden_repository_fields(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(forbidden_repository_fields(child, f"{prefix}[{index}]"))
    return findings


def main() -> int:
    root = repo_root()
    checks: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})
        if not condition:
            errors.append(f"{name}: {detail}")

    p = {k: root / v for k, v in REL.items()}
    for key, path in p.items():
        check(f"file_exists:{key}", path.exists(), REL[key].as_posix())
    if errors:
        return emit(checks, errors, warnings, False)

    main_html, main_js, main_css = text(p["main_html"]), text(p["main_js"]), text(p["main_css"])
    ci_html, ci_style, ci_js = text(p["ci_html"]), text(p["ci_style_js"]), text(p["ci_js"])
    contract, runtime_js, workflow = text(p["contract"]), text(p["runtime_verifier"]), text(p["workflow"])

    try:
        cfg = json.loads(text(p["ci_config"]))
    except Exception as exc:
        check("config_json_parse", False, str(exc))
        cfg = {}
    else:
        check("config_json_parse", True, "change_intelligence_cloud.json")

    generated_from = cfg.get("generatedFrom", {})
    mesh = generated_from.get("authorityMesh", {})
    repository_projection_authority = generated_from.get("repositoryProjectionAuthority", {})
    analysis_projection_authority = generated_from.get("analysisRunProjectionAuthority", {})
    authority_evidence_projection_authority = generated_from.get("authorityEvidenceProjectionAuthority", {})
    entitlement_projection_authority = generated_from.get("entitlementProjectionAuthority", {})
    maturity = cfg.get("maturity", {})
    safety = cfg.get("safety", {})

    check("config_schema", cfg.get("schemaVersion") == "prisma.change_intelligence.cloud_center.vertical.v1", str(cfg.get("schemaVersion")))
    check("authority_base", generated_from.get("baseHead") == BASE_HEAD, str(generated_from.get("baseHead")))
    check("authority_mesh_run", mesh.get("runId") == 32156981312, str(mesh.get("runId")))
    check("authority_mesh_artifact", mesh.get("artifactId") == 9332162633, str(mesh.get("artifactId")))
    check("authority_layer_map", mesh.get("layerMapPresent") is True, str(mesh.get("layerMapPresent")))
    check("authority_coverage", mesh.get("requiredAuthorityCoverage") == "100%", str(mesh.get("requiredAuthorityCoverage")))
    check("maturity_local_verified", maturity.get("engineStatus") == "LOCAL_VERIFIED", str(maturity.get("engineStatus")))
    check("no_certifiable_claim", maturity.get("certifiable") is False, str(maturity.get("certifiable")))
    check("no_production_claim", maturity.get("productionCertified") is False, str(maturity.get("productionCertified")))
    check("human_usefulness_not_measured", maturity.get("humanUsefulness") == "NOT_MEASURED", str(maturity.get("humanUsefulness")))
    check("read_only_default", safety.get("readOnlyDefault") is True, str(safety.get("readOnlyDefault")))
    check("no_fake_green", safety.get("noFakeGreen") is True, str(safety.get("noFakeGreen")))

    owners = {x.get("id"): x for x in cfg.get("sharedOwners", [])}
    required = {
        "customer-registration": "REUSE_AS_IS",
        "licensing-contract-alignment": "SHARED_OWNER",
        "commercial-billing": "SHARED_OWNER",
        "private-repository-rental": "ADAPT",
        "change-intelligence-engine": "REUSE_AS_IS",
    }
    for oid, mode in required.items():
        owner = owners.get(oid, {})
        check(
            f"shared_owner:{oid}",
            owner.get("reuseMode") == mode and owner.get("doNotRebuild") is True,
            f"reuse={owner.get('reuseMode')} doNotRebuild={owner.get('doNotRebuild')}",
        )

    cp = cfg.get("controlPlane", {})
    repositories = cp.get("repositories", {})
    repository_status = repositories.get("status")
    check("repositories_state_supported", repository_status in {"NOT_CONNECTED", REPOSITORY_CONNECTED_STATUS}, str(repository_status))
    if repository_status == "NOT_CONNECTED":
        check("repositories_unbound_items_empty", repositories.get("items") == [], str(repositories.get("items")))
    elif repository_status == REPOSITORY_CONNECTED_STATUS:
        rows = repositories.get("items")
        check("repositories_source_rows_non_empty", isinstance(rows, list) and len(rows) == 1, f"count={len(rows) if isinstance(rows, list) else 'invalid'}")
        check("repository_projection_authority_profile", repository_projection_authority.get("profile") == REPOSITORY_PROJECTION_PROFILE, str(repository_projection_authority.get("profile")))
        check("repository_projection_authority_result", repository_projection_authority.get("result") == "PASS_COMPOSED_AUTHORITY_MESH", str(repository_projection_authority.get("result")))
        check("repository_projection_authority_coverage", repository_projection_authority.get("requiredAuthorityCoverage") == "100%", str(repository_projection_authority.get("requiredAuthorityCoverage")))
        check("repository_projection_authority_blockers", repository_projection_authority.get("blockers") == 0, str(repository_projection_authority.get("blockers")))
        check("repository_projection_authority_drift", repository_projection_authority.get("repoDriftStable") is True, str(repository_projection_authority.get("repoDriftStable")))
        check("repository_projection_authority_lanes", isinstance(repository_projection_authority.get("laneCount"), int) and repository_projection_authority.get("laneCount") >= 2, str(repository_projection_authority.get("laneCount")))
        check("repository_projection_authority_run", isinstance(repository_projection_authority.get("runId"), int) and repository_projection_authority.get("runId") > 0, str(repository_projection_authority.get("runId")))
        check("repository_projection_authority_artifact", isinstance(repository_projection_authority.get("artifactId"), int) and repository_projection_authority.get("artifactId") > 0, str(repository_projection_authority.get("artifactId")))
        check("repository_projection_authority_digest", re.fullmatch(r"sha256:[0-9a-f]{64}", str(repository_projection_authority.get("artifactDigest", ""))) is not None, str(repository_projection_authority.get("artifactDigest")))
        projection_head = str(repository_projection_authority.get("baseHead", ""))
        check("repository_projection_authority_head", re.fullmatch(r"[0-9a-f]{40}", projection_head) is not None, projection_head)
        if isinstance(rows, list):
            for index, row in enumerate(rows):
                prefix = f"repository_row:{index}"
                if not isinstance(row, dict):
                    check(prefix, False, "row must be object")
                    continue
                repository_identity = row.get("repositoryIdentity")
                check(f"{prefix}:identity", isinstance(repository_identity, str) and repository_identity == generated_from.get("repository") and row.get("Repository") == repository_identity, str(repository_identity))
                check(f"{prefix}:status", row.get("Status") == REPOSITORY_CONNECTED_STATUS, str(row.get("Status")))
                check(f"{prefix}:mode", row.get("Mode") == "READ_ONLY", str(row.get("Mode")))
                check(f"{prefix}:provider", isinstance(row.get("provider"), str) and bool(row.get("provider")), str(row.get("provider")))
                authorization = row.get("authorization") if isinstance(row.get("authorization"), dict) else {}
                check(f"{prefix}:authorization_state", authorization.get("state") == "VERIFIED_AT_CAPTURE", str(authorization.get("state")))
                check(f"{prefix}:authorization_source", isinstance(authorization.get("evidenceSource"), str) and bool(authorization.get("evidenceSource")), str(authorization.get("evidenceSource")))
                check(f"{prefix}:authorization_applied_read_only", authorization.get("appliedAccessMode") == "READ_ONLY", str(authorization.get("appliedAccessMode")))
                check(f"{prefix}:authorization_freshness", authorization.get("freshness") == "SNAPSHOT", str(authorization.get("freshness")))
                check(f"{prefix}:authorization_capture_date", re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(authorization.get("capturedAt", ""))) is not None, str(authorization.get("capturedAt")))
                does_not_prove = authorization.get("doesNotProve") if isinstance(authorization.get("doesNotProve"), list) else []
                for boundary in ("future permission persistence", "authorization for any other repository", "hosted multi-tenant execution"):
                    check(f"{prefix}:does_not_prove:{boundary}", boundary in does_not_prove, str(does_not_prove))
                provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
                check(f"{prefix}:provenance_repository_id", isinstance(provenance.get("repositoryId"), str) and bool(provenance.get("repositoryId")), str(provenance.get("repositoryId")))
                check(f"{prefix}:provenance_default_branch", isinstance(provenance.get("defaultBranch"), str) and bool(provenance.get("defaultBranch")), str(provenance.get("defaultBranch")))
                check(f"{prefix}:provenance_head", provenance.get("capturedHead") == projection_head, str(provenance.get("capturedHead")))
                check(f"{prefix}:provenance_visibility", provenance.get("visibility") in {"public", "private", "internal"}, str(provenance.get("visibility")))
                rental = row.get("rentalBoundary") if isinstance(row.get("rentalBoundary"), dict) else {}
                check(f"{prefix}:rental_capability", rental.get("capability") == "ci.rental.private_repo_v2", str(rental.get("capability")))
                check(f"{prefix}:rental_reference_only", rental.get("reuseMode") == "REFERENCE_ONLY", str(rental.get("reuseMode")))
                check(f"{prefix}:source_egress_denied", rental.get("sourceCodeEgress") is False, str(rental.get("sourceCodeEgress")))
                check(f"{prefix}:browser_credentials_denied", rental.get("credentialsInBrowser") is False, str(rental.get("credentialsInBrowser")))
                check(f"{prefix}:cleanup_evidence_required", rental.get("cleanupEvidenceRequired") is True, str(rental.get("cleanupEvidenceRequired")))
                forbidden = forbidden_repository_fields(row)
                check(f"{prefix}:forbidden_fields_absent", not forbidden, str(forbidden))
        projection_rule = str(repositories.get("projectionRule", ""))
        freshness_rule = str(repositories.get("freshnessRule", ""))
        check("repositories_projection_rule_read_only", "READ_ONLY" in projection_rule and "source-backed" in projection_rule, projection_rule)
        check("repositories_freshness_rule_recheck", "Re-check" in freshness_rule and "stale" in freshness_rule, freshness_rule)

    analysis_runs = cp.get("analysisRuns", {})
    analysis_status = analysis_runs.get("status")
    check("analysis_runs_state_supported", analysis_status in {"NOT_CONNECTED", ANALYSIS_RUN_CONNECTED_STATUS}, str(analysis_status))
    if analysis_status == "NOT_CONNECTED":
        check("analysis_runs_unbound_items_empty", analysis_runs.get("items") == [], str(analysis_runs.get("items")))
    elif analysis_status == ANALYSIS_RUN_CONNECTED_STATUS:
        checks_exact = {
            "analysis_authority_head": (analysis_projection_authority.get("baseHead"), ANALYSIS_RUN_HEAD),
            "analysis_authority_profile": (analysis_projection_authority.get("profile"), ANALYSIS_RUN_PROFILE),
            "analysis_authority_run": (analysis_projection_authority.get("authorityRunId"), ANALYSIS_RUN_AUTHORITY_RUN),
            "analysis_authority_artifact": (analysis_projection_authority.get("authorityArtifactId"), ANALYSIS_RUN_AUTHORITY_ARTIFACT),
            "analysis_authority_artifact_digest": (analysis_projection_authority.get("authorityArtifactDigest"), ANALYSIS_RUN_AUTHORITY_ARTIFACT_DIGEST),
            "analysis_authority_request_digest": (analysis_projection_authority.get("authorityRequestDigest"), ANALYSIS_RUN_AUTHORITY_REQUEST_DIGEST),
            "analysis_authority_result": (analysis_projection_authority.get("authorityResult"), "PASS_COMPOSED_AUTHORITY_MESH"),
            "analysis_authority_lanes": (analysis_projection_authority.get("laneCount"), 2),
            "analysis_authority_coverage": (analysis_projection_authority.get("requiredAuthorityCoverage"), "100%"),
            "analysis_authority_blockers": (analysis_projection_authority.get("blockers"), 0),
            "analysis_authority_drift": (analysis_projection_authority.get("repoDriftStable"), True),
            "analysis_evidence_run": (analysis_projection_authority.get("evidenceRunId"), ANALYSIS_RUN_EVIDENCE_RUN),
            "analysis_evidence_artifact": (analysis_projection_authority.get("evidenceArtifactId"), ANALYSIS_RUN_EVIDENCE_ARTIFACT),
            "analysis_evidence_artifact_digest": (analysis_projection_authority.get("evidenceArtifactDigest"), ANALYSIS_RUN_EVIDENCE_ARTIFACT_DIGEST),
            "analysis_engine_artifact_digest": (analysis_projection_authority.get("engineArtifactSha256"), ANALYSIS_RUN_ENGINE_ARTIFACT_SHA256),
        }
        for name, (actual, expected) in checks_exact.items():
            check(name, actual == expected, f"actual={actual} expected={expected}")

        rows = analysis_runs.get("items")
        check("analysis_rows_exactly_one", isinstance(rows, list) and len(rows) == 1, f"count={len(rows) if isinstance(rows, list) else 'invalid'}")
        if isinstance(rows, list) and len(rows) == 1 and isinstance(rows[0], dict):
            row = rows[0]
            provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
            evidence = row.get("evidence") if isinstance(row.get("evidence"), dict) else {}
            row_exact = {
                "analysis_row_run": (row.get("Run"), "code-atlas-discover-28b0821d"),
                "analysis_row_repository": (row.get("Repository"), generated_from.get("repository")),
                "analysis_row_intent": (row.get("Intent"), "DISCOVER"),
                "analysis_row_status": (row.get("Status"), ANALYSIS_RUN_ENGINE_STATUS),
                "analysis_row_head": (provenance.get("repoHead"), ANALYSIS_RUN_HEAD),
                "analysis_row_tree": (provenance.get("repoTree"), ANALYSIS_RUN_TREE),
                "analysis_row_profile": (provenance.get("profileId"), "generic"),
                "analysis_row_domain": (provenance.get("domain"), "runtime"),
                "analysis_row_request_digest": (provenance.get("requestDigest"), ANALYSIS_RUN_REQUEST_DIGEST),
                "analysis_row_snapshot_digest": (provenance.get("snapshotDigest"), ANALYSIS_RUN_SNAPSHOT_DIGEST),
                "analysis_row_engine_artifact": (provenance.get("engineArtifactSha256"), ANALYSIS_RUN_ENGINE_ARTIFACT_SHA256),
                "analysis_row_evidence_run": (evidence.get("workflowRunId"), ANALYSIS_RUN_EVIDENCE_RUN),
                "analysis_row_evidence_artifact": (evidence.get("artifactId"), ANALYSIS_RUN_EVIDENCE_ARTIFACT),
                "analysis_row_evidence_digest": (evidence.get("artifactDigest"), ANALYSIS_RUN_EVIDENCE_ARTIFACT_DIGEST),
                "analysis_row_read_only": (row.get("readOnly"), True),
                "analysis_row_derived_index_non_authority": (row.get("derivedIndexAuthoritative"), False),
                "analysis_row_retrieval_not_proof": (row.get("semanticRetrievalIsProof"), False),
                "analysis_row_profile_no_truth_invention": (row.get("profileMayInventTruth"), False),
                "analysis_row_not_production": (row.get("productionCertified"), False),
            }
            for name, (actual, expected) in row_exact.items():
                check(name, actual == expected, f"actual={actual} expected={expected}")
            does_not_prove = row.get("doesNotProve") if isinstance(row.get("doesNotProve"), list) else []
            for boundary in (
                "production readiness",
                "hosted multi-tenant execution",
                "enterprise IAM or security readiness",
                "human usefulness",
                "independent-agent verification",
                "authorization to mutate the repository",
            ):
                check(f"analysis_row_does_not_prove:{boundary}", boundary in does_not_prove, str(does_not_prove))
            forbidden = forbidden_repository_fields(row)
            check("analysis_row_forbidden_fields_absent", not forbidden, str(forbidden))
        projection_rule = str(analysis_runs.get("projectionRule", ""))
        check("analysis_projection_rule_immutable", "immutable" in projection_rule and "HEAD/tree" in projection_rule and "not promoted" in projection_rule, projection_rule)

    p3_authority_exact = {
        "authority_evidence_head": (authority_evidence_projection_authority.get("baseHead"), AUTHORITY_EVIDENCE_HEAD),
        "authority_evidence_tree": (authority_evidence_projection_authority.get("baseTree"), AUTHORITY_EVIDENCE_TREE),
        "authority_evidence_profile": (authority_evidence_projection_authority.get("profile"), AUTHORITY_EVIDENCE_PROFILE),
        "authority_evidence_authority_run": (authority_evidence_projection_authority.get("authorityRunId"), AUTHORITY_EVIDENCE_AUTHORITY_RUN),
        "authority_evidence_authority_artifact": (authority_evidence_projection_authority.get("authorityArtifactId"), AUTHORITY_EVIDENCE_AUTHORITY_ARTIFACT),
        "authority_evidence_authority_artifact_digest": (authority_evidence_projection_authority.get("authorityArtifactDigest"), AUTHORITY_EVIDENCE_AUTHORITY_ARTIFACT_DIGEST),
        "authority_evidence_authority_request_digest": (authority_evidence_projection_authority.get("authorityRequestDigest"), AUTHORITY_EVIDENCE_AUTHORITY_REQUEST_DIGEST),
        "authority_evidence_authority_result": (authority_evidence_projection_authority.get("authorityResult"), "PASS_COMPOSED_AUTHORITY_MESH"),
        "authority_evidence_lanes": (authority_evidence_projection_authority.get("laneCount"), 2),
        "authority_evidence_coverage": (authority_evidence_projection_authority.get("requiredAuthorityCoverage"), "100%"),
        "authority_evidence_blockers": (authority_evidence_projection_authority.get("blockers"), 0),
        "authority_evidence_drift": (authority_evidence_projection_authority.get("repoDriftStable"), True),
        "authority_evidence_gate_run": (authority_evidence_projection_authority.get("mutationGateRunId"), AUTHORITY_EVIDENCE_GATE_RUN),
        "authority_evidence_gate_artifact": (authority_evidence_projection_authority.get("mutationGateArtifactId"), AUTHORITY_EVIDENCE_GATE_ARTIFACT),
        "authority_evidence_gate_artifact_digest": (authority_evidence_projection_authority.get("mutationGateArtifactDigest"), AUTHORITY_EVIDENCE_GATE_ARTIFACT_DIGEST),
        "authority_evidence_evidence_run": (authority_evidence_projection_authority.get("evidenceRunId"), AUTHORITY_EVIDENCE_RUN),
        "authority_evidence_evidence_artifact": (authority_evidence_projection_authority.get("evidenceArtifactId"), AUTHORITY_EVIDENCE_ARTIFACT),
        "authority_evidence_evidence_artifact_digest": (authority_evidence_projection_authority.get("evidenceArtifactDigest"), AUTHORITY_EVIDENCE_ARTIFACT_DIGEST),
    }
    for name, (actual, expected) in p3_authority_exact.items():
        check(name, actual == expected, f"actual={actual} expected={expected}")

    p3_boundaries = [
        "authorization for the Cloud projection to mutate repository source",
        "production readiness",
        "hosted multi-tenant execution",
        "enterprise IAM or security readiness",
        "human usefulness",
        "independent-agent verification",
    ]

    authority_packs = cp.get("authorityPacks", {})
    check("authority_packs_state", authority_packs.get("status") == AUTHORITY_EVIDENCE_CONNECTED_STATUS, str(authority_packs.get("status")))
    pack_rows = authority_packs.get("items")
    check("authority_pack_rows_exactly_one", isinstance(pack_rows, list) and len(pack_rows) == 1, f"count={len(pack_rows) if isinstance(pack_rows, list) else 'invalid'}")
    if isinstance(pack_rows, list) and len(pack_rows) == 1 and isinstance(pack_rows[0], dict):
        row = pack_rows[0]
        provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
        exact = {
            "authority_pack_id": (row.get("Pack"), AUTHORITY_PACK_ID),
            "authority_pack_repository": (row.get("Repository"), generated_from.get("repository")),
            "authority_pack_reference_state": (row.get("ReferenceState"), "SOURCE_VERIFIED_REFERENCE"),
            "authority_pack_schema": (row.get("packSchemaVersion"), "code_atlas_agent_authority_pack.v1"),
            "authority_pack_checksum": (row.get("packChecksum"), AUTHORITY_PACK_CHECKSUM),
            "authority_pack_preparation_decision": (row.get("preparationDecision"), "PASS"),
            "authority_pack_head": (provenance.get("repoHead"), AUTHORITY_EVIDENCE_HEAD),
            "authority_pack_tree": (provenance.get("repoTree"), AUTHORITY_EVIDENCE_TREE),
            "authority_pack_repository_identity": (provenance.get("repositoryIdentity"), AUTHORITY_EVIDENCE_REPOSITORY_IDENTITY),
            "authority_pack_request_digest": (provenance.get("requestDigest"), AUTHORITY_PACK_REQUEST_DIGEST),
            "authority_pack_authority_lock": (provenance.get("authorityDigest"), AUTHORITY_LOCK_DIGEST),
            "authority_pack_evidence_lock": (provenance.get("evidenceDigest"), EVIDENCE_LOCK_DIGEST),
            "authority_pack_policy_lock": (provenance.get("policyDigest"), None),
            "authority_pack_read_only": (row.get("readOnly"), True),
            "authority_pack_reference_only": (row.get("referenceOnly"), True),
            "authority_pack_not_production": (row.get("productionCertified"), False),
            "authority_pack_not_certifiable": (row.get("certifiable"), False),
        }
        for name, (actual, expected) in exact.items():
            check(name, actual == expected, f"actual={actual} expected={expected}")
        pack_dnp = row.get("doesNotProve") if isinstance(row.get("doesNotProve"), list) else []
        for boundary in p3_boundaries:
            check(f"authority_pack_does_not_prove:{boundary}", boundary in pack_dnp, str(pack_dnp))
        check("authority_pack_forbidden_fields_absent", not forbidden_repository_fields(row), str(forbidden_repository_fields(row)))
    pack_rule = str(authority_packs.get("projectionRule", ""))
    check("authority_pack_projection_rule_reference_only", "Reference only" in pack_rule and "neither generates" in pack_rule and "mutation authority" in pack_rule, pack_rule)

    evidence_refs = cp.get("evidenceReferences", {})
    check("evidence_refs_state", evidence_refs.get("status") == AUTHORITY_EVIDENCE_CONNECTED_STATUS, str(evidence_refs.get("status")))
    evidence_rows = evidence_refs.get("items")
    check("evidence_rows_exactly_one", isinstance(evidence_rows, list) and len(evidence_rows) == 1, f"count={len(evidence_rows) if isinstance(evidence_rows, list) else 'invalid'}")
    if isinstance(evidence_rows, list) and len(evidence_rows) == 1 and isinstance(evidence_rows[0], dict):
        row = evidence_rows[0]
        provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
        exact = {
            "evidence_repository": (row.get("Repository"), generated_from.get("repository")),
            "evidence_reference_state": (row.get("ReferenceState"), "SOURCE_VERIFIED_REFERENCE"),
            "evidence_verification_schema": (row.get("verificationSchemaVersion"), "code_atlas_change_verification.v1"),
            "evidence_verification_decision": (row.get("verificationDecision"), "PASS"),
            "evidence_report_digest": (row.get("verificationReportDigest"), VERIFICATION_REPORT_DIGEST),
            "evidence_bundle_schema": (row.get("bundleSchemaVersion"), "code_atlas_portable_evidence_bundle.v1"),
            "evidence_bundle_digest": (row.get("bundleManifestDigest"), EVIDENCE_BUNDLE_MANIFEST_DIGEST),
            "evidence_pack_id": (row.get("packId"), AUTHORITY_PACK_ID),
            "evidence_pack_checksum": (row.get("packChecksum"), AUTHORITY_PACK_CHECKSUM),
            "evidence_head": (provenance.get("repoHead"), AUTHORITY_EVIDENCE_HEAD),
            "evidence_tree": (provenance.get("repoTree"), AUTHORITY_EVIDENCE_TREE),
            "evidence_repository_identity": (provenance.get("repositoryIdentity"), AUTHORITY_EVIDENCE_REPOSITORY_IDENTITY),
            "evidence_request_digest": (provenance.get("requestDigest"), AUTHORITY_PACK_REQUEST_DIGEST),
            "evidence_workflow_run": (provenance.get("workflowRunId"), AUTHORITY_EVIDENCE_RUN),
            "evidence_artifact": (provenance.get("artifactId"), AUTHORITY_EVIDENCE_ARTIFACT),
            "evidence_artifact_digest": (provenance.get("artifactDigest"), AUTHORITY_EVIDENCE_ARTIFACT_DIGEST),
            "evidence_read_only": (row.get("readOnly"), True),
            "evidence_reference_only": (row.get("referenceOnly"), True),
            "evidence_not_production": (row.get("productionCertified"), False),
            "evidence_not_certifiable": (row.get("certifiable"), False),
        }
        for name, (actual, expected) in exact.items():
            check(name, actual == expected, f"actual={actual} expected={expected}")
        evidence_dnp = row.get("doesNotProve") if isinstance(row.get("doesNotProve"), list) else []
        for boundary in p3_boundaries:
            check(f"evidence_does_not_prove:{boundary}", boundary in evidence_dnp, str(evidence_dnp))
        check("evidence_forbidden_fields_absent", not forbidden_repository_fields(row), str(forbidden_repository_fields(row)))
    evidence_rule = str(evidence_refs.get("projectionRule", ""))
    check("evidence_projection_rule_bounded_pass", "PASS is preserved" in evidence_rule and "not promoted" in evidence_rule and "mutation authority" in evidence_rule, evidence_rule)


    p4_authority_exact = {
        "entitlement_authority_head": (entitlement_projection_authority.get("baseHead"), ENTITLEMENT_HEAD),
        "entitlement_authority_tree": (entitlement_projection_authority.get("baseTree"), ENTITLEMENT_TREE),
        "entitlement_authority_profile": (entitlement_projection_authority.get("profile"), ENTITLEMENT_PROFILE),
        "entitlement_authority_run": (entitlement_projection_authority.get("authorityRunId"), ENTITLEMENT_AUTHORITY_RUN),
        "entitlement_authority_artifact": (entitlement_projection_authority.get("authorityArtifactId"), ENTITLEMENT_AUTHORITY_ARTIFACT),
        "entitlement_authority_artifact_digest": (entitlement_projection_authority.get("authorityArtifactDigest"), ENTITLEMENT_AUTHORITY_ARTIFACT_DIGEST),
        "entitlement_composed_sha256": (entitlement_projection_authority.get("composedArtifactSha256"), ENTITLEMENT_COMPOSED_SHA256),
        "entitlement_authority_request_digest": (entitlement_projection_authority.get("authorityRequestDigest"), ENTITLEMENT_AUTHORITY_REQUEST_DIGEST),
        "entitlement_authority_result": (entitlement_projection_authority.get("authorityResult"), "PASS_COMPOSED_AUTHORITY_MESH"),
        "entitlement_authority_lanes": (entitlement_projection_authority.get("laneCount"), 2),
        "entitlement_authority_coverage": (entitlement_projection_authority.get("requiredAuthorityCoverage"), "100%"),
        "entitlement_authority_blockers": (entitlement_projection_authority.get("blockers"), 0),
        "entitlement_authority_drift": (entitlement_projection_authority.get("repoDriftStable"), True),
        "entitlement_gate_run": (entitlement_projection_authority.get("mutationGateRunId"), ENTITLEMENT_GATE_RUN),
        "entitlement_gate_artifact": (entitlement_projection_authority.get("mutationGateArtifactId"), ENTITLEMENT_GATE_ARTIFACT),
        "entitlement_gate_artifact_digest": (entitlement_projection_authority.get("mutationGateArtifactDigest"), ENTITLEMENT_GATE_ARTIFACT_DIGEST),
    }
    for name, (actual, expected) in p4_authority_exact.items():
        check(name, actual == expected, f"actual={actual} expected={expected}")

    entitlements = cp.get("usageEntitlements", {})
    source_owner = entitlements.get("sourceOwner") if isinstance(entitlements.get("sourceOwner"), dict) else {}
    entitlement_exact = {
        "entitlement_state": (entitlements.get("status"), ENTITLEMENT_CONNECTED_STATUS),
        "entitlement_product": (entitlements.get("requestedProduct"), "PRISMA Change Assurance"),
        "entitlement_source_path": (source_owner.get("path"), ENTITLEMENT_SOURCE_PATH),
        "entitlement_source_blob": (source_owner.get("sourceBlobSha"), ENTITLEMENT_SOURCE_BLOB),
        "entitlement_source_catalog": (source_owner.get("catalog"), "PLAN_BASED_PROVISIONING_CATALOG"),
        "entitlement_reuse_mode": (source_owner.get("reuseMode"), "REFERENCE_ONLY"),
        "entitlement_source_dnr": (source_owner.get("doNotRebuild"), True),
        "entitlement_plan_features": (entitlements.get("planFeaturesAtCapture"), ENTITLEMENT_PLAN_FEATURES),
        "entitlement_catalog_matches": (entitlements.get("catalogMatches"), []),
        "entitlement_grant_status": (entitlements.get("grantStatus"), "NOT_PRESENT_IN_CANONICAL_PLAN_FEATURES"),
        "entitlement_live_enforcement_absent": (entitlements.get("liveEnforcementObserved"), False),
        "entitlement_no_license_mutation": (entitlements.get("licenseMutationPerformed"), False),
        "entitlement_read_only": (entitlements.get("readOnly"), True),
        "entitlement_not_production": (entitlements.get("productionCertified"), False),
        "entitlement_not_certifiable": (entitlements.get("certifiable"), False),
    }
    for name, (actual, expected) in entitlement_exact.items():
        check(name, actual == expected, f"actual={actual} expected={expected}")
    source_capabilities = source_owner.get("capabilityIds") if isinstance(source_owner.get("capabilityIds"), list) else []
    check("entitlement_source_capabilities", source_capabilities == ["licensing.source_contract_alignment", "licensing.customer_setup.plan_based_onboarding"], str(source_capabilities))
    entitlement_dnp = entitlements.get("doesNotProve") if isinstance(entitlements.get("doesNotProve"), list) else []
    for boundary in ("entitlement grant", "live license enforcement", "billing authorization", "production readiness"):
        check(f"entitlement_does_not_prove:{boundary}", boundary in entitlement_dnp, str(entitlement_dnp))
    entitlement_rule = str(entitlements.get("projectionRule", ""))
    entitlement_next = str(entitlements.get("nextGate", ""))
    check("entitlement_projection_fail_closed", "fail-closed" in entitlement_rule and "NOT_PRESENT_IN_CANONICAL_PLAN_FEATURES" in entitlement_rule and "does not create or grant" in entitlement_rule, entitlement_rule)
    check("entitlement_next_gate_separate_decision", "separately governed" in entitlement_next and "Change Assurance feature" in entitlement_next and "NOT_GRANTED" in entitlement_next, entitlement_next)

    links = re.findall(r'<a\b(?=[^>]*data-ci-entry=["\']v1["\'])(?=[^>]*href=["\']/internal/web/change_intelligence_center\.html["\'])[^>]*>', main_html, re.I)
    check("single_navigation_seam", len(links) == 1, f"found={len(links)}")
    check("main_js_uncoupled", "change_intelligence_center" not in main_js and "pci-" not in main_js)
    check("main_css_uncoupled", "change_intelligence_center" not in main_css and "pci-" not in main_css)
    check("ci_html_namespace", 'class="pci-surface"' in ci_html)
    check("ci_html_style_module", "change_intelligence_center_style.js" in ci_html)
    check("ci_html_projection_module", "change_intelligence_center.js" in ci_html)
    check("ci_html_no_css_link", "change_intelligence_center.css" not in ci_html)
    check("visual_no_important", "!important" not in ci_style)
    check("visual_no_cc_selector", re.search(r"\.cc[-_a-zA-Z0-9]", ci_style) is None)
    check("visual_reduced_motion", "prefers-reduced-motion" in ci_style)
    check("visual_reduced_transparency", "prefers-reduced-transparency" in ci_style)
    check("visual_focus", ":focus-visible" in ci_style)
    check("visual_scoped_injection", 'style.dataset.pciStyle = "v1"' in ci_style and "document.head.appendChild(style)" in ci_style)
    check("js_read_only_http", re.search(r"method\s*:\s*[\"'](?:POST|PUT|PATCH|DELETE)[\"']", ci_js, re.I) is None)
    check("js_no_browser_persistence", "localStorage" not in ci_js and "sessionStorage" not in ci_js)
    check("js_governed_config", CONFIG_PATH_LITERAL in ci_js)
    check("js_fail_closed", "BLOCKED_CONFIG_UNAVAILABLE" in ci_js and "NOT_CONNECTED" in ci_js)

    for term in ("REUSE_AS_IS", "SHARED_OWNER", "ADAPT", "DO_NOT_TOUCH", "NEW_OWNER", "Layer Map", "No-fake-green", "Commercial Billing Authority"):
        check(f"contract_term:{term}", term in contract, term)

    check("runtime_chromium", "chromium" in runtime_js and "playwright" in runtime_js)
    check("runtime_desktop_mobile", "desktop" in runtime_js and "mobile" in runtime_js)
    check("runtime_all_views", all(view in runtime_js for view in ("overview", "repositories", "runs", "discover", "guard", "control", "authority", "evidence", "roi", "entitlements")))
    check("runtime_fail_closed_semantics", "UNKNOWN|NOT_CONNECTED|BLOCKED" in runtime_js)
    check("runtime_screenshots", "page.screenshot" in runtime_js)
    check("workflow_source_gate", "verify-cloud-center-change-intelligence-01.py" in workflow)
    check("workflow_runtime_gate", "verify-cloud-center-change-intelligence-runtime-01.mjs" in workflow)
    check("workflow_browser_install", "playwright install --with-deps chromium" in workflow)
    check("workflow_evidence_upload", "change-intelligence-cloud-runtime-evidence" in workflow)

    diff_evaluated = False
    diff_base, diff_base_source = resolve_diff_base(root)
    if diff_base:
        diff_evaluated = True
        code, output = git(root, "diff", "--name-only", f"{diff_base}...HEAD")
        if code != 0:
            check("git_diff_boundary", False, f"base={diff_base} source={diff_base_source} error={output}")
        else:
            changed = {x.strip().replace("\\", "/") for x in output.splitlines() if x.strip()}
            check("git_diff_non_empty", bool(changed), f"base={diff_base} source={diff_base_source} changed={len(changed)}")
            check("git_diff_boundary", not (changed - ALLOWED_DIFF), f"base={diff_base} source={diff_base_source} changed={len(changed)} outside={sorted(changed - ALLOWED_DIFF)}")
            check("git_diff_canonical_cloud_center_read_only", not (changed & CANONICAL_CLOUD_CENTER_READ_ONLY), f"canonicalChanged={sorted(changed & CANONICAL_CLOUD_CENTER_READ_ONLY)}")
            check("git_diff_no_css", not any(x.lower().endswith(".css") for x in changed), "Commercial Billing Authority no-CSS boundary")
    else:
        check("git_diff_boundary", False, "CURRENT_PR_BASE_UNAVAILABLE")

    return emit(checks, errors, warnings, diff_evaluated)


def emit(checks, errors, warnings, diff_evaluated):
    result = {
        "schemaVersion": "prisma.change_intelligence.cloud_center.verify.v1",
        "baseHead": BASE_HEAD,
        "result": "PASS_CHANGE_INTELLIGENCE_CLOUD_CENTER_SOURCE" if not errors else "FAIL_CHANGE_INTELLIGENCE_CLOUD_CENTER_SOURCE",
        "sourceReady": not errors,
        "runtimeVerified": False,
        "productionCertified": False,
        "certifiable": False,
        "diffBoundaryEvaluated": diff_evaluated,
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
