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

    for key in ("authorityPacks", "evidenceReferences"):
        check(f"unbound_is_explicit:{key}", cp.get(key, {}).get("status") == "NOT_CONNECTED", str(cp.get(key, {}).get("status")))

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
