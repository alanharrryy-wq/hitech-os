from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


WATCH_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = WATCH_ROOT / "SYNC_SENTINEL_WATCH_CONTRACT.json"
LEVELS = {"NONE": 0, "SCAN": 1, "CERTIFY": 2}
SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:token|secret|password|cookie)\s*[:=]\s*)[^\s,;]+"),
]


def load_contract() -> dict[str, Any]:
    data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if data.get("schemaVersion") != "prisma.sync-sentinel.watch.v1":
        raise RuntimeError("WATCH_CONTRACT_SCHEMA_INVALID")
    if data.get("policy", {}).get("unknownFailsClosed") is not True:
        raise RuntimeError("WATCH_CONTRACT_UNKNOWN_MUST_FAIL_CLOSED")
    return data


def normalize_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def _matches(path: str, pattern: str) -> bool:
    return fnmatch.fnmatchcase(path, pattern)


def classify_paths(paths: list[str], contract: dict[str, Any] | None = None) -> dict[str, Any]:
    cfg = contract or load_contract()
    normalized = sorted({normalize_path(path) for path in paths if normalize_path(path)})
    certify_patterns = [str(v) for v in cfg.get("certifyPatterns", [])]
    scan_patterns = [str(v) for v in cfg.get("scanPatterns", [])]
    matches: list[dict[str, str]] = []
    impact = "NONE"
    wake_files: list[str] = []
    for path in normalized:
        matched_certify = next((pattern for pattern in certify_patterns if _matches(path, pattern)), None)
        if matched_certify:
            impact = "CERTIFY"
            wake_files.append(path)
            matches.append({"path": path, "level": "CERTIFY", "pattern": matched_certify})
            continue
        matched_scan = next((pattern for pattern in scan_patterns if _matches(path, pattern)), None)
        if matched_scan:
            if LEVELS[impact] < LEVELS["SCAN"]:
                impact = "SCAN"
            wake_files.append(path)
            matches.append({"path": path, "level": "SCAN", "pattern": matched_scan})
    return {
        "schemaVersion": "prisma.sync-sentinel.watch-classification.v1",
        "impact": impact,
        "changedFiles": normalized,
        "wakeFiles": sorted(set(wake_files)),
        "matches": matches,
        "productionCertified": False,
    }


def _git(repo: Path, *args: str) -> str:
    cp = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    if cp.returncode:
        raise RuntimeError(f"WATCH_GIT_FAILED:{' '.join(args)}:{cp.stderr.strip()[:500]}")
    return cp.stdout.strip()


def diff_paths(repo: Path, base: str, head: str) -> list[str]:
    if not base or set(base) == {"0"}:
        parents = _git(repo, "rev-list", "--parents", "-n", "1", head).split()
        if len(parents) < 2:
            return [line for line in _git(repo, "show", "--pretty=format:", "--name-only", head).splitlines() if line.strip()]
        base = parents[1]
    return [line for line in _git(repo, "diff", "--name-only", base, head, "--").splitlines() if line.strip()]


def _sanitize(value: str) -> str:
    text = value
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text[:4000]


def _json_objects(text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    rows: list[dict[str, Any]] = []
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def _stage_payload(log_path: Path) -> dict[str, Any] | None:
    if not log_path.is_file():
        return None
    text = log_path.read_text(encoding="utf-8", errors="replace")
    candidates = _json_objects(text)
    # A stage report may contain nested check objects that also have a `verdict`.
    # Prefer the enclosing report contract (`status` or `checks`) before considering
    # a lone check. Otherwise a final nested PASS can mask the parent FAIL.
    for value in reversed(candidates):
        if "status" in value or "checks" in value:
            return value
    for value in reversed(candidates):
        if "verdict" in value:
            return value
    return None


def _first_failed_check(payload: dict[str, Any]) -> tuple[list[str], dict[str, Any] | None, list[str]]:
    rows = payload.get("checks")
    if not isinstance(rows, list):
        return [], None, []
    passed: list[str] = []
    failed: dict[str, Any] | None = None
    not_established: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        verdict = str(row.get("verdict") or "UNKNOWN").upper()
        cid = str(row.get("id") or "UNKNOWN")
        if failed is None and verdict == "PASS":
            passed.append(cid)
            continue
        if failed is None:
            failed = row
        else:
            not_established.append(cid)
    return passed, failed, not_established


def _stage_status(stage: str, log_path: Path, payload: dict[str, Any] | None) -> str:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if stage == "self-test" and "PASS_SYNC_SENTINEL_SELF_TEST" in text:
        return "PASS_SYNC_SENTINEL_SELF_TEST"
    return str((payload or {}).get("status") or (payload or {}).get("verdict") or "UNKNOWN")


def build_summary(classification: dict[str, Any], logs_dir: Path) -> str:
    stage_names = ["self-test", "scan", "diagnose", "certify"]
    lines = [
        "## PRISMA Sync Sentinel Watch",
        "",
        f"- **Impact:** `{classification.get('impact', 'UNKNOWN')}`",
        f"- **HEAD:** `{classification.get('head', 'unknown')}`",
        f"- **Base:** `{classification.get('base', 'unknown')}`",
        f"- **Event:** `{classification.get('event', 'unknown')}`",
        "- **productionCertified:** `false`",
    ]
    wake = classification.get("wakeFiles") or []
    lines.append(f"- **Wake files:** `{len(wake)}`")
    if wake:
        lines.extend(["", "### Files that woke Sentinel", ""])
        lines.extend(f"- `{path}`" for path in wake[:80])

    first_stage_failure: tuple[str, dict[str, Any] | None, Path] | None = None
    stage_rows: list[tuple[str, str, dict[str, Any] | None]] = []
    for stage in stage_names:
        log_path = logs_dir / f"{stage}.log"
        if not log_path.is_file():
            stage_rows.append((stage, "NOT_RUN", None))
            continue
        payload = _stage_payload(log_path)
        status = _stage_status(stage, log_path, payload)
        upper = status.upper()
        stage_rows.append((stage, status, payload))
        if first_stage_failure is None and not (upper.startswith("PASS") or upper == "PASS"):
            first_stage_failure = (stage, payload, log_path)

    lines.extend(["", "### Stage timeline", "", "| Stage | Result |", "|---|---|"])
    for stage, status, _ in stage_rows:
        lines.append(f"| `{stage}` | `{_sanitize(status)}` |")

    if first_stage_failure:
        stage, payload, log_path = first_stage_failure
        lines.extend(["", "### Causal failure localization", "", f"- **Failed stage:** `{stage}`"])
        if payload:
            passed, failed, not_established = _first_failed_check(payload)
            if passed:
                lines.append(f"- **Passed before failure:** `{', '.join(passed)}`")
            if failed:
                lines.append(f"- **Fault zone/check:** `{_sanitize(str(failed.get('id') or 'UNKNOWN'))}`")
                lines.append(f"- **Verdict:** `{_sanitize(str(failed.get('verdict') or 'UNKNOWN'))}`")
                lines.append(f"- **Cause:** {_sanitize(str(failed.get('summary') or failed.get('message') or 'No structured cause'))}")
            if not_established:
                lines.append(f"- **Not established after failure:** `{', '.join(not_established)}`")
            facts = payload.get("facts") if isinstance(payload.get("facts"), dict) else {}
            for key in ("sourceDrift", "cleanupPass", "orphanProcesses", "liveDbTouched"):
                value = payload.get(key, facts.get(key))
                if value is not None:
                    lines.append(f"- **{key}:** `{value}`")
            if payload.get("secretFindings") is not None:
                lines.append(f"- **secretFindings:** `{payload.get('secretFindings')}`")
        else:
            tail = "\n".join(log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-20:])
            lines.extend(["- **Fault zone/check:** `UNSTRUCTURED_STAGE_FAILURE`", "", "```text", _sanitize(tail), "```"])
    else:
        lines.extend(["", "PASS is intentionally quiet: evidence is retained without opening issues or posting automated PR noise."])
    return "\n".join(lines) + "\n"


def cmd_classify(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    contract = load_contract()
    event = args.event
    forced = event in {"schedule", "workflow_dispatch"}
    if args.paths_file:
        paths = Path(args.paths_file).read_text(encoding="utf-8").splitlines()
    elif forced:
        paths = []
    else:
        paths = diff_paths(repo, args.base, args.head)
    result = classify_paths(paths, contract)
    if forced:
        result["impact"] = "CERTIFY"
        result["matches"].append({"path": "<event>", "level": "CERTIFY", "pattern": f"forced:{event}"})
    result.update({
        "event": event,
        "base": args.base,
        "head": args.head or _git(repo, "rev-parse", "HEAD"),
        "weeklySchedule": contract.get("weeklySchedule"),
        "retentionDays": contract.get("artifacts", {}).get("retentionDays"),
    })
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    classification = json.loads(Path(args.classification).read_text(encoding="utf-8"))
    summary = build_summary(classification, Path(args.logs_dir))
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if target:
        with Path(target).open("a", encoding="utf-8") as handle:
            handle.write(summary)
    else:
        print(summary, end="")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PRISMA Sync Sentinel event-driven impact classifier")
    sub = p.add_subparsers(dest="command", required=True)
    classify = sub.add_parser("classify")
    classify.add_argument("--repo", default=".")
    classify.add_argument("--event", required=True)
    classify.add_argument("--base", default="")
    classify.add_argument("--head", default="")
    classify.add_argument("--paths-file", default=None)
    classify.add_argument("--output", default=None)
    classify.set_defaults(func=cmd_classify)
    summarize = sub.add_parser("summarize")
    summarize.add_argument("--classification", required=True)
    summarize.add_argument("--logs-dir", required=True)
    summarize.set_defaults(func=cmd_summarize)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:
        print(json.dumps({
            "status": "BLOCKED_SYNC_SENTINEL_WATCH",
            "faultZone": "WATCH_CLASSIFICATION",
            "error": _sanitize(f"{type(exc).__name__}: {exc}"),
            "productionCertified": False,
        }, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
