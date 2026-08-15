from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import traceback
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from code_atlas.change_intelligence import prepare_change

PIN = os.environ.get("CAEXT_HISTORICAL_CODE_ATLAS_PIN", "b024dcd2c533bf00e6f6926863b48472af1c215a")
WORKERS = max(1, min(18, int(os.environ.get("CAEXT_WORKERS", "18"))))


@dataclass(frozen=True)
class HistoricalCase:
    case_id: str
    slug: str
    url: str
    stack: str
    commit: str
    parent: str
    target: str
    request: str
    mode: str = "existing_target"


CASES = (
    HistoricalCase(
        "GO", "spf13/cobra", "https://github.com/spf13/cobra.git", "Go library / CLI",
        "24ada7fe71e3a3a8741dd52e0a7fc3b97450535a", "680936a2200be363c61feda8cd29287f0726a48c",
        "command.go",
        "Prevent the default completion command from breaking root commands that accept arguments, without touching unrelated command behavior.",
    ),
    HistoricalCase(
        "JAVA", "spring-projects/spring-petclinic", "https://github.com/spring-projects/spring-petclinic.git",
        "Java / Spring application",
        "bb37aad8c332264723817d855e8b3b96b7c392bc", "0f6e8614047bd74cf6223b4d8a858d2ed2824f8a",
        "src/main/java/org/springframework/samples/petclinic/owner/OwnerController.java",
        "Normalize surrounding whitespace in owner surname search and preserve the existing owner flow.",
    ),
    HistoricalCase(
        "MIXED", "pybind/pybind11", "https://github.com/pybind/pybind11.git", "C++ / Python mixed-language library",
        "0599909bfebc7d3440cc1fda3144e437e6ade056", "856a3485ca5b704fc7614e89540670cb553e6e4f",
        "include/pybind11/detail/function_ref.h",
        "Allow function_ref to return a copyable type with a deleted move constructor under guaranteed copy elision.",
    ),
    HistoricalCase(
        "NEWPATH", "kubernetes/examples", "https://github.com/kubernetes/examples.git", "Kubernetes YAML / IaC examples",
        "6227892d666343a741fe4db9ae0425fff0dd1e28", "083633d483c903121d10a671ebc771f155c0b798",
        "nginx-platform-app/deployment.yml",
        "Add a production-style Nginx platform deployment example without guessing files that do not exist in the parent snapshot.",
        "new_path",
    ),
)


def iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def jdump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sh(cmd: list[str], *, cwd: Path | None = None, check: bool = True, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
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


def clone_history(case: HistoricalCase, root: Path) -> Path:
    dest = root / f"repo_{case.case_id.lower()}"
    sh(["git", "init", str(dest)])
    git(dest, "remote", "add", "origin", case.url)
    git(dest, "fetch", "--depth=1", "--no-tags", "origin", case.parent)
    git(dest, "fetch", "--depth=1", "--no-tags", "origin", case.commit)
    git(dest, "checkout", "--detach", case.parent)
    if git_text(dest, "rev-parse", "HEAD") != case.parent:
        raise RuntimeError(f"PARENT_PIN_MISMATCH:{case.slug}")
    if git(dest, "cat-file", "-e", f"{case.commit}^{{commit}}", check=False).returncode != 0:
        raise RuntimeError(f"HISTORICAL_COMMIT_MISSING:{case.slug}")
    return dest


def parse_name_status(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            rows.append({"status": status, "oldPath": parts[1], "path": parts[2]})
        elif len(parts) >= 2:
            rows.append({"status": status, "path": parts[1]})
        else:
            raise RuntimeError(f"UNPARSEABLE_NAME_STATUS:{raw}")
    return rows


def actual_diff(repo: Path, case: HistoricalCase) -> tuple[list[dict[str, str]], set[str], str]:
    proc = git(repo, "diff", "--name-status", "--find-renames", case.parent, case.commit)
    rows = parse_name_status(proc.stdout)
    paths = {row["path"] for row in rows}
    return rows, paths, proc.stdout


def policy(case: HistoricalCase) -> dict[str, Any]:
    return {
        "schemaVersion": "code_atlas_customer_policy.v1",
        "policyId": f"caext-historical-{case.case_id.lower()}",
        "version": "1",
        "protectedPaths": [],
        "requiredAuthorities": [],
        "requiredTests": [],
        "requiredReviews": [],
        "forbiddenOperations": ["push", "deploy", "database-mutation", "dependency-install", "process-kill", "port-change"],
        "domainEvidenceRequirements": [],
        "impactThresholds": {},
    }


def stable_prepare_view(report: dict[str, Any]) -> dict[str, Any]:
    findings = []
    for row in report.get("findings") or []:
        if isinstance(row, dict):
            findings.append({
                "code": row.get("code"),
                "severity": row.get("severity"),
                "status": row.get("status"),
            })
    model = report.get("changeModel") or {}
    radius = model.get("impactRadius") or {}
    pack = report.get("authorityPack") or {}
    return {
        "decision": report.get("decision"),
        "intent": model.get("intent"),
        "targets": sorted(str(x) for x in model.get("targets") or []),
        "impactChanged": sorted(str(x) for x in radius.get("changed") or []),
        "impactImpacted": sorted(str(x) for x in radius.get("impacted") or []),
        "protectedScope": sorted(str(x) for x in model.get("protectedScope") or []),
        "allowedScope": sorted(str(x) for x in model.get("allowedScope") or []),
        "requiredEvidence": sorted(digest(x) for x in model.get("requiredEvidence") or []),
        "authorityPackIssued": bool(pack),
        "findings": sorted(findings, key=lambda x: (str(x.get("code")), str(x.get("severity")), str(x.get("status")))),
    }


def run_prepare(repo: Path, case: HistoricalCase, out: Path) -> dict[str, Any]:
    return prepare_change(
        repo,
        change_request=case.request,
        target_paths=[case.target],
        output_root=out,
        policy=policy(case),
        domain="runtime",
        intent="VERIFY",
        workers=WORKERS,
    )


def pct(numerator: int, denominator: int) -> float | str:
    if denominator == 0:
        return "NOT_APPLICABLE"
    return round(100.0 * numerator / denominator, 2)


def score_existing(case: HistoricalCase, report: dict[str, Any], actual: set[str]) -> dict[str, Any]:
    model = report.get("changeModel") or {}
    radius = model.get("impactRadius") or {}
    predicted = {str(x) for x in radius.get("impacted") or []}
    intersection = actual & predicted
    false_negatives = actual - predicted
    false_positives = predicted - actual
    actual_companions = actual - {case.target}
    predicted_companions = predicted - {case.target}
    companion_hits = actual_companions & predicted_companions
    return {
        "decision": str(report.get("decision") or "UNKNOWN"),
        "target": case.target,
        "actualChangedCount": len(actual),
        "predictedImpactCount": len(predicted),
        "intersectionCount": len(intersection),
        "recallPct": pct(len(intersection), len(actual)),
        "precisionPct": pct(len(intersection), len(predicted)),
        "actualCompanionCount": len(actual_companions),
        "predictedCompanionCount": len(predicted_companions),
        "companionRecallPct": pct(len(companion_hits), len(actual_companions)),
        "actualChanged": sorted(actual),
        "predictedImpact": sorted(predicted),
        "hits": sorted(intersection),
        "falseNegatives": sorted(false_negatives),
        "falsePositives": sorted(false_positives),
        "accuracyInterpretation": "MEASURED_NOT_GATED",
    }


def score_new_path(case: HistoricalCase, report: dict[str, Any], actual: set[str], target_exists_in_parent: bool) -> dict[str, Any]:
    decision = str(report.get("decision") or "UNKNOWN")
    pack = report.get("authorityPack")
    accepted = decision in {"BLOCKED", "UNKNOWN"}
    return {
        "decision": decision,
        "target": case.target,
        "targetExistsInParent": target_exists_in_parent,
        "actualChangedCount": len(actual),
        "actualChanged": sorted(actual),
        "authorityPackIssued": bool(pack),
        "expectedDecision": ["BLOCKED", "UNKNOWN"],
        "behaviorPass": accepted and not bool(pack),
        "recallPct": "NOT_APPLICABLE_NEW_PATH_MISSING_IN_PARENT",
        "precisionPct": "NOT_APPLICABLE_NEW_PATH_MISSING_IN_PARENT",
        "companionRecallPct": "NOT_APPLICABLE_NEW_PATH_MISSING_IN_PARENT",
        "accuracyInterpretation": "FAIL_CLOSED_BEHAVIOR_ONLY",
    }


def self_test() -> None:
    parsed = parse_name_status("M\ta.py\nA\tb.py\nR100\told.py\tnew.py\n")
    assert parsed == [
        {"status": "M", "path": "a.py"},
        {"status": "A", "path": "b.py"},
        {"status": "R100", "oldPath": "old.py", "path": "new.py"},
    ]
    case = HistoricalCase("T", "o/r", "x", "test", "c", "p", "a.py", "req")
    report = {"decision": "PASS", "changeModel": {"impactRadius": {"impacted": ["a.py", "test_a.py", "extra.py"]}}}
    score = score_existing(case, report, {"a.py", "test_a.py"})
    assert score["recallPct"] == 100.0
    assert score["precisionPct"] == 66.67
    assert score["companionRecallPct"] == 100.0
    missing = score_new_path(case, {"decision": "BLOCKED", "authorityPack": None}, {"a.py"}, False)
    assert missing["behaviorPass"] is True
    print("PASS_CAEXT_HISTORICAL_SELF_TEST")


def run(output_root: Path, hitech_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    if git(hitech_root, "diff", "--quiet", PIN, "--", "tools/code-atlas/src/code_atlas", check=False).returncode != 0:
        raise RuntimeError("CODE_ATLAS_CORE_DIFFERS_FROM_GOVERNED_PIN")

    tmp = Path(tempfile.mkdtemp(prefix="caext_hist_"))
    stage = tmp / "package"
    stage.mkdir(parents=True)
    started = time.perf_counter()
    state: dict[str, Any] = {
        "schemaVersion": "caext_historical_real_diff.v1",
        "classification": "VERIFY / EXTERNAL EVIDENCE / HISTORICAL REAL-DIFF",
        "codeAtlasCommit": PIN,
        "workersConfigured": WORKERS,
        "workerPeak": "NOT_MEASURED",
        "startedAt": iso(),
        "cases": [],
        "failures": [],
        "accuracyThresholds": "NONE_BY_DESIGN",
        "productionCertified": False,
    }

    try:
        for case in CASES:
            case_started = time.perf_counter()
            case_stage = stage / f"case_{case.case_id.lower()}"
            case_stage.mkdir(parents=True)
            repo = clone_history(case, tmp)
            before = identity(repo)
            if before["dirty"]:
                raise RuntimeError(f"DIRTY_PARENT_CLONE:{case.slug}")
            rows, actual, raw_diff = actual_diff(repo, case)
            (case_stage / "actual_name_status.txt").write_text(raw_diff, encoding="utf-8")
            jdump(case_stage / "actual_diff.json", rows)

            target_exists = (repo / case.target).is_file()
            if case.mode == "existing_target" and not target_exists:
                raise RuntimeError(f"EXPECTED_TARGET_MISSING_IN_PARENT:{case.slug}:{case.target}")
            if case.mode == "existing_target" and case.target not in actual:
                raise RuntimeError(f"TARGET_NOT_CHANGED_BY_HISTORICAL_COMMIT:{case.slug}:{case.target}")
            if case.mode == "new_path" and target_exists:
                raise RuntimeError(f"NEW_PATH_ALREADY_EXISTS_IN_PARENT:{case.slug}:{case.target}")
            if case.mode == "new_path" and case.target not in actual:
                raise RuntimeError(f"NEW_PATH_NOT_ADDED_BY_HISTORICAL_COMMIT:{case.slug}:{case.target}")

            t0 = time.perf_counter()
            prepare1 = run_prepare(repo, case, case_stage / "prepare1")
            prepare1_seconds = round(time.perf_counter() - t0, 4)
            t0 = time.perf_counter()
            prepare2 = run_prepare(repo, case, case_stage / "prepare2")
            prepare2_seconds = round(time.perf_counter() - t0, 4)
            jdump(case_stage / "prepare1.json", prepare1)
            jdump(case_stage / "prepare2.json", prepare2)

            stable1 = stable_prepare_view(prepare1)
            stable2 = stable_prepare_view(prepare2)
            repeatable = stable1 == stable2
            repeatability = {
                "stable": repeatable,
                "fingerprint1": digest(stable1),
                "fingerprint2": digest(stable2),
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

            after = identity(repo)
            read_only = before["head"] == after["head"] and before["tree"] == after["tree"] and not after["dirty"]
            jdump(case_stage / "identity_before.json", before)
            jdump(case_stage / "identity_after.json", after)

            case_result = {
                "caseId": case.case_id,
                "repository": case.slug,
                "stack": case.stack,
                "mode": case.mode,
                "parent": case.parent,
                "parentTree": before["tree"],
                "commit": case.commit,
                "commitTree": git_text(repo, "rev-parse", f"{case.commit}^{{tree}}"),
                "target": case.target,
                "decision": score["decision"],
                "repeatability": repeatable,
                "readOnly": read_only,
                "behaviorPass": behavior_pass,
                "prepare1Seconds": prepare1_seconds,
                "prepare2Seconds": prepare2_seconds,
                "totalSeconds": round(time.perf_counter() - case_started, 4),
                "workerPeak": "NOT_MEASURED",
                **{k: v for k, v in score.items() if k not in {"decision", "target", "behaviorPass"}},
            }
            state["cases"].append(case_result)

            if not repeatable:
                state["failures"].append({"caseId": case.case_id, "class": "EVIDENCE_REPEATABILITY_FAILURE"})
            if not read_only:
                state["failures"].append({"caseId": case.case_id, "class": "EXTERNAL_READ_ONLY_VIOLATION"})
            if case.mode == "new_path" and not behavior_pass:
                state["failures"].append({
                    "caseId": case.case_id,
                    "class": "NEW_PATH_FAIL_CLOSED_VIOLATION",
                    "decision": score["decision"],
                    "authorityPackIssued": score["authorityPackIssued"],
                })

        mechanics_ok = not state["failures"]
        state["recommendedClassification"] = (
            "VERIFY_HISTORICAL_EVIDENCE_CAPTURED" if mechanics_ok else "BLOCKED_HISTORICAL_EVIDENCE_QUALITY"
        )

        rows = state["cases"]
        json_rows = []
        for row in rows:
            json_rows.append({k: v for k, v in row.items()})
        jdump(stage / "02_HISTORICAL_MATRIX.json", json_rows)
        fields = sorted({k for row in rows for k in row if k not in {"actualChanged", "predictedImpact", "hits", "falseNegatives", "falsePositives"}})
        with (stage / "01_HISTORICAL_MATRIX.csv").open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(row.get(k), ensure_ascii=False) if isinstance(row.get(k), (dict, list)) else row.get(k) for k in fields})

        accuracy_lines = ["# HISTORICAL REAL-DIFF ACCURACY", "", "No accuracy threshold is used as a pass/fail gate. Low precision or recall is evidence.", ""]
        for row in rows:
            accuracy_lines.extend([
                f"## {row['caseId']} — {row['repository']}",
                f"- Mode: `{row['mode']}`",
                f"- Decision: `{row['decision']}`",
                f"- Recall: `{row.get('recallPct')}`",
                f"- Precision: `{row.get('precisionPct')}`",
                f"- Companion recall: `{row.get('companionRecallPct')}`",
                f"- False negatives: `{json.dumps(row.get('falseNegatives', []), ensure_ascii=False)}`",
                f"- False positives: `{json.dumps(row.get('falsePositives', []), ensure_ascii=False)}`",
                "",
            ])
        md(stage / "HISTORICAL_ACCURACY.md", "\n".join(accuracy_lines))

        md(stage / "00_EXECUTIVE_SUMMARY.md", f"""# CODE ATLAS HISTORICAL REAL-DIFF V1

- Cases: **{len(rows)}**
- Existing-target historical diffs: **3**
- Missing-parent new-path case: **1**
- Repeatability: **{'PASS' if all(r['repeatability'] for r in rows) else 'BLOCKED'}**
- External originals read-only: **{'PASS' if all(r['readOnly'] for r in rows) else 'BLOCKED'}**
- Kubernetes new-path fail-closed behavior: **{'PASS' if next(r for r in rows if r['caseId']=='NEWPATH')['behaviorPass'] else 'BLOCKED'}**
- Accuracy thresholds: **NONE BY DESIGN**
- Recommended classification: **{state['recommendedClassification']}**
- Worker peak: **NOT_MEASURED**

## Interpretation
This gate compares Code Atlas PREPARE impact at immutable historical parent commits with the paths that actually changed in the next real commit. Precision/recall values measure evidence quality; they do not authorize source changes by themselves.

The Kubernetes case is intentionally different: its explicit target did not exist in the parent snapshot, so correct behavior is fail-closed `BLOCKED` or `UNKNOWN` without an authority pack. Recall/precision are not meaningful for that case.

This evidence does not certify arbitrary repositories, complete multi-stack dependency understanding, production, enterprise IAM/security, hosted multi-tenant, legal/privacy, or paid-pilot readiness.
""")
        md(stage / "NEXT_GATE.md", "# NEXT GATE\n\nIf mechanics are PASS, adjudicate the measured false positives/false negatives as bounded evidence, then proceed to human/agent usefulness testing. Do not patch core from low accuracy alone.\n")
    except Exception as exc:
        state["failures"].append({"class": "HARNESS_OR_ENVIRONMENT_FAILURE", "error": repr(exc), "traceback": traceback.format_exc()})
        state["recommendedClassification"] = "BLOCKED"
        md(stage / "00_EXECUTIVE_SUMMARY.md", "# CODE ATLAS HISTORICAL REAL-DIFF V1\n\n**BLOCKED / INCOMPLETE.** See run_state.json.\n")
    finally:
        state["finishedAt"] = iso()
        state["elapsedSeconds"] = round(time.perf_counter() - started, 4)
        jdump(stage / "run_state.json", state)
        files = []
        for path in sorted(stage.rglob("*")):
            if path.is_file() and path.name != "EVIDENCE_INDEX.json":
                files.append({
                    "path": path.relative_to(stage).as_posix(),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "bytes": path.stat().st_size,
                })
        jdump(stage / "EVIDENCE_INDEX.json", {
            "schemaVersion": "caext_historical_evidence_index.v1",
            "generatedAt": iso(),
            "codeAtlasCommit": PIN,
            "files": files,
        })
        out = output_root / f"caexthist_{datetime.now().astimezone().strftime('%d%m_%H%M%S')}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(stage).as_posix())
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Code Atlas historical real-diff evidence V1")
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
    print(f"CAEXT_HISTORICAL_RESULT={out}")
    with zipfile.ZipFile(out) as archive:
        state = json.loads(archive.read("run_state.json").decode("utf-8"))
    print(f"CAEXT_HISTORICAL_CLASSIFICATION={state.get('recommendedClassification')}")
    return 0 if state.get("recommendedClassification") == "VERIFY_HISTORICAL_EVIDENCE_CAPTURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
