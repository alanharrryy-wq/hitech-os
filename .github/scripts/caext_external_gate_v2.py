from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import traceback
import zipfile
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from code_atlas.change_intelligence import prepare_change, verify_prepared_change
from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context
from code_atlas.intelligence.repository import discover_repository

PIN = os.environ.get("CAEXT_CODE_ATLAS_PIN", "bcc617d969fd033697d024ec56a72bd02f0ba27b")
WORKERS = max(1, min(18, int(os.environ.get("CAEXT_WORKERS", "18"))))
NEUTRAL_PROFILES = {"", "neutral", "neutral/default", "default"}
LEAK_TERMS = (
    "PRISMA", "hitech-os", "terminal-de-venta-system", "Factory Ledger", "Authority Mesh",
    "AutoMesh", "NDC", "Tablet", "PC", "Mobile", "Chart Lab", "F:\\", "PRISMA_CTX",
)
TEXT_SCAN_LIMIT = 2_500_000


@dataclass(frozen=True)
class RepoSpec:
    repo_id: str
    slug: str
    url: str
    sha: str
    tree: str
    stack: str
    target: str
    other: str
    request: str
    historical_commit: str | None = None
    historical_paths: tuple[str, ...] = ()


REGRESSION_SPECS = (
    RepoSpec(
        "A", "pallets/click", "https://github.com/pallets/click.git",
        "8b44edfff7d9a6c895fa804148c16b3a0bc9efb5", "a52cd0994280efa88a13aa9af244c4b809b89b13",
        "Python library / CLI", "src/click/_termui_impl.py", "tests/test_termui.py",
        "Fix Windows temporary pager text handling without touching parser core or packaging.",
        "8b44edfff7d9a6c895fa804148c16b3a0bc9efb5",
        ("CHANGES.md", "src/click/_termui_impl.py", "tests/test_termui.py"),
    ),
    RepoSpec(
        "B", "vitejs/vite", "https://github.com/vitejs/vite.git",
        "dcf88bd2ad2b1a8845f9029587cc8c825e382d42", "d2deca5bf3ec6b42068290ba4f97b52d93eb8b9d",
        "TypeScript / Node monorepo", "packages/vite/src/node/plugins/define.ts",
        "packages/vite/src/node/__tests__/plugins/define.spec.ts",
        "Fix define-key matching for $-prefixed keys without touching unrelated build pipeline behavior.",
        "dcf88bd2ad2b1a8845f9029587cc8c825e382d42",
        ("packages/vite/src/node/plugins/define.ts", "packages/vite/src/node/__tests__/plugins/define.spec.ts"),
    ),
    RepoSpec(
        "C", "BurntSushi/ripgrep", "https://github.com/BurntSushi/ripgrep.git",
        "3fce3b5bb0236da2df6d99672afb8a719642eca7", "856ed9162d23416ee7dc5f4389975b54ca062f60",
        "Rust CLI / workspace", "crates/ignore/src/gitignore.rs", "crates/ignore/src/types.rs",
        "Increase ignore matcher pool capacity without changing unrelated search behavior or release metadata.",
        "020687a77d13146923333f0beb274eeabd54a270",
        ("Cargo.lock", "crates/globset/Cargo.toml", "crates/ignore/Cargo.toml", "crates/ignore/src/gitignore.rs", "crates/ignore/src/types.rs"),
    ),
)

# Populated only after the three-repository regression gate is green.
DIVERSITY_SPECS: tuple[RepoSpec, ...] = ()


def iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def jdump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def sh(cmd: list[str], *, cwd: Path | None = None, check: bool = True, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, check=False, text=True, encoding="utf-8", errors="replace",
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
    )
    if check and proc.returncode:
        raise RuntimeError(f"COMMAND_FAILED[{proc.returncode}] {' '.join(cmd)}\n{proc.stderr[-4000:]}")
    return proc


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return sh(["git", "-C", str(repo), *args], check=check)


def git_text(repo: Path, *args: str) -> str | None:
    proc = git(repo, *args, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else None


def identity(repo: Path) -> dict[str, Any]:
    status = git_text(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return {
        "head": git_text(repo, "rev-parse", "HEAD"),
        "tree": git_text(repo, "rev-parse", "HEAD^{tree}"),
        "dirty": bool(status) if status is not None else None,
        "status": status or "",
    }


def clone_pinned(spec: RepoSpec, root: Path) -> Path:
    dest = root / f"repo_{spec.repo_id}"
    sh(["git", "init", str(dest)])
    git(dest, "remote", "add", "origin", spec.url)
    git(dest, "fetch", "--depth=1", "--no-tags", "origin", spec.sha)
    git(dest, "checkout", "--detach", "FETCH_HEAD")
    ident = identity(dest)
    if ident["head"] != spec.sha or ident["tree"] != spec.tree or ident["dirty"]:
        raise RuntimeError(f"PIN_MISMATCH:{spec.slug}:{ident}")
    return dest


def worktree(base: Path, root: Path, label: str) -> Path:
    dest = root / "worktrees" / label
    dest.parent.mkdir(parents=True, exist_ok=True)
    git(base, "worktree", "add", "--detach", "--force", str(dest), "HEAD")
    return dest


def remove_worktree(base: Path, dest: Path) -> None:
    git(base, "worktree", "remove", "--force", str(dest), check=False)
    shutil.rmtree(dest, ignore_errors=True)


def mutate(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    suffix = path.suffix.lower()
    marker = "\n# caext-v2 fixture\n" if suffix in {".py", ".sh", ".yml", ".yaml"} else (
        "\n<!-- caext-v2 fixture -->\n" if suffix in {".md", ".html"} else "\n// caext-v2 fixture\n"
    )
    with path.open("a", encoding="utf-8", errors="replace") as handle:
        handle.write(marker)


def policy(repo_id: str, protected: str | None, *, strict: bool = False, authority: str | None = None) -> dict[str, Any]:
    return {
        "schemaVersion": "code_atlas_customer_policy.v1",
        "policyId": f"caext-v2-{repo_id}-{'strict' if strict else 'base'}",
        "version": "2",
        "protectedPaths": [protected] if protected else [],
        "requiredAuthorities": [authority] if authority else [],
        "requiredTests": ["caext.required.check"] if strict else [],
        "requiredReviews": [],
        "forbiddenOperations": ["push", "deploy", "database-mutation", "dependency-install", "process-kill", "port-change"],
        "domainEvidenceRequirements": ["caext.required.evidence"] if strict else [],
        "impactThresholds": {},
    }


def token_pattern(term: str) -> re.Pattern[str]:
    if term == "F:\\":
        return re.compile(r"(?i)(?<![A-Za-z0-9_])F:\\")
    return re.compile(rf"(?i)(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])")


def boundary_occurrences(text: str, term: str) -> list[tuple[int, int]]:
    return [match.span() for match in token_pattern(term).finditer(text)]


def walk_strings(value: Any, path: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{index}]")


def source_terms(repo: Path, inventory_paths: Iterable[str]) -> set[str]:
    found: set[str] = set()
    patterns = {term: token_pattern(term) for term in LEAK_TERMS}
    for rel in inventory_paths:
        for term, pattern in patterns.items():
            if pattern.search(rel):
                found.add(term)
        path = repo / rel
        try:
            if not path.is_file() or path.is_symlink() or path.stat().st_size > TEXT_SCAN_LIMIT:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for term, pattern in patterns.items():
            if term not in found and pattern.search(text):
                found.add(term)
        if len(found) == len(patterns):
            break
    return found


def classify_occurrence(*, term: str, json_path: str, artifact_name: str, source_derived: bool,
                        profile_name: str = "neutral/default", profile_terms: Iterable[str] = ()) -> str:
    if "histor" in artifact_name.lower() or "histor" in json_path.lower():
        return "HISTORICAL_TOOL_EVIDENCE"
    profile_blob = " ".join([profile_name, *profile_terms])
    if profile_name.lower() not in NEUTRAL_PROFILES and token_pattern(term).search(profile_blob):
        return "PROFILE_DERIVED"
    if source_derived:
        return "SOURCE_DERIVED"
    return "CORE_LEAK"


def scan_leakage(repo: Path, artifacts: dict[str, Any], inventory_paths: list[str], *,
                 profile_name: str = "neutral/default", profile_terms: Iterable[str] = ()) -> list[dict[str, Any]]:
    derived = source_terms(repo, inventory_paths)
    rows: list[dict[str, Any]] = []
    for artifact_name, payload in artifacts.items():
        for json_path, text in walk_strings(payload):
            for term in LEAK_TERMS:
                spans = boundary_occurrences(text, term)
                if not spans:
                    continue
                provenance = classify_occurrence(
                    term=term, json_path=json_path, artifact_name=artifact_name,
                    source_derived=term in derived, profile_name=profile_name, profile_terms=profile_terms,
                )
                rows.append({
                    "term": term, "artifact": artifact_name, "jsonPath": json_path,
                    "occurrenceCount": len(spans), "provenance": provenance,
                    "severity": "BUG_LEAKAGE" if provenance == "CORE_LEAK" else "EVIDENCE_CONTEXT",
                })
    return rows


def prepare_metrics(prepared: dict[str, Any], discovery_graphs: dict[str, Any]) -> dict[str, Any]:
    model = prepared.get("changeModel") or {}
    radius = model.get("impactRadius") or {}
    changed = set(str(x) for x in radius.get("changed") or [])
    impacted = set(str(x) for x in radius.get("impacted") or [])
    dep_graph = discovery_graphs.get("dependencyGraph") or {}
    direct = {
        str(edge.get("from")) for edge in dep_graph.get("edges") or []
        if str(edge.get("to")) in changed and str(edge.get("from")) in impacted and str(edge.get("from")) not in changed
    }
    transitive = impacted - changed - direct
    discovery_impact = discovery_graphs.get("changeImpact") or {}
    return {
        "discoveryGraphNodes": len(dep_graph.get("nodes") or []),
        "discoveryGraphEdges": int(dep_graph.get("edgeCount") or 0),
        "discoveryChangeImpactSize": len(discovery_impact.get("impacted") or []),
        "prepareImpactRadiusSize": len(impacted),
        "prepareDirectImpactCount": len(direct),
        "prepareTransitiveImpactCount": len(transitive),
        "protectedScopeCount": len(model.get("protectedScope") or []),
        "requiredEvidenceCount": len(model.get("requiredEvidence") or []),
        "prepareImpactSource": "prepared.changeModel.impactRadius",
        "impactPartitionSource": "discovery dependency topology intersected with PREPARE impact membership",
        "legacyDiscoveryChangeImpactSize": "DEPRECATED_DO_NOT_USE",
    }


def stable_view(context: dict[str, Any]) -> dict[str, Any]:
    snap = context.get("snapshot") or {}
    auth = context.get("authorities") or {}
    return {
        "repository": snap.get("repository"), "profile": snap.get("profile"), "scanner": snap.get("scannerVersion"),
        "request": snap.get("requestDigest"), "authorityHashes": snap.get("authorityHashes"),
        "materialHashes": snap.get("materialHashes"), "inventoryDigest": snap.get("inventoryDigest"),
        "authorityDigest": snap.get("authorityDigest"), "graphs": digest(context.get("graphs") or {}),
        "authorities": digest(auth.get("candidates") or []), "coverage": digest(context.get("coverage") or {}),
    }


def finding_codes(report: dict[str, Any]) -> list[str]:
    return sorted({str(row.get("code")) for row in report.get("findings") or [] if isinstance(row, dict) and row.get("code")})


def negative_row(name: str, report: dict[str, Any], accepted: set[str], seconds: float) -> dict[str, Any]:
    actual = str(report.get("decision") or "ERROR")
    return {
        "scenario": name, "actual": actual, "accepted": sorted(accepted), "behaviorPass": actual in accepted,
        "findingCodes": finding_codes(report), "seconds": round(seconds, 4),
    }


def run_negatives(spec: RepoSpec, base: Path, root: Path, pbase: dict[str, Any], pstrict: dict[str, Any],
                  pauth: dict[str, Any] | None, pol: dict[str, Any], pol_strict: dict[str, Any],
                  pol_auth: dict[str, Any] | None, protected: str | None, authority: str | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def verify(name: str, repo: Path, changed: list[str], prep: dict[str, Any], current_policy: dict[str, Any],
               accepted: set[str], evidence: list[Any] | None = None) -> None:
        started = time.perf_counter()
        report = verify_prepared_change(
            prep, repo, changed_paths=changed, produced_evidence=evidence, policy=current_policy, workers=WORKERS,
        )
        rows.append(negative_row(name, report, accepted, time.perf_counter() - started))

    wt = worktree(base, root, f"{spec.repo_id}_allowed")
    try:
        mutate(wt / spec.target)
        verify("allowed_in_scope", wt, [spec.target], pbase, pol, {"PASS"})
    finally:
        remove_worktree(base, wt)

    wt = worktree(base, root, f"{spec.repo_id}_outside")
    try:
        mutate(wt / spec.other)
        verify("out_of_scope", wt, [spec.other], pbase, pol, {"BLOCKED"})
    finally:
        remove_worktree(base, wt)

    if protected:
        wt = worktree(base, root, f"{spec.repo_id}_protected")
        try:
            mutate(wt / protected)
            verify("protected_path", wt, [protected], pbase, pol, {"BLOCKED"})
        finally:
            remove_worktree(base, wt)

    verify("missing_required_evidence", base, [], pstrict, pol_strict, {"BLOCKED"}, evidence=[])

    if pauth and pol_auth and authority:
        wt = worktree(base, root, f"{spec.repo_id}_authority")
        try:
            mutate(wt / authority)
            verify("authority_drift", wt, [authority], pauth, pol_auth, {"BLOCKED"})
        finally:
            remove_worktree(base, wt)

    evidence_path = protected or authority
    if evidence_path:
        wt = worktree(base, root, f"{spec.repo_id}_evidence")
        try:
            mutate(wt / evidence_path)
            verify("evidence_drift", wt, [], pbase, pol, {"BLOCKED"})
        finally:
            remove_worktree(base, wt)

    wt = worktree(base, root, f"{spec.repo_id}_stale")
    try:
        mutate(wt / spec.target)
        git(wt, "config", "user.name", "CAEXT V2")
        git(wt, "config", "user.email", "caext-v2@example.invalid")
        git(wt, "add", "--", spec.target)
        git(wt, "commit", "-m", "caext v2 disposable fixture")
        verify("stale_commit_tree", wt, [spec.target], pbase, pol, {"BLOCKED"})
    finally:
        remove_worktree(base, wt)

    started = time.perf_counter()
    missing = prepare_change(
        base, change_request="Modify a target that does not exist; do not guess.",
        target_paths=["__missing__/never.exists"], policy=pol, domain="runtime", intent="VERIFY", workers=WORKERS,
    )
    rows.append(negative_row("unknown_target", missing, {"BLOCKED", "UNKNOWN"}, time.perf_counter() - started))

    wt = worktree(base, root, f"{spec.repo_id}_unicode")
    try:
        rel = "caext fixtures/área incómoda/new route.txt"
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_text("fixture\n", encoding="utf-8")
        verify("new_unicode_space_path", wt, [rel], pbase, pol, {"BLOCKED"})
    finally:
        remove_worktree(base, wt)

    wt = worktree(base, root, f"{spec.repo_id}_dirty")
    try:
        rel = "caext hidden/ñ dirty outside scope.txt"
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_text("fixture\n", encoding="utf-8")
        verify("dirty_hidden_outside_manifest", wt, [], pbase, pol, {"BLOCKED"})
    finally:
        remove_worktree(base, wt)
    return rows


def historical_validation(spec: RepoSpec, base: Path, root: Path) -> dict[str, Any]:
    if not spec.historical_commit or not spec.historical_paths:
        return {"status": "NOT_MEASURED"}
    if spec.historical_commit != spec.sha:
        git(base, "fetch", "--depth=1", "--no-tags", "origin", spec.historical_commit)
    wt = worktree(base, root, f"historical_{spec.repo_id}")
    try:
        git(wt, "checkout", "--detach", spec.historical_commit)
        context = resolve_intelligence_context(
            wt, request=IntelligenceRequest(intent="VERIFY", domain="runtime", changed_paths=(spec.target,), workers=WORKERS),
        )
        impacted = set(((context.get("graphs") or {}).get("changeImpact") or {}).get("impacted") or [])
        actual = set(spec.historical_paths)
        return {
            "status": "MEASURED", "commit": spec.historical_commit,
            "actualChanged": sorted(actual), "impact": sorted(impacted),
            "missedHistorical": sorted(actual - impacted), "extraImpact": sorted(impacted - actual),
            "recallPct": round(100 * len(actual & impacted) / max(1, len(actual)), 2),
        }
    finally:
        remove_worktree(base, wt)


def selected_specs(repo_set: str) -> tuple[RepoSpec, ...]:
    if repo_set == "regression":
        return REGRESSION_SPECS
    if repo_set == "diversity":
        if not DIVERSITY_SPECS:
            raise RuntimeError("DIVERSITY_SET_NOT_YET_AUTHORIZED_BY_GREEN_REGRESSION")
        return DIVERSITY_SPECS
    if not DIVERSITY_SPECS:
        raise RuntimeError("DIVERSITY_SET_NOT_YET_AUTHORIZED_BY_GREEN_REGRESSION")
    return (*REGRESSION_SPECS, *DIVERSITY_SPECS)


def run_gate(repo_set: str, output_root: Path, hitech_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    if git(hitech_root, "diff", "--quiet", PIN, "--", "tools/code-atlas/src/code_atlas", check=False).returncode != 0:
        raise RuntimeError("CODE_ATLAS_CORE_DIFFERS_FROM_CERTIFIED_PIN")

    temp_root = Path(tempfile.mkdtemp(prefix="caext_v2_"))
    stage = temp_root / "package"
    stage.mkdir(parents=True)
    started_all = time.perf_counter()
    state: dict[str, Any] = {
        "schemaVersion": "caext_v2.v1", "classification": "VERIFY / EXTERNAL EVIDENCE",
        "harnessFailureClass": "J TEST HARNESS FAILURE", "codeAtlasCommit": PIN,
        "repoSet": repo_set, "startedAt": iso(), "workersConfigured": WORKERS,
        "workerPeak": "NOT_MEASURED", "productionCertified": False, "repos": [], "failures": [],
    }
    try:
        for spec in selected_specs(repo_set):
            repo_started = time.perf_counter()
            repo_stage = stage / f"repo_{spec.repo_id}"
            repo_stage.mkdir(parents=True)
            timings: dict[str, Any] = {}

            t0 = time.perf_counter()
            base = clone_pinned(spec, temp_root)
            timings["cloneSeconds"] = round(time.perf_counter() - t0, 4)
            pre = identity(base)
            jdump(repo_stage / "identity_pre.json", pre)

            t0 = time.perf_counter()
            inventory = discover_repository(base, workers=WORKERS)
            timings["repositoryDiscoverySeconds"] = round(time.perf_counter() - t0, 4)
            inventory_paths = [str(row.get("path")) for row in inventory.get("files") or [] if row.get("path")]

            discover_request = IntelligenceRequest(intent="DISCOVER", domain="runtime", semantic_query=spec.request, workers=WORKERS)
            t0 = time.perf_counter()
            context1 = resolve_intelligence_context(base, request=discover_request)
            timings["intelligenceDiscoverSeconds"] = round(time.perf_counter() - t0, 4)
            graphs = context1.get("graphs") or {}
            authorities = context1.get("authorities") or {}
            coverage = context1.get("coverage") or {}

            protected = next((name for name in ("README.md", "SECURITY.md", "CONTRIBUTING.md") if (base / name).is_file()), None)
            authority = next((name for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", ".github/CODEOWNERS", "CODEOWNERS", "pyproject.toml", "package.json", "Cargo.toml") if (base / name).is_file()), None)
            pol = policy(spec.repo_id, protected)
            pol_strict = policy(spec.repo_id, protected, strict=True)
            pol_auth = policy(spec.repo_id, protected, authority=authority) if authority else None

            t0 = time.perf_counter()
            pbase = prepare_change(base, change_request=spec.request, target_paths=[spec.target], policy=pol, domain="runtime", intent="VERIFY", workers=WORKERS)
            pstrict = prepare_change(base, change_request=spec.request, target_paths=[spec.target], policy=pol_strict, domain="runtime", intent="VERIFY", workers=WORKERS)
            pauth = prepare_change(base, change_request=spec.request, target_paths=[spec.target], policy=pol_auth, domain="runtime", intent="VERIFY", workers=WORKERS) if pol_auth else None
            timings["prepareChangeSeconds"] = round(time.perf_counter() - t0, 4)
            jdump(repo_stage / "prep_base.json", pbase)
            jdump(repo_stage / "prep_strict.json", pstrict)

            t0 = time.perf_counter()
            context2 = resolve_intelligence_context(base, request=discover_request)
            view1, view2 = stable_view(context1), stable_view(context2)
            repeatability = {"stable": view1 == view2, "fingerprint1": digest(view1), "fingerprint2": digest(view2)}
            timings["repeatabilitySeconds"] = round(time.perf_counter() - t0, 4)

            t0 = time.perf_counter()
            negatives = run_negatives(spec, base, temp_root, pbase, pstrict, pauth, pol, pol_strict, pol_auth, protected, authority)
            timings["negativeSuiteSeconds"] = round(time.perf_counter() - t0, 4)
            timings["verifySecondsMeasuredInsideNegatives"] = round(sum(float(row.get("seconds") or 0) for row in negatives), 4)
            jdump(repo_stage / "negative_tests.json", negatives)

            t0 = time.perf_counter()
            historical = historical_validation(spec, base, temp_root)
            timings["historicalValidationSeconds"] = round(time.perf_counter() - t0, 4)
            jdump(repo_stage / "historical_validation.json", historical)

            t0 = time.perf_counter()
            leaks = scan_leakage(
                base,
                {"intelligence_context.json": context1, "prep_base.json": pbase, "prep_strict.json": pstrict},
                inventory_paths,
                profile_name="neutral/default",
            )
            timings["leakScanSeconds"] = round(time.perf_counter() - t0, 4)
            jdump(repo_stage / "neutrality_leaks.json", leaks)

            post = identity(base)
            jdump(repo_stage / "identity_post.json", post)
            baseline_unchanged = pre["head"] == post["head"] and pre["tree"] == post["tree"] and not post["dirty"]
            states = Counter(str(row.get("state")) for row in authorities.get("candidates") or [])
            prep = prepare_metrics(pbase, graphs)
            bad_negatives = [row for row in negatives if not row.get("behaviorPass")]
            core_leaks = [row for row in leaks if row.get("provenance") == "CORE_LEAK"]
            timings.update({"graphBuildSeconds": "NOT_MEASURED", "retrievalSeconds": "NOT_MEASURED", "workerPeak": "NOT_MEASURED"})
            timings["repoTotalSeconds"] = round(time.perf_counter() - repo_started, 4)

            metrics = {
                "repoId": spec.repo_id, "repository": spec.slug, "stack": spec.stack, "commit": spec.sha, "tree": spec.tree,
                "profile": "neutral/default", "fileCount": inventory.get("fileCount"), "workersConfigured": WORKERS,
                "workerPeak": "NOT_MEASURED", "authorityDiscoveryCount": len(authorities.get("candidates") or []),
                "AUTHORITATIVE": states["AUTHORITATIVE"], "SUPPORTED": states["SUPPORTED"],
                "CONFLICTED": states["CONFLICTED"], "MISSING": states["MISSING"], **prep,
                "ownershipEdges": (graphs.get("ownershipGraph") or {}).get("edgeCount"),
                "evidenceEdges": (graphs.get("evidenceGraph") or {}).get("edgeCount"),
                "architectureNodes": len((graphs.get("architectureLayerGraph") or {}).get("nodes") or []),
                "testCount": (graphs.get("testIntelligence") or {}).get("testCount"),
                "physicalCoverage": (coverage.get("physical") or {}).get("percent"),
                "semanticCoverage": (coverage.get("semantic") or {}).get("percent"),
                "coreLeakCount": len(core_leaks),
                "leakOccurrencesByProvenance": dict(Counter(str(row.get("provenance")) for row in leaks)),
                "negativePassed": sum(1 for row in negatives if row.get("behaviorPass")), "negativeTotal": len(negatives),
                "negativeFailures": len(bad_negatives), "repeatability": repeatability["stable"],
                "historicalRecallPct": historical.get("recallPct", "NOT_MEASURED"),
                "baselineCloneUnchanged": baseline_unchanged, "errors": 0, "retries": 0,
                "blockers": sum(1 for row in negatives if row.get("actual") == "BLOCKED"), "phaseTimings": timings,
            }
            jdump(repo_stage / "metrics.json", metrics)
            jdump(repo_stage / "repeatability.json", repeatability)
            state["repos"].append({"spec": spec.__dict__, "metrics": metrics, "negative": negatives, "leaks": leaks})

        all_metrics = [row["metrics"] for row in state["repos"]]
        bad = [(row["spec"]["repo_id"], neg) for row in state["repos"] for neg in row["negative"] if not neg.get("behaviorPass")]
        core_leaks = [(row["spec"]["repo_id"], leak) for row in state["repos"] for leak in row["leaks"] if leak.get("provenance") == "CORE_LEAK"]
        all_repeat = all(bool(row["metrics"].get("repeatability")) for row in state["repos"])
        all_read_only = all(bool(row["metrics"].get("baselineCloneUnchanged")) for row in state["repos"])
        recommendation = (
            "FIX_HARNESS_OR_REVIEW_BEHAVIOR" if core_leaks or bad else
            "BLOCKED_EVIDENCE_QUALITY" if not all_repeat or not all_read_only else
            "VERIFY_CONTINUE_EXTERNAL_DIVERSITY"
        )
        state["recommendedClassification"] = recommendation

        fields = sorted({key for row in all_metrics for key in row if key != "phaseTimings"})
        with (stage / "01_REPO_MATRIX.csv").open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in all_metrics:
                writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value for key, value in row.items() if key != "phaseTimings"})
        jdump(stage / "02_REPO_MATRIX.json", all_metrics)
        jdump(stage / "PERFORMANCE.json", {row["repoId"]: row["phaseTimings"] for row in all_metrics})
        md(stage / "00_EXECUTIVE_SUMMARY.md", f"""# CODE ATLAS EXTERNAL DIVERSITY GATE V2 — {repo_set.upper()}

- Repositories tested: **{len(all_metrics)}**
- Read-only compliance: **{'PASS' if all_read_only else 'BLOCKED'}**
- Repeatability: **{'PASS' if all_repeat else 'BLOCKED'}**
- CORE_LEAK findings: **{len(core_leaks)}**
- Negative behavior failures: **{len(bad)}**
- Recommended classification: **{recommendation}**
- Code Atlas source pin: `{PIN}`
- Worker peak: `NOT_MEASURED` unless explicitly instrumented.

## Harness V2 truth rules
- Leakage matching uses token boundaries, not raw substring matching.
- Every occurrence is `SOURCE_DERIVED`, `PROFILE_DERIVED`, `HISTORICAL_TOOL_EVIDENCE`, or `CORE_LEAK`.
- Impact Radius size comes from `prepared.changeModel.impactRadius`, never the DISCOVER change-impact result.
- Direct/transitive partitions are restricted to PREPARE membership; dependency topology only partitions that membership.
- `UNKNOWN` and `BLOCKED` remain valid outcomes.
- This does not certify production, enterprise, arbitrary repositories, IAM/security, privacy/legal, hosted multi-tenant, or paid-pilot readiness.
""")
        md(stage / "NEGATIVE_TEST_RESULTS.md", "# NEGATIVE TEST RESULTS\n\n" + "\n".join(
            f"- Repo {repo_id}: {'PASS' if row.get('behaviorPass') else 'FAIL'} `{row.get('scenario')}` -> `{row.get('actual')}`; findings `{','.join(row.get('findingCodes') or [])}`"
            for repo_id, row in [(r["spec"]["repo_id"], n) for r in state["repos"] for n in r["negative"]]
        ))
        md(stage / "NEUTRALITY_LEAK_SCAN.md", "# NEUTRALITY LEAK SCAN V2\n\n" + (
            "- No `CORE_LEAK` findings. Source/profile/historical-derived occurrences remain explicitly classified."
            if not core_leaks else "\n".join(f"- Repo {repo_id}: {row}" for repo_id, row in core_leaks)
        ))
        md(stage / "NEXT_GATE.md", f"# NEXT GATE\n\nRecommended classification: **{recommendation}**\n\n" + (
            "Proceed to the broader diversity repo set without modifying Code Atlas core."
            if recommendation == "VERIFY_CONTINUE_EXTERNAL_DIVERSITY" else
            "Stop. Adjudicate the recorded failure before any broader claim or core change."
        ))
    except Exception as exc:
        state["failures"].append({"class": "I/J ENVIRONMENT OR HARNESS FAILURE", "error": repr(exc), "traceback": traceback.format_exc()})
        state["recommendedClassification"] = "BLOCKED"
        md(stage / "00_EXECUTIVE_SUMMARY.md", "# CODE ATLAS EXTERNAL DIVERSITY GATE V2\n\n**BLOCKED / INCOMPLETE.** See run_state.json.")
    finally:
        state["finishedAt"] = iso()
        state["elapsedSeconds"] = round(time.perf_counter() - started_all, 4)
        jdump(stage / "run_state.json", state)
        files = []
        for path in sorted(stage.rglob("*")):
            if path.is_file() and path.name != "EVIDENCE_INDEX.json":
                files.append({"path": path.relative_to(stage).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
        jdump(stage / "EVIDENCE_INDEX.json", {"schemaVersion": "caext_v2_evidence_index.v1", "generatedAt": iso(), "codeAtlasCommit": PIN, "files": files})
        suffix = datetime.now().astimezone().strftime("%d%m_%H%M%S")
        out = output_root / f"caextv2_{repo_set}_{suffix}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(stage).as_posix())
        shutil.rmtree(temp_root, ignore_errors=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas External Diversity Gate V2")
    parser.add_argument("--repo-set", choices=("regression", "diversity", "all"), default="regression")
    parser.add_argument("--output", required=True)
    parser.add_argument("--hitech-root", default=".")
    args = parser.parse_args()
    out = run_gate(args.repo_set, Path(args.output).resolve(), Path(args.hitech_root).resolve())
    print(f"CAEXT_V2_RESULT={out}")
    with zipfile.ZipFile(out) as archive:
        state = json.loads(archive.read("run_state.json").decode("utf-8"))
    print(f"CAEXT_V2_CLASSIFICATION={state.get('recommendedClassification')}")
    return 0 if state.get("recommendedClassification") in {"VERIFY_CONTINUE_EXTERNAL_DIVERSITY", "VERIFY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
