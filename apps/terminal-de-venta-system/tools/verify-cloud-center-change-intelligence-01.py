#!/usr/bin/env python3
"""Fail-closed source verifier for PRISMA Change Intelligence Cloud Center V1.

This verifier is intentionally static. It does not start servers, touch ports,
mutate databases, run Prisma generation, call Cloudflare, or certify runtime.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

BASE_HEAD = "d14effee1a1223cc772247ea9d7ec8547dc15c78"
ROOT_MARKERS = (".git", "package.json", "pnpm-workspace.yaml")

REL = {
    "main_html": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.html"),
    "main_js": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.js"),
    "main_css": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/cloud_command_center.css"),
    "ci_html": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/change_intelligence_center.html"),
    "ci_css": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/change_intelligence_center.css"),
    "ci_js": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/web/change_intelligence_center.js"),
    "ci_config": Path("apps/terminal-de-venta-system/Prisma Cloud Ctr/internal/config/change_intelligence_cloud.json"),
    "contract": Path("apps/terminal-de-venta-system/docs/productization/PRISMA_CHANGE_INTELLIGENCE_CLOUD_CENTER_VERTICAL_CONTRACT.md"),
    "verifier": Path("apps/terminal-de-venta-system/tools/verify-cloud-center-change-intelligence-01.py"),
}

ALLOWED_DIFF = {
    REL["main_html"].as_posix(),
    REL["ci_html"].as_posix(),
    REL["ci_css"].as_posix(),
    REL["ci_js"].as_posix(),
    REL["ci_config"].as_posix(),
    REL["contract"].as_posix(),
    REL["verifier"].as_posix(),
}


def find_repo_root() -> Path:
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if any((candidate / marker).exists() for marker in ROOT_MARKERS):
            if (candidate / "apps").exists() and (candidate / "tools").exists():
                return candidate
    script = Path(__file__).resolve()
    for candidate in script.parents:
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("REPO_ROOT_NOT_FOUND")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(root: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.returncode, proc.stdout.strip()


def main() -> int:
    root = find_repo_root()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})
        if not condition:
            errors.append(f"{name}: {detail}")

    paths = {key: root / rel for key, rel in REL.items()}
    for key, path in paths.items():
        check(f"file_exists:{key}", path.exists(), str(REL[key]))

    if errors:
        return emit(root, checks, errors, warnings, diff_evaluated=False)

    main_html = read_text(paths["main_html"])
    main_js = read_text(paths["main_js"])
    main_css = read_text(paths["main_css"])
    ci_html = read_text(paths["ci_html"])
    ci_css = read_text(paths["ci_css"])
    ci_js = read_text(paths["ci_js"])
    contract_md = read_text(paths["contract"])

    try:
        cfg = json.loads(read_text(paths["ci_config"]))
        config_ok = True
    except Exception as exc:  # pragma: no cover - fail closed
        cfg = {}
        config_ok = False
        errors.append(f"config_json_parse: {exc}")
    checks.append({"name": "config_json_parse", "pass": config_ok, "detail": "change_intelligence_cloud.json"})

    if config_ok:
        mesh = cfg.get("generatedFrom", {}).get("authorityMesh", {})
        maturity = cfg.get("maturity", {})
        safety = cfg.get("safety", {})
        check("config_schema", cfg.get("schemaVersion") == "prisma.change_intelligence.cloud_center.vertical.v1", str(cfg.get("schemaVersion")))
        check("authority_base", cfg.get("generatedFrom", {}).get("baseHead") == BASE_HEAD, str(cfg.get("generatedFrom", {}).get("baseHead")))
        check("authority_mesh_run", mesh.get("runId") == 32156981312, str(mesh.get("runId")))
        check("authority_mesh_artifact", mesh.get("artifactId") == 9332162633, str(mesh.get("artifactId")))
        check("authority_layer_map", mesh.get("layerMapPresent") is True, str(mesh.get("layerMapPresent")))
        check("authority_coverage", mesh.get("requiredAuthorityCoverage") == "100%", str(mesh.get("requiredAuthorityCoverage")))
        check("maturity_local_verified", maturity.get("engineStatus") == "LOCAL_VERIFIED", str(maturity.get("engineStatus")))
        check("no_certifiable_claim", maturity.get("certifiable") is False, str(maturity.get("certifiable")))
        check("no_production_certified_claim", maturity.get("productionCertified") is False, str(maturity.get("productionCertified")))
        check("no_paid_pilot_claim", maturity.get("paidPilotReady") == "NOT_CERTIFIED_BY_CURRENT_EVIDENCE", str(maturity.get("paidPilotReady")))
        check("human_usefulness_not_measured", maturity.get("humanUsefulness") == "NOT_MEASURED", str(maturity.get("humanUsefulness")))
        check("independent_evaluator_blocked", maturity.get("independentEvaluator") == "BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR", str(maturity.get("independentEvaluator")))
        check("read_only_default", safety.get("readOnlyDefault") is True, str(safety.get("readOnlyDefault")))
        check("source_egress_default_false", safety.get("sourceCodeEgressDefault") is False, str(safety.get("sourceCodeEgressDefault")))
        check("no_fake_green", safety.get("noFakeGreen") is True, str(safety.get("noFakeGreen")))
        check("no_process_port_mutation", safety.get("noProcessOrPortMutation") is True, str(safety.get("noProcessOrPortMutation")))

        owners = {item.get("id"): item for item in cfg.get("sharedOwners", [])}
        required_owners = {
            "customer-registration": "REUSE_AS_IS",
            "licensing-contract-alignment": "SHARED_OWNER",
            "commercial-billing": "SHARED_OWNER",
            "private-repository-rental": "ADAPT",
            "change-intelligence-engine": "REUSE_AS_IS",
        }
        for owner_id, reuse_mode in required_owners.items():
            owner = owners.get(owner_id, {})
            check(f"shared_owner:{owner_id}", owner.get("reuseMode") == reuse_mode and owner.get("doNotRebuild") is True, f"reuse={owner.get('reuseMode')} doNotRebuild={owner.get('doNotRebuild')}")

        cp = cfg.get("controlPlane", {})
        for key in ("repositories", "analysisRuns", "authorityPacks", "evidenceReferences"):
            check(f"unbound_is_explicit:{key}", cp.get(key, {}).get("status") == "NOT_CONNECTED", str(cp.get(key, {}).get("status")))

    link_pattern = re.compile(
        r'<a\b(?=[^>]*\bdata-ci-entry=["\']v1["\'])(?=[^>]*\bhref=["\']/internal/web/change_intelligence_center\.html["\'])[^>]*>',
        re.IGNORECASE,
    )
    links = link_pattern.findall(main_html)
    check("single_navigation_seam", len(links) == 1, f"found={len(links)}")
    check("main_js_uncoupled", "change_intelligence_center" not in main_js and "pci-" not in main_js, "existing cloud_command_center.js has no CI coupling")
    check("main_css_uncoupled", "change_intelligence_center" not in main_css and "pci-" not in main_css, "existing cloud_command_center.css has no CI coupling")

    check("ci_html_body_namespace", 'class="pci-surface"' in ci_html, "body.pci-surface")
    check("ci_html_config_indirect", "change_intelligence_center.js" in ci_html and "change_intelligence_center.css" in ci_html, "dedicated JS/CSS refs")
    check("ci_html_back_link", 'href="/"' in ci_html and "Prisma Cloud Center" in ci_html, "back navigation")

    check("css_no_important", "!important" not in ci_css, "no !important")
    check("css_no_cc_selector", re.search(r"(^|[,{\s])\.cc[-_a-zA-Z0-9]", ci_css) is None, "no .cc-* selector")
    wildcard_selector = re.search(r"(^|\})([^@{}]*\*)\s*\{", ci_css, re.MULTILINE)
    check("css_no_wildcard_selector", wildcard_selector is None, "no wildcard CSS selector")
    check("css_reduced_motion", "prefers-reduced-motion" in ci_css, "reduced-motion contract")
    check("css_reduced_transparency", "prefers-reduced-transparency" in ci_css, "reduced-transparency contract")
    check("css_focus_visible", ":focus-visible" in ci_css, "keyboard focus contract")

    mutating_fetch = re.search(r"method\s*:\s*[\"'](?:POST|PUT|PATCH|DELETE)[\"']", ci_js, re.IGNORECASE)
    check("js_read_only_http", mutating_fetch is None, "no mutating HTTP method")
    check("js_no_storage_secret", "localStorage" not in ci_js and "sessionStorage" not in ci_js, "no browser persistence")
    check("js_no_secret_prompt", re.search(r"admin.?token|password|private.?key|bearer", ci_js, re.IGNORECASE) is None, "no secret collection vocabulary")
    check("js_loads_governed_config", CONFIG_PATH_LITERAL in ci_js, CONFIG_PATH_LITERAL)
    check("js_fail_closed_config", "BLOCKED_CONFIG_UNAVAILABLE" in ci_js, "explicit blocked config state")
    check("js_not_connected_semantics", "NOT_CONNECTED" in ci_js, "explicit disconnected state")

    required_contract_terms = [
        "REUSE_AS_IS",
        "SHARED_OWNER",
        "ADAPT",
        "DO_NOT_TOUCH",
        "NEW_OWNER",
        "Layer Map",
        "No-fake-green",
        "source-ready vertical shell only",
    ]
    for term in required_contract_terms:
        check(f"contract_term:{term}", term in contract_md, term)

    diff_evaluated = False
    code, _ = git(root, "cat-file", "-e", f"{BASE_HEAD}^{{commit}}")
    if code == 0:
        diff_evaluated = True
        code, output = git(root, "diff", "--name-only", f"{BASE_HEAD}...HEAD")
        if code != 0:
            errors.append(f"git_diff_failed: {output}")
            checks.append({"name": "git_diff_boundary", "pass": False, "detail": output})
        else:
            changed = {line.strip().replace("\\", "/") for line in output.splitlines() if line.strip()}
            outside = sorted(changed - ALLOWED_DIFF)
            missing_expected = sorted({REL["main_html"].as_posix(), REL["ci_html"].as_posix(), REL["ci_css"].as_posix(), REL["ci_js"].as_posix(), REL["ci_config"].as_posix(), REL["contract"].as_posix(), REL["verifier"].as_posix()} - changed)
            check("git_diff_boundary", not outside, f"changed={len(changed)} outside={outside}")
            check("git_diff_expected_files", not missing_expected, f"missing={missing_expected}")
    else:
        warnings.append(f"DIFF_BOUNDARY_NOT_EVALUATED: base {BASE_HEAD} not present in local Git object database")
        checks.append({"name": "git_diff_boundary", "pass": None, "detail": "NOT_EVALUATED_BASE_UNAVAILABLE"})

    return emit(root, checks, errors, warnings, diff_evaluated=diff_evaluated)


CONFIG_PATH_LITERAL = "/internal/config/change_intelligence_cloud.json"


def emit(root: Path, checks: list[dict[str, Any]], errors: list[str], warnings: list[str], *, diff_evaluated: bool) -> int:
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
