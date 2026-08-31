from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import time
import traceback
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_v1():
    source = Path(__file__).with_name("caext_historical_real_diff_v1.py")
    spec = importlib.util.spec_from_file_location("caext_historical_real_diff_v1", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("HISTORICAL_V1_HARNESS_IMPORT_UNAVAILABLE")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V1 = _load_v1()
CASES = V1.CASES
BASELINE_REFERENCE_PIN = V1.PIN
WORKERS = V1.WORKERS


def iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def jdump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def pct(numerator: int, denominator: int) -> float | str:
    if denominator == 0:
        return "NOT_APPLICABLE"
    return round(100.0 * numerator / denominator, 2)


def stable_v2_view(report: dict[str, Any]) -> dict[str, Any]:
    model = report.get("changeModel") or {}
    radius = model.get("impactRadius") or {}
    pack = report.get("authorityPack") or {}
    return {
        "decision": report.get("decision"),
        "legacyImpacted": sorted(str(x) for x in radius.get("impacted") or []),
        "inspectionPaths": sorted(str(x) for x in radius.get("inspectionPaths") or []),
        "inspectOnlyCandidates": sorted(str(x) for x in radius.get("inspectOnlyCandidates") or []),
        "whyIsThisInBlast": radius.get("whyIsThisInBlast") or [],
        "unknownOrUnsupported": radius.get("unknownOrUnsupported") or [],
        "blastDigest": radius.get("blastDigest"),
        "allowedScope": sorted(str(x) for x in pack.get("allowedScope") or []),
        "impactRadiusIsAuthorization": radius.get("impactRadiusIsAuthorization"),
    }


def score_projection(target: str, actual: set[str], predicted: set[str]) -> dict[str, Any]:
    hits = actual & predicted
    false_negatives = actual - predicted
    false_positives = predicted - actual
    actual_companions = actual - {target}
    predicted_companions = predicted - {target}
    companion_hits = actual_companions & predicted_companions
    return {
        "actualChangedCount": len(actual),
        "predictedCount": len(predicted),
        "hitCount": len(hits),
        "recallPct": pct(len(hits), len(actual)),
        "precisionPct": pct(len(hits), len(predicted)),
        "actualCompanionCount": len(actual_companions),
        "predictedCompanionCount": len(predicted_companions),
        "companionRecallPct": pct(len(companion_hits), len(actual_companions)),
        "falsePositiveCount": len(false_positives),
        "falsePositiveRatioPct": pct(len(false_positives), len(predicted)),
        "actualChanged": sorted(actual),
        "predicted": sorted(predicted),
        "hits": sorted(hits),
        "falseNegatives": sorted(false_negatives),
        "falsePositives": sorted(false_positives),
    }


def score_existing(case: Any, report: dict[str, Any], actual: set[str]) -> dict[str, Any]:
    model = report.get("changeModel") or {}
    radius = model.get("impactRadius") or {}
    pack = report.get("authorityPack") or {}
    legacy = {str(x) for x in radius.get("impacted") or []}
    primary = {str(x) for x in radius.get("inspectionPaths") or legacy}
    inspect_only = {str(x) for x in radius.get("inspectOnlyCandidates") or []}
    all_candidates = primary | inspect_only
    unknown = list(radius.get("unknownOrUnsupported") or [])
    allowed = {str(x) for x in pack.get("allowedScope") or []}
    widening = sorted(allowed - {case.target})
    relations = list((radius.get("inspectionV2") or {}).get("relations") or [])
    missing_provenance = [
        row for row in relations
        if row.get("supportLevel") != "UNKNOWN" and not row.get("evidence")
    ]
    baseline = score_projection(case.target, actual, legacy)
    blast_primary = score_projection(case.target, actual, primary)
    blast_all = score_projection(case.target, actual, all_candidates)
    return {
        "decision": str(report.get("decision") or "UNKNOWN"),
        "target": case.target,
        "baseline": baseline,
        "blastV2Primary": blast_primary,
        "blastV2AllInspectionCandidates": blast_all,
        "inspectOnlyCandidateCount": len(inspect_only),
        "inspectOnlyCandidates": sorted(inspect_only),
        "unknownOrUnsupportedCount": len(unknown),
        "unknownOrUnsupportedRatePct": pct(len(unknown), len(primary) + len(unknown)),
        "authorizationWideningCount": len(widening),
        "authorizationWideningPaths": widening,
        "nonUnknownRelationMissingEvidenceCount": len(missing_provenance),
        "blastDigest": radius.get("blastDigest"),
        "impactRadiusIsAuthorization": radius.get("impactRadiusIsAuthorization"),
        "historicalCochangeIsInspectOnly": (radius.get("inspectionV2") or {}).get("historicalCochangeIsInspectOnly"),
        "ownershipIsInspectOnly": (radius.get("inspectionV2") or {}).get("ownershipIsInspectOnly"),
        "recallPct": baseline["recallPct"],
        "precisionPct": baseline["precisionPct"],
        "companionRecallPct": baseline["companionRecallPct"],
        "falseNegatives": baseline["falseNegatives"],
        "falsePositives": baseline["falsePositives"],
        "v2RecallPct": blast_primary["recallPct"],
        "v2PrecisionPct": blast_primary["precisionPct"],
        "v2CompanionRecallPct": blast_primary["companionRecallPct"],
        "v2FalsePositiveCount": blast_primary["falsePositiveCount"],
        "v2FalsePositiveRatioPct": blast_primary["falsePositiveRatioPct"],
        "accuracyInterpretation": "MEASURED_NOT_GATED",
    }


def score_new_path(case: Any, report: dict[str, Any], actual: set[str], target_exists: bool) -> dict[str, Any]:
    decision = str(report.get("decision") or "UNKNOWN")
    pack = report.get("authorityPack")
    accepted = decision in {"BLOCKED", "UNKNOWN"} and not bool(pack)
    return {
        "decision": decision,
        "target": case.target,
        "targetExistsInParent": target_exists,
        "actualChangedCount": len(actual),
        "actualChanged": sorted(actual),
        "authorityPackIssued": bool(pack),
        "expectedDecision": ["BLOCKED", "UNKNOWN"],
        "behaviorPass": accepted,
        "baseline": {"recallPct": "NOT_APPLICABLE_NEW_PATH_MISSING_IN_PARENT"},
        "blastV2Primary": {"recallPct": "NOT_APPLICABLE_NEW_PATH_MISSING_IN_PARENT"},
        "authorizationWideningCount": 0,
        "nonUnknownRelationMissingEvidenceCount": 0,
        "accuracyInterpretation": "FAIL_CLOSED_BEHAVIOR_ONLY",
    }


def self_test() -> None:
    actual = {"a.cpp", "test_a.cpp", "test_a.py"}
    baseline = score_projection("a.cpp", actual, {"a.cpp"})
    v2 = score_projection("a.cpp", actual, actual)
    assert baseline["recallPct"] == 33.33
    assert v2["recallPct"] == 100.0
    assert v2["precisionPct"] == 100.0
    assert v2["companionRecallPct"] == 100.0
    assert BASELINE_REFERENCE_PIN
    assert len(CASES) == 4
    print("PASS_CAEXT_HISTORICAL_BLAST_V2_SELF_TEST")


def run(output_root: Path, hitech_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    baseline_pin_check = V1.git(hitech_root, "cat-file", "-e", f"{BASELINE_REFERENCE_PIN}^{{commit}}", check=False)
    if baseline_pin_check.returncode != 0:
        raise RuntimeError("BASELINE_REFERENCE_PIN_MISSING")

    tmp = Path(tempfile.mkdtemp(prefix="caext_hist_blast_v2_"))
    stage = tmp / "package"
    stage.mkdir(parents=True)
    started = time.perf_counter()
    evaluated_commit = V1.git_text(hitech_root, "rev-parse", "HEAD")
    core_delta = V1.git_text(
        hitech_root, "diff", "--name-only", BASELINE_REFERENCE_PIN, "--", "tools/code-atlas/src/code_atlas",
    ) or ""
    state: dict[str, Any] = {
        "schemaVersion": "caext_historical_blast_v2.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE / HISTORICAL REAL-DIFF / BLAST V2",
        "baselineReferenceCommit": BASELINE_REFERENCE_PIN,
        "evaluatedCodeAtlasCommit": evaluated_commit,
        "evaluatedCoreDelta": [line for line in core_delta.splitlines() if line.strip()],
        "workersConfigured": WORKERS,
        "startedAt": iso(),
        "cases": [],
        "failures": [],
        "accuracyThresholds": "NONE_BY_DESIGN",
        "baselineRuntime": "NOT_SEPARATELY_MEASURABLE_WITHOUT_PARALLEL_ENGINE",
        "productionCertified": False,
    }

    try:
        for case in CASES:
            case_started = time.perf_counter()
            case_stage = stage / f"case_{case.case_id.lower()}"
            case_stage.mkdir(parents=True)
            repo = V1.clone_history(case, tmp)
            before = V1.identity(repo)
            if before["dirty"]:
                raise RuntimeError(f"DIRTY_PARENT_CLONE:{case.slug}")
            rows, actual, raw_diff = V1.actual_diff(repo, case)
            (case_stage / "actual_name_status.txt").write_text(raw_diff, encoding="utf-8")
            jdump(case_stage / "actual_diff.json", rows)

            target_exists = (repo / case.target).is_file()
            if case.mode == "existing_target" and (not target_exists or case.target not in actual):
                raise RuntimeError(f"HISTORICAL_TARGET_INVALID:{case.slug}:{case.target}")
            if case.mode == "new_path" and (target_exists or case.target not in actual):
                raise RuntimeError(f"HISTORICAL_NEW_PATH_INVALID:{case.slug}:{case.target}")

            t0 = time.perf_counter()
            prepare1 = V1.run_prepare(repo, case, case_stage / "prepare1")
            prepare1_seconds = round(time.perf_counter() - t0, 4)
            t0 = time.perf_counter()
            prepare2 = V1.run_prepare(repo, case, case_stage / "prepare2")
            prepare2_seconds = round(time.perf_counter() - t0, 4)
            jdump(case_stage / "prepare1.json", prepare1)
            jdump(case_stage / "prepare2.json", prepare2)

            stable1 = stable_v2_view(prepare1)
            stable2 = stable_v2_view(prepare2)
            repeatable = stable1 == stable2
            repeatability = {
                "stable": repeatable,
                "fingerprint1": digest(stable1),
                "fingerprint2": digest(stable2),
                "blastDigest1": stable1.get("blastDigest"),
                "blastDigest2": stable2.get("blastDigest"),
                "view1": stable1,
                "view2": stable2,
            }
            jdump(case_stage / "repeatability.json", repeatability)

            if case.mode == "existing_target":
                score = score_existing(case, prepare1, actual)
                behavior_pass = True
            else:
                score = score_new_path(case, prepare1, actual, target_exists)
                behavior_pass = bool(score["behaviorPass"])
            jdump(case_stage / "score.json", score)

            after = V1.identity(repo)
            read_only = before["head"] == after["head"] and before["tree"] == after["tree"] and not after["dirty"]
            jdump(case_stage / "identity_before.json", before)
            jdump(case_stage / "identity_after.json", after)

            result = {
                "caseId": case.case_id,
                "repository": case.slug,
                "stack": case.stack,
                "mode": case.mode,
                "parent": case.parent,
                "commit": case.commit,
                "target": case.target,
                "decision": score["decision"],
                "repeatability": repeatable,
                "readOnly": read_only,
                "behaviorPass": behavior_pass,
                "prepare1Seconds": prepare1_seconds,
                "prepare2Seconds": prepare2_seconds,
                "v2RuntimeSecondsMean": round((prepare1_seconds + prepare2_seconds) / 2.0, 4),
                "totalSeconds": round(time.perf_counter() - case_started, 4),
                **{k: v for k, v in score.items() if k not in {"decision", "target", "behaviorPass"}},
            }
            state["cases"].append(result)

            if not repeatable:
                state["failures"].append({"caseId": case.case_id, "class": "PRODUCT", "code": "V2_NONDETERMINISM"})
            if not read_only:
                state["failures"].append({"caseId": case.case_id, "class": "HARNESS", "code": "EXTERNAL_READ_ONLY_VIOLATION"})
            if case.mode == "new_path" and not behavior_pass:
                state["failures"].append({"caseId": case.case_id, "class": "PRODUCT", "code": "NEW_PATH_FAIL_CLOSED_VIOLATION"})
            if score.get("authorizationWideningCount", 0):
                state["failures"].append({"caseId": case.case_id, "class": "PRODUCT", "code": "AUTHORIZATION_WIDENING"})
            if score.get("nonUnknownRelationMissingEvidenceCount", 0):
                state["failures"].append({"caseId": case.case_id, "class": "PRODUCT", "code": "RELATION_PROVENANCE_MISSING"})

        state["recommendedClassification"] = (
            "VERIFY_BLAST_V2_HISTORICAL_EVIDENCE_CAPTURED" if not state["failures"]
            else "BLOCKED_BLAST_V2_EVIDENCE_QUALITY"
        )
        rows = state["cases"]
        jdump(stage / "02_HISTORICAL_BLAST_V2_MATRIX.json", rows)
        flat_fields = sorted({
            key for row in rows for key, value in row.items()
            if not isinstance(value, (dict, list))
        })
        with (stage / "01_HISTORICAL_BLAST_V2_MATRIX.csv").open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=flat_fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({key: row.get(key) for key in flat_fields})

        lines = [
            "# HISTORICAL REAL-DIFF BASELINE VS BLAST V2",
            "",
            "Accuracy remains measured evidence, not a pass/fail threshold.",
            "Historical co-change and ownership remain inspect-only and cannot widen edit authority.",
            "",
        ]
        for row in rows:
            baseline = row.get("baseline") or {}
            v2 = row.get("blastV2Primary") or {}
            all_candidates = row.get("blastV2AllInspectionCandidates") or {}
            lines.extend([
                f"## {row['caseId']} — {row['repository']}",
                f"- Decision: `{row['decision']}`",
                f"- Baseline recall / precision / companion: `{baseline.get('recallPct')}` / `{baseline.get('precisionPct')}` / `{baseline.get('companionRecallPct')}`",
                f"- V2 primary recall / precision / companion: `{v2.get('recallPct')}` / `{v2.get('precisionPct')}` / `{v2.get('companionRecallPct')}`",
                f"- V2 primary false-positive count / ratio: `{v2.get('falsePositiveCount')}` / `{v2.get('falsePositiveRatioPct')}`",
                f"- V2 all-candidate recall / precision: `{all_candidates.get('recallPct')}` / `{all_candidates.get('precisionPct')}`",
                f"- UNKNOWN/unsupported count / rate: `{row.get('unknownOrUnsupportedCount')}` / `{row.get('unknownOrUnsupportedRatePct')}`",
                f"- Authorization widening: `{row.get('authorizationWideningCount')}`",
                f"- Repeatable: `{row.get('repeatability')}`",
                f"- V2 mean runtime seconds: `{row.get('v2RuntimeSecondsMean')}`",
                "",
            ])
        md(stage / "HISTORICAL_BLAST_V2_ACCURACY.md", "\n".join(lines))
        md(stage / "00_EXECUTIVE_SUMMARY.md", f"""# CODE ATLAS HISTORICAL BLAST V2

- Reuses V1 historical carrier/cases: **YES**
- Baseline reference pin: `{BASELINE_REFERENCE_PIN}`
- Evaluated Code Atlas commit: `{evaluated_commit}`
- Cases: **{len(rows)}**
- Repeatability: **{'PASS' if all(r['repeatability'] for r in rows) else 'BLOCKED'}**
- External originals read-only: **{'PASS' if all(r['readOnly'] for r in rows) else 'BLOCKED'}**
- Authorization widening: **{sum(int(r.get('authorizationWideningCount', 0)) for r in rows)}**
- Relation provenance gaps: **{sum(int(r.get('nonUnknownRelationMissingEvidenceCount', 0)) for r in rows)}**
- Accuracy thresholds: **NONE BY DESIGN**
- Baseline runtime: **NOT_SEPARATELY_MEASURABLE_WITHOUT_PARALLEL_ENGINE**
- Classification: **{state['recommendedClassification']}**
- Production certified: **false**

The legacy `impactRadius.impacted` projection is the in-run baseline. Blast V2 is the additive inspection projection. Accuracy deltas are evidence, never edit authorization. Inspect-only ownership/history candidates are reported separately from the primary inspection set.
""")
        md(stage / "NEXT_GATE.md", "# NEXT GATE\n\nAdjudicate measured deltas. Any PRODUCT failure must be fixed or explicitly left unsupported. Do not convert low accuracy or UNKNOWN into a green claim.\n")
    except Exception as exc:
        state["failures"].append({"class": "ENVIRONMENT", "code": "HARNESS_OR_ENVIRONMENT_FAILURE", "error": repr(exc), "traceback": traceback.format_exc()})
        state["recommendedClassification"] = "BLOCKED"
        md(stage / "00_EXECUTIVE_SUMMARY.md", "# CODE ATLAS HISTORICAL BLAST V2\n\n**BLOCKED / INCOMPLETE.** See run_state.json.\n")
    finally:
        state["finishedAt"] = iso()
        state["elapsedSeconds"] = round(time.perf_counter() - started, 4)
        jdump(stage / "run_state.json", state)
        evidence = []
        for path in sorted(stage.rglob("*")):
            if path.is_file() and path.name != "EVIDENCE_INDEX.json":
                evidence.append({
                    "path": path.relative_to(stage).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                })
        jdump(stage / "EVIDENCE_INDEX.json", {
            "schemaVersion": "caext_historical_blast_v2_evidence_index.v1",
            "generatedAt": iso(),
            "baselineReferenceCommit": BASELINE_REFERENCE_PIN,
            "evaluatedCodeAtlasCommit": evaluated_commit,
            "files": evidence,
        })
        out = output_root / f"caextblastv2_{datetime.now().astimezone().strftime('%d%m_%H%M%S')}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(stage).as_posix())
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas historical Blast V2 evidence")
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
    print(f"CAEXT_BLAST_V2_RESULT={out}")
    with zipfile.ZipFile(out) as archive:
        state = json.loads(archive.read("run_state.json").decode("utf-8"))
    print(f"CAEXT_BLAST_V2_CLASSIFICATION={state.get('recommendedClassification')}")
    return 0 if state.get("recommendedClassification") == "VERIFY_BLAST_V2_HISTORICAL_EVIDENCE_CAPTURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
