#!/usr/bin/env python3
"""Fail-closed source verifier for PRISMA Change Intelligence Cloud Center V1."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

BASE_HEAD = "d14effee1a1223cc772247ea9d7ec8547dc15c78"
CONFIG_PATH_LITERAL = "/internal/config/change_intelligence_cloud.json"

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


def repo_root() -> Path:
    for candidate in (Path.cwd().resolve(), *Path.cwd().resolve().parents):
        if (candidate / ".git").exists() and (candidate / "apps").exists():
            return candidate
    raise RuntimeError("REPO_ROOT_NOT_FOUND")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(root: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, encoding="utf-8", errors="replace", check=False)
    return p.returncode, p.stdout.strip()


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
        o = owners.get(oid, {})
        check(f"shared_owner:{oid}", o.get("reuseMode") == mode and o.get("doNotRebuild") is True,
              f"reuse={o.get('reuseMode')} doNotRebuild={o.get('doNotRebuild')}")

    cp = cfg.get("controlPlane", {})
    for key in ("repositories", "analysisRuns", "authorityPacks", "evidenceReferences"):
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
    check("runtime_all_views", all(view in runtime_js for view in ("overview","repositories","runs","discover","guard","control","authority","evidence","roi","entitlements")))
    check("runtime_fail_closed_semantics", "UNKNOWN|NOT_CONNECTED|BLOCKED" in runtime_js)
    check("runtime_screenshots", "page.screenshot" in runtime_js)
    check("workflow_source_gate", "verify-cloud-center-change-intelligence-01.py" in workflow)
    check("workflow_runtime_gate", "verify-cloud-center-change-intelligence-runtime-01.mjs" in workflow)
    check("workflow_browser_install", "playwright install --with-deps chromium" in workflow)
    check("workflow_evidence_upload", "change-intelligence-cloud-runtime-evidence" in workflow)

    diff_evaluated = False
    code, _ = git(root, "cat-file", "-e", f"{BASE_HEAD}^{{commit}}")
    if code == 0:
        diff_evaluated = True
        code, output = git(root, "diff", "--name-only", f"{BASE_HEAD}...HEAD")
        if code != 0:
            check("git_diff_boundary", False, output)
        else:
            changed = {x.strip().replace("\\", "/") for x in output.splitlines() if x.strip()}
            check("git_diff_boundary", not (changed - ALLOWED_DIFF), f"changed={len(changed)} outside={sorted(changed - ALLOWED_DIFF)}")
            check("git_diff_expected_files", not (ALLOWED_DIFF - changed), f"missing={sorted(ALLOWED_DIFF - changed)}")
            check("git_diff_no_css", not any(x.lower().endswith(".css") for x in changed), "Commercial Billing Authority no-CSS boundary")
    else:
        warnings.append(f"DIFF_BOUNDARY_NOT_EVALUATED: base {BASE_HEAD} unavailable")

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
