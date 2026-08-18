from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from code_atlas.change_intelligence import (
    build_hardened_portable_bundle_manifest,
    build_rental_runner_plan,
    cleanup_customer_workspace,
    cleanup_published_artifacts,
    create_customer_workspace,
    sanitize_artifact_bytes,
    sanitize_artifacts_for_egress,
    validate_runner_cleanup,
    validate_runner_egress,
)
from code_atlas.change_intelligence.contracts import sha256_json
from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context

PIN = os.environ.get("CAEXT_RENTAL_P2_PIN", "d14effee1a1223cc772247ea9d7ec8547dc15c78")
WORKERS = max(1, min(18, int(os.environ.get("CAEXT_WORKERS", "18"))))

HISTORICAL_BASELINE = {
    "GO": {"recallPct": 25.0, "precisionPct": 100.0, "companionRecallPct": 0.0},
    "JAVA": {"recallPct": 50.0, "precisionPct": 100.0, "companionRecallPct": 0.0},
}


def iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def jdump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sh(cmd: list[str], *, cwd: Path | None = None, check: bool = True, timeout: int = 3600) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    if check and proc.returncode:
        raise RuntimeError(f"COMMAND_FAILED[{proc.returncode}] {' '.join(cmd)}\n{proc.stderr[-5000:]}")
    return proc


def git_text(repo: Path, *args: str) -> str:
    return sh(["git", "-C", str(repo), *args]).stdout.strip()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"MODULE_IMPORT_FAILED:{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_zip_json(path: Path, member: str) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read(member).decode("utf-8"))


def _delta(new: Any, old: Any) -> float | str:
    if not isinstance(new, (int, float)) or not isinstance(old, (int, float)):
        return "NOT_APPLICABLE"
    return round(float(new) - float(old), 2)


def run_existing_harnesses(hitech_root: Path, raw_root: Path) -> dict[str, Any]:
    historical = load_module(hitech_root / ".github/scripts/caext_historical_real_diff_v1.py", "caext_hist_p2")
    regression = load_module(hitech_root / ".github/scripts/caext_external_gate_v2.py", "caext_regression_p2")
    historical.PIN = PIN
    historical.WORKERS = WORKERS
    regression.PIN = PIN
    regression.WORKERS = WORKERS

    historical_zip = historical.run(raw_root / "historical", hitech_root)
    regression_zip = regression.run_gate("regression", raw_root / "regression", hitech_root)
    historical_state = read_zip_json(historical_zip, "run_state.json")
    regression_state = read_zip_json(regression_zip, "run_state.json")
    return {
        "historicalModule": historical,
        "historicalZip": historical_zip,
        "historicalState": historical_state,
        "regressionZip": regression_zip,
        "regressionState": regression_state,
    }


def probe_go_java(historical_module: Any, probe_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in historical_module.CASES:
        if case.case_id not in {"GO", "JAVA"}:
            continue
        case_root = probe_root / case.case_id.lower()
        case_root.mkdir(parents=True, exist_ok=True)
        repo = historical_module.clone_history(case, case_root)
        before = historical_module.identity(repo)
        _diff_rows, actual, _raw = historical_module.actual_diff(repo, case)
        context1 = resolve_intelligence_context(
            repo,
            case_root / "context1",
            request=IntelligenceRequest(intent="VERIFY", domain="runtime", changed_paths=(case.target,), workers=WORKERS),
        )
        context2 = resolve_intelligence_context(
            repo,
            case_root / "context2",
            request=IntelligenceRequest(intent="VERIFY", domain="runtime", changed_paths=(case.target,), workers=WORKERS),
        )
        after = historical_module.identity(repo)
        graphs1 = context1.get("graphs") or {}
        graphs2 = context2.get("graphs") or {}
        deps = graphs1.get("dependencyGraph") or {}
        impact = (graphs1.get("changeImpact") or {}).get("impacted") or []
        impacted = {str(item) for item in impact}
        actual_tests = {
            path
            for path in actual
            if path.endswith("_test.go") or "/src/test/" in "/" + path.replace("\\", "/") or path.endswith("Tests.java")
        }
        actual_companions = actual - {case.target}
        relevant_edges = [
            edge
            for edge in deps.get("edges") or []
            if edge.get("from") == case.target
            or edge.get("to") == case.target
            or edge.get("from") in actual
            or edge.get("to") in actual
        ]
        unresolved = [
            row
            for row in deps.get("unresolved") or []
            if row.get("language") in {"go", "java"}
        ]
        rows.append({
            "caseId": case.case_id,
            "repository": case.slug,
            "parent": case.parent,
            "commit": case.commit,
            "target": case.target,
            "readOnly": before.get("head") == after.get("head") and before.get("tree") == after.get("tree") and not after.get("dirty"),
            "dependencyEdgeCount": deps.get("edgeCount"),
            "relevantEdges": relevant_edges,
            "unresolvedLanguageFacts": unresolved,
            "impact": sorted(impacted),
            "actualChanged": sorted(actual),
            "changedTestRecallPct": round(100 * len(actual_tests & impacted) / max(1, len(actual_tests)), 2) if actual_tests else "NOT_APPLICABLE",
            "companionRecallPct": round(100 * len(actual_companions & impacted) / max(1, len(actual_companions)), 2) if actual_companions else "NOT_APPLICABLE",
            "graphRepeatability": graphs1 == graphs2,
        })
        shutil.rmtree(case_root, ignore_errors=True)
    return rows


def p0_roundtrip(temp_root: Path) -> dict[str, Any]:
    plan = build_rental_runner_plan(
        repository_identity="caext/private-customer-fixture",
        requested_outputs=["verification"],
        retention_mode="EPHEMERAL",
        retention_seconds=0,
    )
    workspace = create_customer_workspace(
        base_root=temp_root / "customer-workspaces",
        lifecycle_policy=plan["dataLifecyclePolicy"],
        session_id="p2-fixture",
    )
    workspace_root = Path(workspace["workspacePath"])
    raw = workspace_root / "report.json"
    raw.write_text(
        json.dumps(
            {
                "repository": "caext/private-customer-fixture",
                "token": "github_pat_seeded_secret_abcdefghijklmnopqrstuvwxyz",
                "owner": "private.customer@example.com",
                "status": "VERIFY",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    egress_root = temp_root / "synthetic-egress"
    prepared = sanitize_artifacts_for_egress(
        artifacts=[{"localPath": str(raw), "name": "reports/result.json", "kind": "verification"}],
        output_dir=egress_root,
    )
    manifest = build_hardened_portable_bundle_manifest(
        repository_snapshot={
            "repositoryIdentity": "caext/private-customer-fixture",
            "commitIdentity": "fixture-commit",
            "treeIdentity": "fixture-tree",
        },
        artifacts=prepared["artifacts"],
        sanitization_attestations=prepared["sanitizationAttestations"],
        lifecycle_policy_digest=plan["dataLifecyclePolicyDigest"],
        purpose="P2 rental hardening verification",
    )
    egress = validate_runner_egress(runner_plan=plan, bundle_manifest=manifest)
    sanitized_text = (egress_root / "reports/result.json").read_text(encoding="utf-8")
    if "github_pat_seeded_secret_abcdefghijklmnopqrstuvwxyz" in sanitized_text or "private.customer@example.com" in sanitized_text:
        raise RuntimeError("P0_SEEDED_SECRET_OR_PII_SURVIVED_SANITIZATION")
    cleanup = cleanup_customer_workspace(
        workspace=workspace,
        lifecycle_policy=plan["dataLifecyclePolicy"],
        reason="p2-verification-complete",
    )
    cleanup_validation = validate_runner_cleanup(runner_plan=plan, cleanup_evidence=cleanup)
    export_cleanup = cleanup_published_artifacts(
        published_files=prepared["publishedFiles"],
        output_root=egress_root,
    )
    return {
        "planSchema": plan["schemaVersion"],
        "manifestSchema": manifest["schemaVersion"],
        "sourceCodeIncluded": manifest["sourceCodeIncluded"],
        "allArtifactsInspected": manifest["allArtifactsInspected"],
        "artifactContentSanitizationProven": manifest["artifactContentSanitizationProven"],
        "sanitizationDecision": prepared["sanitizationAttestations"][0]["decision"],
        "seededSecretRemoved": True,
        "seededPiiRemoved": True,
        "egressAllowed": egress["allowed"],
        "postEgressCleanupRequired": egress["postEgressCleanupRequired"],
        "workspaceCleanupVerified": cleanup_validation["cleanupVerified"],
        "workspaceRemainingPaths": cleanup_validation["remainingPaths"],
        "publishedArtifactCleanupVerified": export_cleanup["cleanupVerified"],
        "secureEraseGuaranteed": False,
        "productionCertified": False,
    }


def sanitize_child_zip(source_zip: Path, destination_root: Path, prefix: str) -> list[dict[str, Any]]:
    attestations: list[dict[str, Any]] = []
    with zipfile.ZipFile(source_zip) as archive:
        for info in sorted(archive.infolist(), key=lambda item: item.filename):
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            content = archive.read(info)
            sanitized, attestation = sanitize_artifact_bytes(
                name=f"{prefix}/{name}",
                kind="p2-external-evidence",
                content=content,
            )
            target = destination_root / prefix / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(sanitized)
            attestations.append(attestation)
    return attestations


def sanitize_stage(raw_stage: Path, final_stage: Path) -> list[dict[str, Any]]:
    attestations: list[dict[str, Any]] = []
    for source in sorted(path for path in raw_stage.rglob("*") if path.is_file()):
        rel = source.relative_to(raw_stage).as_posix()
        sanitized, attestation = sanitize_artifact_bytes(
            name=rel,
            kind="p2-verification-evidence",
            content=source.read_bytes(),
        )
        target = final_stage / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sanitized)
        attestations.append(attestation)
    return attestations


def historical_comparison(historical_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in historical_state.get("cases") or []:
        case_id = case.get("caseId")
        baseline = HISTORICAL_BASELINE.get(str(case_id))
        if not baseline:
            continue
        rows.append({
            "caseId": case_id,
            "repository": case.get("repository"),
            "baseline": baseline,
            "current": {
                "recallPct": case.get("recallPct"),
                "precisionPct": case.get("precisionPct"),
                "companionRecallPct": case.get("companionRecallPct"),
                "falseNegatives": case.get("falseNegatives"),
                "falsePositives": case.get("falsePositives"),
            },
            "delta": {
                "recallPct": _delta(case.get("recallPct"), baseline["recallPct"]),
                "precisionPct": _delta(case.get("precisionPct"), baseline["precisionPct"]),
                "companionRecallPct": _delta(case.get("companionRecallPct"), baseline["companionRecallPct"]),
            },
            "accuracyIsAuthorization": False,
        })
    return rows


def run(output_root: Path, hitech_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    head = git_text(hitech_root, "rev-parse", "HEAD")
    tree = git_text(hitech_root, "rev-parse", "HEAD^{tree}")
    if head != PIN:
        raise RuntimeError(f"P2_PIN_MISMATCH:expected={PIN}:actual={head}")

    temp_root = Path(tempfile.mkdtemp(prefix="caext_rental_p2_"))
    raw_children = temp_root / "raw-children"
    raw_stage = temp_root / "raw-stage"
    final_stage = temp_root / "final-stage"
    raw_children.mkdir(parents=True)
    raw_stage.mkdir(parents=True)
    final_stage.mkdir(parents=True)
    started = time.perf_counter()
    state: dict[str, Any] = {
        "schemaVersion": "caext_rental_p2.v1",
        "classification": "VERIFY / EXTERNAL RENTAL EVIDENCE",
        "codeAtlasCommit": PIN,
        "codeAtlasTree": tree,
        "workersConfigured": WORKERS,
        "workerPeak": "NOT_MEASURED",
        "startedAt": iso(),
        "failures": [],
        "productionCertified": False,
        "certifiable": False,
        "humanUsefulness": "NOT_MEASURED",
        "independentReplication": "BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR",
    }

    try:
        child = run_existing_harnesses(hitech_root, raw_children)
        historical_state = child["historicalState"]
        regression_state = child["regressionState"]
        probes = probe_go_java(child["historicalModule"], temp_root / "probes")
        p0 = p0_roundtrip(temp_root / "p0")
        comparison = historical_comparison(historical_state)

        child_attestations = []
        child_attestations.extend(sanitize_child_zip(child["historicalZip"], raw_stage, "historical"))
        child_attestations.extend(sanitize_child_zip(child["regressionZip"], raw_stage, "regression"))

        historical_ok = historical_state.get("recommendedClassification") == "VERIFY_HISTORICAL_EVIDENCE_CAPTURED"
        regression_ok = regression_state.get("recommendedClassification") in {"VERIFY_CONTINUE_EXTERNAL_DIVERSITY", "VERIFY"}
        probes_ok = all(row.get("readOnly") and row.get("graphRepeatability") for row in probes)
        p0_ok = all(
            p0.get(key) is True
            for key in (
                "allArtifactsInspected",
                "artifactContentSanitizationProven",
                "seededSecretRemoved",
                "seededPiiRemoved",
                "egressAllowed",
                "postEgressCleanupRequired",
                "workspaceCleanupVerified",
                "publishedArtifactCleanupVerified",
            )
        ) and p0.get("sourceCodeIncluded") is False

        if not historical_ok:
            state["failures"].append({"class": "HISTORICAL_REPLAY_BLOCKED", "classification": historical_state.get("recommendedClassification")})
        if not regression_ok:
            state["failures"].append({"class": "REGRESSION_REPLAY_BLOCKED", "classification": regression_state.get("recommendedClassification")})
        if not probes_ok:
            state["failures"].append({"class": "GO_JAVA_PROBE_MECHANICS_BLOCKED"})
        if not p0_ok:
            state["failures"].append({"class": "P0_RENTAL_HARDENING_ROUNDTRIP_BLOCKED"})

        state.update({
            "historicalClassification": historical_state.get("recommendedClassification"),
            "regressionClassification": regression_state.get("recommendedClassification"),
            "historicalCases": historical_state.get("cases") or [],
            "historicalComparison": comparison,
            "goJavaDependencyProbes": probes,
            "p0Roundtrip": p0,
            "rawChildEvidenceUploaded": False,
            "childArtifactsSanitizedBeforeExport": True,
            "childSanitizationAttestationCount": len(child_attestations),
            "accuracyThresholds": "NONE_BY_DESIGN",
            "accuracyInterpretation": "MEASURED_NOT_GATED",
            "historyAuthorizes": False,
            "recommendedClassification": "VERIFY_RENTAL_P2_EVIDENCE_CAPTURED" if not state["failures"] else "BLOCKED_RENTAL_P2_EVIDENCE_QUALITY",
        })
        jdump(raw_stage / "P2_RESULT.json", state)
        jdump(raw_stage / "P0_RENTAL_ROUNDTRIP.json", p0)
        jdump(raw_stage / "GO_JAVA_DEPENDENCY_PROBES.json", probes)
        jdump(raw_stage / "HISTORICAL_COMPARISON.json", comparison)
        jdump(raw_stage / "CHILD_SANITIZATION_ATTESTATIONS.json", child_attestations)
        md(
            raw_stage / "00_EXECUTIVE_SUMMARY.md",
            f"""# CODE ATLAS RENTAL P2 EXTERNAL REPLAY V1

- Code Atlas pin: `{PIN}`
- Historical replay: **{historical_state.get('recommendedClassification')}**
- Click/Vite/ripgrep regression replay: **{regression_state.get('recommendedClassification')}**
- P0 private-repo lifecycle/sanitization roundtrip: **{'PASS' if p0_ok else 'BLOCKED'}**
- Go/Java dependency probe mechanics: **{'PASS' if probes_ok else 'BLOCKED'}**
- Raw child evidence uploaded: **NO**
- Exported child evidence sanitized: **YES**
- Accuracy thresholds: **NONE BY DESIGN**
- Recommended classification: **{state['recommendedClassification']}**

## Truth boundary
This P2 gate measures evidence after P0/P1. It does not convert impact radius into authorization, does not treat low recall/precision as a green signal, and does not certify production, enterprise, privacy/legal/security, paid-pilot readiness, human usefulness, or independent-agent replication.
""",
        )

        final_attestations = sanitize_stage(raw_stage, final_stage)
        jdump(
            final_stage / "FINAL_SANITIZATION_INDEX.json",
            {
                "schemaVersion": "caext_rental_p2_sanitization_index.v1",
                "codeAtlasCommit": PIN,
                "filesInspected": len(final_attestations),
                "allFilesInspected": True,
                "attestations": final_attestations,
                "rawChildEvidenceUploaded": False,
                "productionCertified": False,
            },
        )
    except Exception as exc:
        state["failures"].append({"class": "P2_HARNESS_OR_ENVIRONMENT_FAILURE", "error": repr(exc), "traceback": traceback.format_exc()})
        state["recommendedClassification"] = "BLOCKED_RENTAL_P2_INCOMPLETE"
        jdump(raw_stage / "P2_RESULT.json", state)
        md(raw_stage / "00_EXECUTIVE_SUMMARY.md", "# CODE ATLAS RENTAL P2 EXTERNAL REPLAY V1\n\n**BLOCKED / INCOMPLETE.** See P2_RESULT.json.\n")
        final_attestations = sanitize_stage(raw_stage, final_stage)
        jdump(
            final_stage / "FINAL_SANITIZATION_INDEX.json",
            {
                "schemaVersion": "caext_rental_p2_sanitization_index.v1",
                "codeAtlasCommit": PIN,
                "filesInspected": len(final_attestations),
                "allFilesInspected": True,
                "attestations": final_attestations,
                "rawChildEvidenceUploaded": False,
                "productionCertified": False,
            },
        )
    finally:
        state["finishedAt"] = iso()
        state["elapsedSeconds"] = round(time.perf_counter() - started, 4)
        # Refresh the final state after timing fields are known, through the same scanner.
        state_bytes = (json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        sanitized_state, state_attestation = sanitize_artifact_bytes(
            name="P2_RESULT.json",
            kind="p2-verification-evidence",
            content=state_bytes,
        )
        (final_stage / "P2_RESULT.json").write_bytes(sanitized_state)
        manifest_rows = []
        for path in sorted(final_stage.rglob("*")):
            if path.is_file():
                manifest_rows.append({
                    "path": path.relative_to(final_stage).as_posix(),
                    "sha256": sha256_bytes(path.read_bytes()),
                    "bytes": path.stat().st_size,
                })
        manifest = {
            "schemaVersion": "caext_rental_p2_manifest.v1",
            "codeAtlasCommit": PIN,
            "codeAtlasTree": tree,
            "classification": state.get("recommendedClassification"),
            "readOnlyExternalOriginalsRequired": True,
            "rawChildEvidenceUploaded": False,
            "finalStateSanitizationAttestation": state_attestation,
            "files": manifest_rows,
            "manifestDigest": None,
            "productionCertified": False,
            "certifiable": False,
        }
        manifest["manifestDigest"] = sha256_json({k: v for k, v in manifest.items() if k != "manifestDigest"})
        jdump(final_stage / "MANIFEST.json", manifest)
        out = output_root / f"caext_p2_{datetime.now().astimezone().strftime('%d%m_%H%M%S')}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
            for path in sorted(final_stage.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(final_stage).as_posix())
        shutil.rmtree(temp_root, ignore_errors=True)
    return out


def self_test() -> None:
    assert _delta(50.0, 25.0) == 25.0
    assert _delta("NOT_APPLICABLE", 25.0) == "NOT_APPLICABLE"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        child = root / "child.zip"
        with zipfile.ZipFile(child, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("result.json", json.dumps({"token": "ghp_abcdefghijklmnopqrstuvwxyz012345", "owner": "a@example.com"}))
        out = root / "sanitized"
        attestations = sanitize_child_zip(child, out, "child")
        text = (out / "child/result.json").read_text(encoding="utf-8")
        assert "ghp_abcdefghijklmnopqrstuvwxyz012345" not in text
        assert "a@example.com" not in text
        assert attestations[0]["decision"] == "PASS_SANITIZED"
    print("PASS_CAEXT_RENTAL_P2_SELF_TEST")


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas rental P2 external replay V1")
    parser.add_argument("--output")
    parser.add_argument("--hitech-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.output:
        parser.error("--output is required unless --self-test is used")
    out = run(Path(args.output).resolve(), Path(args.hitech_root).resolve())
    print(f"CAEXT_RENTAL_P2_RESULT={out}")
    with zipfile.ZipFile(out) as archive:
        state = json.loads(archive.read("P2_RESULT.json").decode("utf-8"))
    classification = state.get("recommendedClassification")
    print(f"CAEXT_RENTAL_P2_CLASSIFICATION={classification}")
    return 0 if classification == "VERIFY_RENTAL_P2_EVIDENCE_CAPTURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
