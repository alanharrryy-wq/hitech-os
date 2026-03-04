from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import secrets
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any

PASS = "PASS"
BLOCKED = "BLOCKED"

CODEX_IDS: tuple[str, ...] = (
    "A_core",
    "B_tooling",
    "C_features",
    "D_validation",
    "Z_aggregator",
)

RUN_ID_NEW_RE = re.compile(r"^(?P<day>\d{8})_(?P<time>\d{6})_(?P<rand>[A-Z0-9]{4})$")
RUN_ID_OLD_RE = re.compile(r"^(?P<day>\d{8})_(?P<seq>\d+)$")
PACK_SECTION_RE = re.compile(r"^===\s+(?P<worker>[A-Za-z0-9_]+)\s+PROMPT\s+===$")
PACK_WORKER_HEADERS: dict[str, str] = {
    "A_core": "=== A_core PROMPT ===",
    "B_tooling": "=== B_tooling PROMPT ===",
    "C_features": "=== C_features PROMPT ===",
    "D_validation": "=== D_validation PROMPT ===",
    "Z_aggregator": "=== Z_aggregator PROMPT ===",
}

REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_DIR = REPO_ROOT / "tools" / "codex"
PROMPT_ZIPS_DIR = CODEX_DIR / "prompt_zips"
PROMPTS_ROOT = CODEX_DIR / "prompts"
RUNS_ROOT = CODEX_DIR / "runs"

HEADER_SCAN_LINES = 40
DOC_WORKERS: tuple[str, ...] = CODEX_IDS[:-1]
WORKER_BUNDLE_REQUIRED: tuple[str, ...] = (
    "STATUS.json",
    "SUMMARY.md",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "SUGGESTIONS.md",
    "SCOPE_LOCK.json",
    "HANDOFF_NOTE.json",
    "LOGS/INDEX.json",
    "CODEX_OUTPUT.txt",
    "SELF_EVAL_REPORT.json",
    "SANCTION_SCORE.json",
    "SELF_CORRECTION_LOG.jsonl",
    "DONE.marker",
)
AGGREGATOR_FINAL_REPORT_REL = "FILES/FINAL_REPORT.txt"
ROOT_FINAL_REPORT = REPO_ROOT / "FINAL_REPORT.md"
EVOLUTIONARY_REQUIRED_FILES: tuple[str, ...] = (
    "SELF_EVAL_REPORT.json",
    "SANCTION_SCORE.json",
    "SELF_CORRECTION_LOG.jsonl",
)
EVOLUTIONARY_MAX_ATTEMPTS = 3
EVOLUTIONARY_RETRY_SECONDS = 0.5
EVOLUTIONARY_ENGINE = REPO_ROOT / "tools" / "hos" / "guardrails" / "evolutionary_sanctions.py"
EVOLUTIONARY_POLICY = REPO_ROOT / "tools" / "hos" / "guardrails" / "policy.json"
REWORK_POLICY_PATH = REPO_ROOT / "tools" / "codex" / "dispatch" / "rework_policy.json"
REWORK_TASK_BANK_PATH = REPO_ROOT / "tools" / "codex" / "dispatch" / "rework_task_bank.json"
REWORK_MARKER_BEGIN = "### REWORK_INSTRUCTION_BEGIN"
REWORK_MARKER_END = "### REWORK_INSTRUCTION_END"
REWORK_DEFAULT_MAX_CYCLES = 3
REWORK_DEFAULT_LOC_INCREMENT = 5000


def _prompt_contract_header(run_id: str, worker: str) -> str:
    done_marker = f"tools/codex/runs/{run_id}/{worker}/DONE.marker"
    lines = [
        f"RUN_ID: {run_id}",
        f"CODEX_ID: {worker}",
        "SESSION_POLICY: CLEAN_START_REQUIRED",
        "SESSION_RECOVERY: IF_HISTORY_PRESENT_IGNORE_PRIOR_CONTEXT_AND_RESTATE_SCOPE",
        "AUTO_REPORT_REQUIRED: true",
        (
            "AUTO_REPORT_ARTIFACTS: "
            "STATUS.json,SUMMARY.md,FILES_CHANGED.json,DIFF.patch,SUGGESTIONS.md,"
            "SCOPE_LOCK.json,HANDOFF_NOTE.json,LOGS/INDEX.json,CODEX_OUTPUT.txt,"
            "SELF_EVAL_REPORT.json,SANCTION_SCORE.json,SELF_CORRECTION_LOG.jsonl"
        ),
        "PRE_DONE_EVOLUTIONARY_CHECK_REQUIRED: true",
        "PRE_DONE_EVOLUTIONARY_MODE: NON_BLOCKING_AUTOSANCTION_RETRY",
        (
            "PRE_DONE_EVOLUTIONARY_ARTIFACTS: "
            "SELF_EVAL_REPORT.json,SANCTION_SCORE.json,SELF_CORRECTION_LOG.jsonl"
        ),
        (
            "PRE_DONE_EVOLUTIONARY_COMMAND: "
            f"python tools/hos/guardrails/evolutionary_sanctions.py --repo . --run-id {run_id} --worker-id {worker} "
            f"--bundle-dir tools/codex/runs/{run_id}/{worker}"
        ),
        "REWORK_AUTONOMY_REQUIRED: true",
        f"REWORK_REQUEST_PATH: tools/codex/runs/{run_id}/{worker}/REWORK_REQUEST.json",
        f"REWORK_MAX_CYCLES: {REWORK_DEFAULT_MAX_CYCLES}",
        f"REWORK_LOC_INCREMENT: {REWORK_DEFAULT_LOC_INCREMENT}",
        "AUTO_RECOVERY_REQUIRED: true",
        f"DONE_MARKER_PATH: {done_marker}",
    ]
    if worker in {"B_tooling", "B_worker"}:
        lines.extend(
            [
                "VISUAL_BASELINE_OWNER: true",
                "VISUAL_BASELINE_UPDATE_DEFAULT: true",
                "VISUAL_BASELINE_COMMAND: python tools/hos/visual/cli_visual.py --suite keystone --update-baseline",
            ]
        )
    if worker in {"Z_aggregator", "Z_integrator"}:
        lines.extend(
            [
                "LEDGER_WATCH_REQUIRED: true",
                f"LEDGER_WATCH_COMMAND: python -m tools.codex.factory watch --run-id {run_id}",
                f"LEDGER_EVENTS_COMMAND: python -m tools.codex.factory ledger --run-id {run_id} --raw-events --limit 200",
                "START_WORK_AFTER_WORKERS_DONE: true",
            ]
        )
    return "\n".join(lines).strip() + "\n\n"


def _apply_prompt_contract(run_id: str, worker: str, prompt_text: str) -> str:
    body = prompt_text.strip()
    header = _prompt_contract_header(run_id, worker)
    if not body:
        return header
    return header + body + "\n"


def _rotate_existing_prompt_dir(prompt_dir: Path) -> tuple[bool, str]:
    if not prompt_dir.exists():
        return True, ""
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = prompt_dir.with_name(f"{prompt_dir.name}__stale_{stamp}")
    try:
        prompt_dir.replace(backup)
        return True, backup.as_posix()
    except OSError:
        try:
            shutil.rmtree(prompt_dir, ignore_errors=True)
            return True, backup.as_posix()
        except OSError as exc:
            return False, str(exc)


def _ensure_worker_run_folders(run_id: str, workers: list[str]) -> None:
    for worker in workers:
        root = RUNS_ROOT / run_id / worker
        root.mkdir(parents=True, exist_ok=True)
        (root / "LOGS").mkdir(parents=True, exist_ok=True)
        (root / "FILES").mkdir(parents=True, exist_ok=True)


def _parse_workers_subset(raw: str | None) -> list[str]:
    if raw is None or not raw.strip():
        return list(CODEX_IDS)

    parsed = [part.strip() for part in str(raw).split(",") if part.strip()]
    if not parsed:
        return list(CODEX_IDS)

    unknown = [worker for worker in parsed if worker not in CODEX_IDS]
    if unknown:
        raise ValueError(f"unknown worker ids in --workers: {','.join(sorted(set(unknown)))}")

    deduped: list[str] = []
    for worker in parsed:
        if worker not in deduped:
            deduped.append(worker)
    return deduped


def _collect_existing_run_ids(day_prefix: str) -> list[str]:
    found: set[str] = set()
    roots = [RUNS_ROOT, PROMPTS_ROOT, PROMPT_ZIPS_DIR]

    for root in roots:
        if not root.exists():
            continue
        if root == PROMPT_ZIPS_DIR:
            entries = [item.stem for item in root.glob("*.zip") if item.is_file()]
        else:
            entries = [item.name for item in root.iterdir()]

        for name in entries:
            is_compatible = bool(RUN_ID_NEW_RE.fullmatch(name) or RUN_ID_OLD_RE.fullmatch(name))
            if is_compatible and str(name).startswith(day_prefix + "_"):
                found.add(name)

    return sorted(found)


def next_run_id(now_utc: dt.datetime | None = None) -> dict[str, Any]:
    now = now_utc or dt.datetime.now(dt.timezone.utc)
    day = now.strftime("%Y%m%d")
    existing = _collect_existing_run_ids(day)
    tries = 0
    run_id = ""
    while tries < 512:
        tries += 1
        stamp = now.strftime("%Y%m%d_%H%M%S")
        random4 = secrets.token_hex(2).upper()
        candidate = f"{stamp}_{random4}"
        if candidate not in existing and not (RUNS_ROOT / candidate).exists():
            run_id = candidate
            break
    if not run_id:
        return {
            "status": BLOCKED,
            "error": "unable to allocate collision-safe run_id after 512 attempts",
            "day": day,
            "existing_for_day": existing,
        }
    return {
        "status": PASS,
        "run_id": run_id,
        "day": day,
        "existing_for_day": existing,
        "source_counts": {
            "runs": len([item for item in existing if (RUNS_ROOT / item).exists()]),
            "prompts": len([item for item in existing if (PROMPTS_ROOT / item).exists()]),
            "prompt_zips": len([item for item in existing if (PROMPT_ZIPS_DIR / f"{item}.zip").exists()]),
        },
    }


def _parse_prompt_pack(text: str) -> tuple[dict[str, str], list[str], list[str]]:
    sections: dict[str, list[str]] = {}
    duplicates: list[str] = []
    seen_headers: list[str] = []
    current_worker: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        match = PACK_SECTION_RE.match(line.strip())
        if match:
            worker = str(match.group("worker")).strip()
            seen_headers.append(worker)
            if worker in sections:
                duplicates.append(worker)
            sections.setdefault(worker, [])
            current_worker = worker
            continue

        if current_worker is not None:
            sections[current_worker].append(raw_line)

    extracted: dict[str, str] = {}
    for worker in CODEX_IDS:
        content_lines = sections.get(worker)
        if content_lines is None:
            continue
        prompt_text = "\n".join(content_lines).strip()
        if prompt_text:
            extracted[worker] = prompt_text + "\n"
        else:
            extracted[worker] = ""

    return extracted, duplicates, seen_headers


def materialize_prompt_pack(run_id: str, pack_path: Path) -> dict[str, Any]:
    prompt_dir = PROMPTS_ROOT / run_id
    expected = expected_prompt_files(run_id)

    if prompt_dir.exists():
        ok, detail = _rotate_existing_prompt_dir(prompt_dir)
        if not ok:
            return {
                "status": BLOCKED,
                "run_id": run_id,
                "pack_path": pack_path.as_posix(),
                "prompt_dir": prompt_dir.as_posix(),
                "error": f"unable to reset existing prompt folder: {detail}",
            }

    if not pack_path.exists() or not pack_path.is_file():
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "pack_path": pack_path.as_posix(),
            "prompt_dir": prompt_dir.as_posix(),
            "error": f"prompts pack missing: {pack_path.as_posix()}",
        }

    try:
        raw_text = pack_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "pack_path": pack_path.as_posix(),
            "prompt_dir": prompt_dir.as_posix(),
            "error": f"prompts pack is not UTF-8: {exc}",
        }

    parsed, duplicates, seen_headers = _parse_prompt_pack(raw_text)
    missing = [worker for worker in CODEX_IDS if worker not in parsed]
    empty = [worker for worker in CODEX_IDS if worker in parsed and not parsed[worker].strip()]
    unknown_sections = sorted(set(seen_headers) - set(CODEX_IDS))

    if missing or duplicates or empty or unknown_sections:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "pack_path": pack_path.as_posix(),
            "prompt_dir": prompt_dir.as_posix(),
            "missing_sections": [PACK_WORKER_HEADERS.get(worker, worker) for worker in missing],
            "duplicate_sections": sorted(set(duplicates)),
            "empty_sections": sorted(empty),
            "unknown_sections": unknown_sections,
            "error": "prompts pack section validation failed",
        }

    prompt_dir.mkdir(parents=True, exist_ok=False)
    written: list[str] = []
    for worker in CODEX_IDS:
        file_name = expected[worker]
        target = prompt_dir / file_name
        resolved_text = parsed[worker].replace("{{RUN_ID}}", run_id)
        resolved_text = _apply_prompt_contract(run_id, worker, resolved_text)
        target.write_text(resolved_text, encoding="utf-8", newline="\n")
        written.append(target.as_posix())

    return {
        "status": PASS,
        "run_id": run_id,
        "pack_path": pack_path.as_posix(),
        "prompt_dir": prompt_dir.as_posix(),
        "written": sorted(written),
    }


def expected_prompt_files(run_id: str) -> dict[str, str]:
    return {worker: f"{worker}_{run_id}.txt" for worker in CODEX_IDS}


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _status_code(status: str) -> int:
    return 0 if str(status).upper() == PASS else 2


def _match_header_value(text: str, key: str) -> tuple[str | None, int | None]:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*[:=]\s*(\S+)\s*$", re.IGNORECASE)
    for index, line in enumerate(text.splitlines()[:HEADER_SCAN_LINES], start=1):
        match = pattern.match(line)
        if match:
            return str(match.group(1)).strip(), index
    return None, None


def validate_run_id(run_id: str) -> list[str]:
    errors: list[str] = []
    match_new = RUN_ID_NEW_RE.fullmatch(run_id)
    match_old = RUN_ID_OLD_RE.fullmatch(run_id)
    if not match_new and not match_old:
        errors.append(
            "RUN_ID must match YYYYMMDD_HHMMSS_RAND4 (example: 20260228_215959_A1B2) "
            "or YYYYMMDD_SEQ (example: 20260228_17)."
        )
        return errors

    if match_new:
        day = str(match_new.group("day"))
        time_part = str(match_new.group("time"))
        try:
            dt.datetime.strptime(day + time_part, "%Y%m%d%H%M%S")
        except ValueError:
            errors.append(f"RUN_ID date/time component is invalid: {day}_{time_part}")
        return errors

    assert match_old is not None
    day_old = str(match_old.group("day"))
    try:
        dt.datetime.strptime(day_old, "%Y%m%d")
    except ValueError:
        errors.append(f"RUN_ID date component is invalid: {day_old}")

    return errors


def extract_prompt_zip(run_id: str) -> dict[str, Any]:
    zip_path = PROMPT_ZIPS_DIR / f"{run_id}.zip"
    prompt_dir = PROMPTS_ROOT / run_id
    expected = expected_prompt_files(run_id)
    expected_names = set(expected.values())

    if prompt_dir.exists():
        ok, detail = _rotate_existing_prompt_dir(prompt_dir)
        if not ok:
            return {
                "status": BLOCKED,
                "run_id": run_id,
                "error": f"unable to reset existing prompt folder: {detail}",
                "zip": zip_path.as_posix(),
                "prompt_dir": prompt_dir.as_posix(),
            }

    if not zip_path.exists():
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "error": f"missing prompt zip: {zip_path.as_posix()}",
            "zip": zip_path.as_posix(),
            "prompt_dir": prompt_dir.as_posix(),
        }

    with zipfile.ZipFile(zip_path) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        by_basename: dict[str, list[zipfile.ZipInfo]] = {}
        for member in members:
            base = Path(member.filename).name
            if not base:
                continue
            by_basename.setdefault(base, []).append(member)

        missing = sorted(name for name in expected_names if name not in by_basename)
        duplicates = sorted(name for name, items in by_basename.items() if name in expected_names and len(items) > 1)
        unexpected = sorted(name for name in by_basename if name not in expected_names)

        if missing or duplicates or unexpected:
            return {
                "status": BLOCKED,
                "run_id": run_id,
                "zip": zip_path.as_posix(),
                "prompt_dir": prompt_dir.as_posix(),
                "missing": missing,
                "duplicates": duplicates,
                "unexpected": unexpected,
                "error": "zip shape validation failed",
            }

        decoded_prompts: dict[str, str] = {}
        for worker in CODEX_IDS:
            name = expected[worker]
            info = by_basename[name][0]
            raw = archive.read(info)
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                return {
                    "status": BLOCKED,
                    "run_id": run_id,
                    "zip": zip_path.as_posix(),
                    "prompt_dir": prompt_dir.as_posix(),
                    "error": f"prompt is not UTF-8: {name} ({exc})",
                }
            decoded_prompts[name] = text

        prompt_dir.mkdir(parents=True, exist_ok=False)
        extracted: list[str] = []
        for worker in CODEX_IDS:
            name = expected[worker]
            target = prompt_dir / name
            resolved_text = _apply_prompt_contract(run_id, worker, decoded_prompts[name])
            target.write_text(resolved_text, encoding="utf-8", newline="\n")
            extracted.append(target.as_posix())

    return {
        "status": PASS,
        "run_id": run_id,
        "zip": zip_path.as_posix(),
        "prompt_dir": prompt_dir.as_posix(),
        "extracted": sorted(extracted),
    }


def _validate_prompt_file(path: Path, run_id: str, worker: str) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    normalized_text = text.replace("\\", "/")

    run_value, run_line = _match_header_value(text, "RUN_ID")
    if run_value is None:
        errors.append("missing RUN_ID header near file top")
    elif run_value != run_id:
        errors.append(f"RUN_ID mismatch in header (line {run_line}): expected {run_id}, got {run_value}")

    codex_value, codex_line = _match_header_value(text, "CODEX_ID")
    if codex_value is None:
        errors.append("missing CODEX_ID header near file top")
    elif codex_value != worker:
        errors.append(f"CODEX_ID mismatch in header (line {codex_line}): expected {worker}, got {codex_value}")

    marker_path = f"tools/codex/runs/{run_id}/{worker}/DONE.marker"
    if marker_path not in normalized_text:
        errors.append(f"missing DONE.marker path instruction: {marker_path}")

    if "SESSION_POLICY: CLEAN_START_REQUIRED" not in text:
        errors.append("missing session hygiene contract: SESSION_POLICY: CLEAN_START_REQUIRED")
    if "AUTO_REPORT_REQUIRED: true" not in text:
        errors.append("missing auto-report contract: AUTO_REPORT_REQUIRED: true")
    if "PRE_DONE_EVOLUTIONARY_CHECK_REQUIRED: true" not in text:
        errors.append("missing pre-DONE evolutionary contract: PRE_DONE_EVOLUTIONARY_CHECK_REQUIRED: true")
    if "REWORK_AUTONOMY_REQUIRED: true" not in text:
        errors.append("missing rework autonomy contract: REWORK_AUTONOMY_REQUIRED: true")
    rework_path = f"tools/codex/runs/{run_id}/{worker}/REWORK_REQUEST.json"
    if rework_path not in normalized_text:
        errors.append(f"missing REWORK_REQUEST path instruction: {rework_path}")

    if worker in {"B_tooling", "B_worker"} and "VISUAL_BASELINE_OWNER: true" not in text:
        errors.append("missing visual baseline owner contract for B worker")
    if worker in {"Z_aggregator", "Z_integrator"} and "LEDGER_WATCH_REQUIRED: true" not in text:
        errors.append("missing ledger watch contract for Z worker")

    return errors


def validate_prompt_folder(run_id: str) -> dict[str, Any]:
    prompt_dir = PROMPTS_ROOT / run_id
    expected = expected_prompt_files(run_id)
    expected_names = set(expected.values())

    if not prompt_dir.exists() or not prompt_dir.is_dir():
        prompt_dir.mkdir(parents=True, exist_ok=True)
        for worker in CODEX_IDS:
            placeholder = (
                "AUTOFIX_PROMPT_PLACEHOLDER: prompt folder was missing and was auto-repaired.\n"
                "Proceed with scoped worker tasks using existing contracts.\n"
            )
            target = prompt_dir / expected[worker]
            target.write_text(_apply_prompt_contract(run_id, worker, placeholder), encoding="utf-8", newline="\n")

    entries = sorted(prompt_dir.iterdir(), key=lambda item: item.name)
    entry_errors: list[str] = []
    file_names: set[str] = set()

    for entry in entries:
        if entry.is_dir():
            if entry.name != "logs":
                entry_errors.append(f"unexpected directory in prompt folder: {entry.name}")
            continue
        file_names.add(entry.name)
        if entry.name not in expected_names:
            entry_errors.append(f"unexpected file in prompt folder: {entry.name}")

    missing_names = sorted(name for name in expected_names if name not in file_names)
    if len(file_names.intersection(expected_names)) != len(expected_names):
        entry_errors.extend(f"missing prompt file: {name}" for name in missing_names)

    file_results: list[dict[str, Any]] = []
    for worker in CODEX_IDS:
        name = expected[worker]
        path = prompt_dir / name
        if not path.exists() or not path.is_file():
            file_results.append({"worker": worker, "file": name, "status": BLOCKED, "errors": ["file missing"]})
            continue
        try:
            current_text = path.read_text(encoding="utf-8")
            if "SESSION_POLICY: CLEAN_START_REQUIRED" not in current_text or "AUTO_REPORT_REQUIRED: true" not in current_text:
                repaired = _apply_prompt_contract(run_id, worker, current_text)
                path.write_text(repaired, encoding="utf-8", newline="\n")
        except OSError:
            pass
        file_errors = _validate_prompt_file(path, run_id, worker)
        file_results.append(
            {
                "worker": worker,
                "file": path.as_posix(),
                "status": PASS if not file_errors else BLOCKED,
                "errors": file_errors,
            }
        )

    blocked = [item for item in file_results if item["status"] != PASS]
    if entry_errors:
        blocked.append({"worker": "<folder>", "status": BLOCKED, "errors": entry_errors})

    return {
        "status": PASS if not blocked else BLOCKED,
        "run_id": run_id,
        "prompt_dir": prompt_dir.as_posix(),
        "entries": [entry.name for entry in entries],
        "results": file_results,
        "errors": entry_errors,
        "blocked": len(blocked),
    }


def _safe_read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _artifacts_present(bundle_root: Path) -> bool:
    return all((bundle_root / rel).exists() for rel in EVOLUTIONARY_REQUIRED_FILES)


def _fallback_sanction_payload(run_id: str, worker: str, bundle_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    files_changed = _safe_read_json(bundle_root / "FILES_CHANGED.json")
    changes = files_changed.get("changes", []) if isinstance(files_changed.get("changes", []), list) else []
    loc_delta = len(changes)
    path_counts: dict[str, int] = {}
    ext_counts: dict[str, int] = {}
    for item in changes:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path", "")).replace("\\", "/").strip()
        if not path:
            continue
        path_counts[path] = path_counts.get(path, 0) + 1
        ext = Path(path).suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    unique_paths = len(path_counts)
    structural_div = _clamp01((len(ext_counts) + unique_paths) / max(1.0, float(loc_delta) * 2.0))
    behavioral_delta = float(max(1, unique_paths))
    vdi = _clamp01((behavioral_delta * structural_div) / max(1.0, float(loc_delta)) * 0.75)
    duplication_ratio = max(0, loc_delta - unique_paths) / max(1.0, float(loc_delta))
    concentration = max(path_counts.values()) / max(1.0, float(loc_delta)) if path_counts else 1.0
    sanction_score = (1.0 - vdi) + (duplication_ratio * concentration)
    sanction_level = "OK" if sanction_score < 0.6 else ("WARN" if sanction_score < 1.2 else "SEVERE")
    computed_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

    report = {
        "run_id": run_id,
        "worker_id": worker,
        "computed_at_utc": computed_at,
        "bundle_dir": bundle_root.as_posix(),
        "loc_delta": int(loc_delta),
        "changed_files_count": int(unique_paths),
        "behavioral_delta": behavioral_delta,
        "structural_diversity": structural_div,
        "duplication_ratio_new": duplication_ratio,
        "file_concentration_ratio": concentration,
        "vdi": vdi,
        "sanction_score": sanction_score,
        "sanction_level": sanction_level,
        "flags": ["AUTOSANCTION_FALLBACK"],
    }
    score = {
        "run_id": run_id,
        "worker_id": worker,
        "computed_at_utc": computed_at,
        "sanction_score": sanction_score,
        "sanction_level": sanction_level,
        "vdi": vdi,
        "loc_delta": int(loc_delta),
        "notes": ["AUTOSANCTION_FALLBACK"],
    }
    return report, score


def _write_fallback_evolutionary_artifacts(run_id: str, worker: str, bundle_root: Path) -> dict[str, Any]:
    report, score = _fallback_sanction_payload(run_id, worker, bundle_root)
    (bundle_root / "SELF_EVAL_REPORT.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    (bundle_root / "SANCTION_SCORE.json").write_text(json.dumps(score, indent=2) + "\n", encoding="utf-8", newline="\n")
    _append_jsonl(
        bundle_root / "SELF_CORRECTION_LOG.jsonl",
        {
            "run_id": run_id,
            "worker_id": worker,
            "computed_at_utc": report["computed_at_utc"],
            "sanction_score": score["sanction_score"],
            "sanction_level": score["sanction_level"],
            "vdi": score["vdi"],
            "loc_delta": score["loc_delta"],
            "flags": ["AUTOSANCTION_FALLBACK"],
        },
    )
    return {
        "sanction_score": score["sanction_score"],
        "sanction_level": score["sanction_level"],
    }


def _read_current_score(bundle_root: Path) -> float | None:
    payload = _safe_read_json(bundle_root / "SANCTION_SCORE.json")
    if "sanction_score" not in payload:
        return None
    return _to_float(payload.get("sanction_score"), 1.0)


def _run_pre_done_evolutionary_non_blocking(run_id: str, worker: str) -> dict[str, Any]:
    bundle_root = RUNS_ROOT / run_id / worker
    bundle_root.mkdir(parents=True, exist_ok=True)
    (bundle_root / "LOGS").mkdir(parents=True, exist_ok=True)
    log_path = bundle_root / "LOGS" / "evolutionary_pre_done.log.jsonl"
    previous_score = _read_current_score(bundle_root)
    best_score = previous_score
    attempts: list[dict[str, Any]] = []
    command = ""

    for attempt in range(1, EVOLUTIONARY_MAX_ATTEMPTS + 1):
        used_engine = False
        rc = 0
        stdout_tail = ""
        stderr_tail = ""
        if EVOLUTIONARY_ENGINE.exists():
            used_engine = True
            cmd = [
                sys.executable or "python",
                EVOLUTIONARY_ENGINE.as_posix(),
                "--repo",
                REPO_ROOT.as_posix(),
                "--run-id",
                run_id,
                "--worker-id",
                worker,
                "--bundle-dir",
                bundle_root.as_posix(),
            ]
            if EVOLUTIONARY_POLICY.exists():
                cmd.extend(["--policy", EVOLUTIONARY_POLICY.as_posix()])
            command = " ".join(cmd)
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                check=False,
                timeout=180,
            )
            rc = int(proc.returncode)
            stdout_tail = (proc.stdout or "").strip()[-300:]
            stderr_tail = (proc.stderr or "").strip()[-300:]

        if (not used_engine) or rc != 0 or not _artifacts_present(bundle_root):
            fallback = _write_fallback_evolutionary_artifacts(run_id, worker, bundle_root)
            score = _to_float(fallback.get("sanction_score"), 1.0)
            level = str(fallback.get("sanction_level", "WARN"))
            source = "fallback"
        else:
            score_payload = _safe_read_json(bundle_root / "SANCTION_SCORE.json")
            score = _to_float(score_payload.get("sanction_score"), 1.0)
            level = str(score_payload.get("sanction_level", "WARN")).upper()
            source = "engine"

        improved = True if best_score is None else score < best_score
        if improved:
            best_score = score
        row = {
            "attempt": attempt,
            "ts_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            "run_id": run_id,
            "worker_id": worker,
            "source": source,
            "engine_used": used_engine,
            "rc": rc,
            "sanction_score": score,
            "sanction_level": level,
            "improved": improved,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
        }
        attempts.append(row)
        _append_jsonl(log_path, row)
        if improved and _artifacts_present(bundle_root):
            break
        if attempt < EVOLUTIONARY_MAX_ATTEMPTS:
            time.sleep(EVOLUTIONARY_RETRY_SECONDS)

    if not _artifacts_present(bundle_root):
        fallback = _write_fallback_evolutionary_artifacts(run_id, worker, bundle_root)
        final_score = _to_float(fallback.get("sanction_score"), 1.0)
        final_level = str(fallback.get("sanction_level", "WARN")).upper()
    else:
        score_payload = _safe_read_json(bundle_root / "SANCTION_SCORE.json")
        final_score = _to_float(score_payload.get("sanction_score"), 1.0)
        final_level = str(score_payload.get("sanction_level", "WARN")).upper()

    trend_down = True
    if previous_score is not None:
        trend_down = final_score < previous_score

    status = "PASS" if _artifacts_present(bundle_root) else "WARN"
    if final_level in {"WARN", "SEVERE"}:
        status = "WARN"
    return {
        "status": status,
        "run_id": run_id,
        "worker_id": worker,
        "attempts": len(attempts),
        "max_attempts": EVOLUTIONARY_MAX_ATTEMPTS,
        "trend_down": trend_down,
        "previous_score": previous_score,
        "final_score": final_score,
        "sanction_level": final_level,
        "artifacts_present": _artifacts_present(bundle_root),
        "command": command,
        "log_path": log_path.as_posix(),
    }


def wait_for_done_markers(
    run_id: str,
    *,
    workers: list[str] | None,
    timeout_seconds: int,
    poll_seconds: float,
) -> dict[str, Any]:
    chosen_workers = workers or list(CODEX_IDS)
    _ensure_worker_run_folders(run_id, chosen_workers)
    start = time.monotonic()
    deadline = start + max(1, int(timeout_seconds))

    per_worker: dict[str, dict[str, Any]] = {
        worker: {
            "worker": worker,
            "marker": (RUNS_ROOT / run_id / worker / "DONE.marker").as_posix(),
            "status": "PENDING",
            "content_ok": False,
            "error": "",
            "evolutionary": {
                "status": "PENDING",
                "attempts": 0,
                "trend_down": False,
                "final_score": None,
                "sanction_level": "",
                "artifacts_present": False,
                "log_path": "",
            },
            "evolutionary_checked": False,
        }
        for worker in chosen_workers
    }

    while time.monotonic() <= deadline:
        all_done = True
        for worker, entry in per_worker.items():
            marker = Path(str(entry["marker"]))
            token = f"DONE {run_id} {worker}"
            if not marker.exists():
                entry["status"] = "PENDING"
                entry["content_ok"] = False
                entry["error"] = "marker missing"
                all_done = False
                continue

            try:
                text = marker.read_text(encoding="utf-8")
            except OSError as exc:
                entry["status"] = "PENDING"
                entry["content_ok"] = False
                entry["error"] = f"marker unreadable: {exc}"
                all_done = False
                continue

            if token not in text:
                entry["status"] = "PENDING"
                entry["content_ok"] = False
                entry["error"] = f"marker content missing token: {token}"
                all_done = False
                continue

            if not bool(entry.get("evolutionary_checked", False)):
                evo_payload = _run_pre_done_evolutionary_non_blocking(run_id, worker)
                entry["evolutionary"] = evo_payload
                entry["evolutionary_checked"] = True

            entry["status"] = PASS
            entry["content_ok"] = True
            entry["error"] = ""

        if all_done:
            duration = round(time.monotonic() - start, 3)
            sanctions = [dict(per_worker[worker].get("evolutionary", {})) for worker in chosen_workers]
            warnings = [item for item in sanctions if str(item.get("status", "PASS")).upper() == "WARN"]
            return {
                "status": PASS,
                "run_id": run_id,
                "duration_seconds": duration,
                "timeout_seconds": int(timeout_seconds),
                "workers": [per_worker[worker] for worker in chosen_workers],
                "sanctions": sanctions,
                "sanction_warnings": len(warnings),
            }

        time.sleep(max(0.1, float(poll_seconds)))

    duration = round(time.monotonic() - start, 3)
    blocked_workers = [entry for entry in per_worker.values() if entry["status"] != PASS]
    blocked_names = sorted(str(item["worker"]) for item in blocked_workers)
    return {
        "status": BLOCKED,
        "run_id": run_id,
        "duration_seconds": duration,
        "timeout_seconds": int(timeout_seconds),
        "workers": [per_worker[worker] for worker in chosen_workers],
        "blocked": len(blocked_workers),
        "error": f"DONE.marker timeout after {int(timeout_seconds)}s; pending_workers={','.join(blocked_names)}",
        "pending_workers": blocked_names,
    }


def _bundle_missing_entries(run_id: str, worker: str) -> list[str]:
    root = RUNS_ROOT / run_id / worker
    missing: list[str] = []
    for rel in WORKER_BUNDLE_REQUIRED:
        if not (root / rel).exists():
            missing.append(rel)
    files_dir = root / "FILES"
    if not files_dir.exists() or not files_dir.is_dir():
        missing.append("FILES/")
    return sorted(set(missing))


def validate_guardrails(run_id: str) -> dict[str, Any]:
    run_root = RUNS_ROOT / run_id
    errors: list[str] = []
    workers_payload: list[dict[str, Any]] = []

    if not run_root.exists():
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "error": f"run folder missing: {run_root.as_posix()}",
        }

    for worker in DOC_WORKERS:
        worker_root = run_root / worker
        docs_dir = worker_root / "FILES" / "docs_test"
        docs = sorted(
            [path.as_posix() for path in docs_dir.glob("*.md") if path.is_file()],
            key=lambda value: value,
        ) if docs_dir.exists() else []
        missing_bundle = _bundle_missing_entries(run_id, worker)
        docs_count = len(docs)
        docs_ok = docs_count == 3
        bundle_ok = len(missing_bundle) == 0
        if not docs_ok:
            errors.append(f"{worker}: expected exactly 3 docs in FILES/docs_test, found {docs_count}")
        if not bundle_ok:
            errors.append(f"{worker}: missing bundle artifacts: {', '.join(missing_bundle)}")
        workers_payload.append(
            {
                "bundle_ok": bundle_ok,
                "docs_count": docs_count,
                "docs_ok": docs_ok,
                "docs": docs,
                "missing_bundle": missing_bundle,
                "worker": worker,
            }
        )

    for worker in CODEX_IDS:
        missing_bundle = _bundle_missing_entries(run_id, worker)
        if missing_bundle:
            errors.append(f"{worker}: missing bundle artifacts: {', '.join(missing_bundle)}")

    aggregator_report = run_root / "Z_aggregator" / "FILES" / "FINAL_REPORT.txt"
    if not aggregator_report.exists():
        errors.append(f"missing aggregator report: {aggregator_report.as_posix()}")
    else:
        text = aggregator_report.read_text(encoding="utf-8")
        ROOT_FINAL_REPORT.write_text(text, encoding="utf-8", newline="\n")

    if not ROOT_FINAL_REPORT.exists():
        errors.append(f"missing root report: {ROOT_FINAL_REPORT.as_posix()}")

    return {
        "status": PASS if not errors else BLOCKED,
        "run_id": run_id,
        "workers": workers_payload,
        "z_aggregator_report": aggregator_report.as_posix(),
        "root_final_report": ROOT_FINAL_REPORT.as_posix(),
        "errors": sorted(set(errors)),
    }


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _safe_rel_path(value: str) -> str | None:
    raw = str(value or "").replace("\\", "/").strip()
    if not raw:
        return None
    while raw.startswith("./"):
        raw = raw[2:]
    raw = raw.strip("/")
    if not raw:
        return None
    parts = [part for part in raw.split("/") if part not in {"", "."}]
    if not parts or any(part == ".." for part in parts):
        return None
    return "/".join(parts)


def _run_git_command(args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except Exception as exc:
        return {"rc": 2, "stdout": "", "stderr": str(exc)}
    return {"rc": int(proc.returncode), "stdout": proc.stdout or "", "stderr": proc.stderr or ""}


def _read_rework_policy(path: Path | None = None) -> dict[str, Any]:
    defaults = {
        "version": "1.0.0",
        "max_reworks": 3,
        "base_loc_target": 10000,
        "loc_increment_per_rework": 5000,
        "required_sanction_level": "OK",
        "use_local_sanction_when_stub": True,
        "task_bank_path": "tools/codex/dispatch/rework_task_bank.json",
    }
    policy_path = path or REWORK_POLICY_PATH
    payload = _safe_read_json(policy_path)
    if not payload:
        return dict(defaults)
    merged = dict(defaults)
    for key in defaults:
        if key in payload:
            merged[key] = payload[key]
    return merged


def _read_task_bank(path: Path) -> list[dict[str, Any]]:
    payload: Any = {}
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            payload = {}
    tasks_raw: list[Any]
    if isinstance(payload, list):
        tasks_raw = payload
    elif isinstance(payload, dict) and isinstance(payload.get("tasks"), list):
        tasks_raw = list(payload.get("tasks", []))
    else:
        tasks_raw = []

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(tasks_raw, start=1):
        if not isinstance(item, dict):
            continue
        task_id = str(item.get("id", f"TASK_{index:03d}")).strip()
        title = str(item.get("title", "")).strip() or task_id
        est = max(0, _to_int(item.get("estimated_mloc"), 0))
        priority = _to_int(item.get("priority"), 0)
        active = bool(item.get("active", True))
        worker_affinity_raw = item.get("worker_affinity", [])
        worker_affinity = [str(value).strip() for value in worker_affinity_raw] if isinstance(worker_affinity_raw, list) else []
        allowed_paths_raw = item.get("allowed_paths", [])
        allowed_paths = [str(value).replace("\\", "/").strip() for value in allowed_paths_raw] if isinstance(allowed_paths_raw, list) else []
        acceptance_raw = item.get("acceptance_checks", [])
        acceptance_checks = [str(value).strip() for value in acceptance_raw] if isinstance(acceptance_raw, list) else []
        normalized.append(
            {
                "id": task_id,
                "title": title,
                "description": str(item.get("description", "")).strip(),
                "estimated_mloc": est,
                "priority": priority,
                "active": active,
                "worker_affinity": [value for value in worker_affinity if value],
                "allowed_paths": [value for value in allowed_paths if value],
                "acceptance_checks": [value for value in acceptance_checks if value],
            }
        )
    return sorted(normalized, key=lambda row: (-int(row["priority"]), -int(row["estimated_mloc"]), str(row["id"])))


def _count_patch_added_loc(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return 0
    added = 0
    for line in text.splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            added += 1
    return int(added)


def _run_manifest_base_ref(run_id: str) -> str:
    manifest = _safe_read_json(RUNS_ROOT / run_id / "RUN_MANIFEST.json")
    candidate = str(manifest.get("base_ref", "")).strip()
    return candidate or "HEAD"


def _is_stub_sanction(report_payload: dict[str, Any], score_payload: dict[str, Any]) -> bool:
    flags = report_payload.get("flags", []) if isinstance(report_payload.get("flags", []), list) else []
    notes = score_payload.get("notes", []) if isinstance(score_payload.get("notes", []), list) else []
    tokens = [str(value).upper() for value in [*flags, *notes]]
    return any("STUB" in token for token in tokens)


def _assignments_path(run_id: str) -> Path:
    return RUNS_ROOT / run_id / "_debug" / "REWORK_TASK_ASSIGNMENTS.json"


def _load_rework_assignments(run_id: str) -> dict[str, list[str]]:
    payload = _safe_read_json(_assignments_path(run_id))
    if not payload:
        return {}
    workers_payload = payload.get("workers", {})
    if not isinstance(workers_payload, dict):
        return {}
    normalized: dict[str, list[str]] = {}
    for worker, values in workers_payload.items():
        if not isinstance(values, list):
            continue
        normalized[str(worker)] = [str(value).strip() for value in values if str(value).strip()]
    return normalized


def _save_rework_assignments(run_id: str, assignments: dict[str, list[str]]) -> None:
    path = _assignments_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "workers": {worker: sorted(set(values)) for worker, values in sorted(assignments.items())},
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_rework_state(worker_root: Path, payload: dict[str, Any]) -> None:
    target = worker_root / "REWORK_STATE.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _select_rework_tasks(
    *,
    worker: str,
    shortfall_mloc: int,
    task_bank: list[dict[str, Any]],
    used_task_ids: set[str],
) -> tuple[list[dict[str, Any]], int, int]:
    if shortfall_mloc <= 0:
        return [], 0, 0
    filtered: list[dict[str, Any]] = []
    for task in task_bank:
        if not bool(task.get("active", True)):
            continue
        task_id = str(task.get("id", "")).strip()
        if not task_id or task_id in used_task_ids:
            continue
        affinity = task.get("worker_affinity", [])
        if isinstance(affinity, list) and affinity and worker not in affinity:
            continue
        filtered.append(task)

    selected: list[dict[str, Any]] = []
    covered = 0
    for task in filtered:
        selected.append(task)
        covered += max(0, _to_int(task.get("estimated_mloc"), 0))
        if covered >= shortfall_mloc:
            break
    remaining = max(0, int(shortfall_mloc) - int(covered))
    return selected, int(covered), int(remaining)


def _strip_rework_block(text: str) -> str:
    pattern = re.compile(
        rf"(?s)\n?{re.escape(REWORK_MARKER_BEGIN)}.*?{re.escape(REWORK_MARKER_END)}\n?",
        re.MULTILINE,
    )
    cleaned = re.sub(pattern, "\n", text)
    return cleaned.rstrip() + "\n"


def _render_rework_prompt_block(request_payload: dict[str, Any]) -> str:
    tasks = request_payload.get("fallback_tasks", [])
    lines = [
        REWORK_MARKER_BEGIN,
        f"REWORK_CYCLE: {request_payload.get('rework_cycle', 1)}",
        f"REWORK_MAX: {request_payload.get('max_reworks', 3)}",
        f"REWORK_TARGET_MLOC: {request_payload.get('target_mloc', 0)}",
        f"REWORK_EFFECTIVE_MLOC: {request_payload.get('effective_mloc', 0)}",
        f"REWORK_SHORTFALL_MLOC: {request_payload.get('shortfall_mloc', 0)}",
        f"REWORK_REQUIRED_SANCTION_LEVEL: {request_payload.get('required_sanction_level', 'OK')}",
        f"REWORK_CURRENT_SANCTION_LEVEL: {request_payload.get('sanction_level', 'WARN')}",
        f"REWORK_CURRENT_SANCTION_SCORE: {request_payload.get('sanction_score', 1.0)}",
        "REWORK_MISSION: Replace failed output with meaningful code. Avoid filler.",
        "REWORK_ACTIONS:",
        "- Rebuild or replace your failed changes with deterministic, testable artifacts.",
        "- Keep scope ownership explicit in SCOPE_LOCK.json.",
        "- Update FILES_CHANGED.json and DIFF.patch to match real mutations.",
        "- End with DONE.marker only after quality checks pass.",
        "REWORK_FALLBACK_TASKS:",
    ]
    if isinstance(tasks, list) and tasks:
        for task in tasks:
            task_id = str(task.get("id", "")).strip()
            title = str(task.get("title", "")).strip()
            est = _to_int(task.get("estimated_mloc"), 0)
            lines.append(f"- {task_id} | {title} | estimated_mloc={est}")
            allowed_paths = task.get("allowed_paths", [])
            if isinstance(allowed_paths, list) and allowed_paths:
                lines.append(f"  allowed_paths: {', '.join(str(item) for item in allowed_paths)}")
    else:
        lines.append("- none available in task bank; improve existing scope output quality and density.")
    lines.append(REWORK_MARKER_END)
    return "\n".join(lines).rstrip() + "\n"


def _inject_rework_prompt_request(run_id: str, worker: str, request_payload: dict[str, Any]) -> dict[str, Any]:
    prompt_file = PROMPTS_ROOT / run_id / expected_prompt_files(run_id)[worker]
    if not prompt_file.exists():
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        placeholder = (
            f"RUN_ID: {run_id}\n"
            f"CODEX_ID: {worker}\n"
            "SESSION_POLICY: CLEAN_START_REQUIRED\n"
            "AUTO_REPORT_REQUIRED: true\n"
        )
        prompt_file.write_text(_apply_prompt_contract(run_id, worker, placeholder), encoding="utf-8", newline="\n")

    current = prompt_file.read_text(encoding="utf-8")
    cleaned = _strip_rework_block(current)
    block = _render_rework_prompt_block(request_payload)
    updated = cleaned.rstrip() + "\n\n" + block
    prompt_file.write_text(updated, encoding="utf-8", newline="\n")
    return {"prompt_file": prompt_file.as_posix(), "updated": True}


def _cleanup_worker_failed_changes(run_id: str, worker: str) -> dict[str, Any]:
    root = RUNS_ROOT / run_id / worker
    files_changed = _safe_read_json(root / "FILES_CHANGED.json")
    changes = files_changed.get("changes", []) if isinstance(files_changed.get("changes", []), list) else []
    changed_paths: set[str] = set()
    for item in changes:
        if not isinstance(item, dict):
            continue
        safe_path = _safe_rel_path(str(item.get("path", "")))
        if safe_path:
            changed_paths.add(safe_path)

    base_ref = _run_manifest_base_ref(run_id)
    restored = 0
    removed = 0
    skipped = 0
    errors: list[str] = []

    for rel in sorted(changed_paths):
        abs_path = (REPO_ROOT / rel).resolve(strict=False)
        try:
            abs_path.relative_to(REPO_ROOT)
        except ValueError:
            skipped += 1
            errors.append(f"unsafe_path:{rel}")
            continue

        tracked = _run_git_command(["ls-files", "--error-unmatch", "--", rel]).get("rc", 2) == 0
        if tracked:
            restore = _run_git_command(["restore", "--source", base_ref, "--", rel])
            if int(restore.get("rc", 2)) != 0:
                restore = _run_git_command(["restore", "--source", "HEAD", "--", rel])
            if int(restore.get("rc", 2)) != 0:
                errors.append(f"restore_failed:{rel}")
            else:
                restored += 1
            continue

        try:
            if abs_path.is_file() or abs_path.is_symlink():
                abs_path.unlink(missing_ok=True)
                removed += 1
            elif abs_path.is_dir():
                shutil.rmtree(abs_path, ignore_errors=True)
                removed += 1
            else:
                skipped += 1
        except Exception as exc:
            errors.append(f"remove_failed:{rel}:{exc}")

    return {
        "base_ref": base_ref,
        "paths_total": len(changed_paths),
        "restored_tracked": restored,
        "removed_untracked": removed,
        "skipped": skipped,
        "errors": sorted(set(errors)),
    }


def _effective_worker_metrics(run_id: str, worker: str, *, use_local_when_stub: bool) -> dict[str, Any]:
    root = RUNS_ROOT / run_id / worker
    score_payload = _safe_read_json(root / "SANCTION_SCORE.json")
    report_payload = _safe_read_json(root / "SELF_EVAL_REPORT.json")
    score_level = str(score_payload.get("sanction_level", report_payload.get("sanction_level", "WARN"))).upper()
    score_value = _to_float(score_payload.get("sanction_score"), _to_float(report_payload.get("sanction_score"), 1.0))
    score_loc = max(0, _to_int(score_payload.get("loc_delta"), 0))
    patch_loc = max(0, _count_patch_added_loc(root / "DIFF.patch"))
    effective_loc = max(score_loc, patch_loc)
    source = "score"
    if use_local_when_stub and _is_stub_sanction(report_payload, score_payload):
        _, local_score = _fallback_sanction_payload(run_id, worker, root)
        score_level = str(local_score.get("sanction_level", score_level)).upper()
        score_value = _to_float(local_score.get("sanction_score"), score_value)
        source = "local_stub_override"
    return {
        "sanction_level": score_level,
        "sanction_score": score_value,
        "loc_delta_score": score_loc,
        "loc_delta_patch": patch_loc,
        "effective_loc_delta": effective_loc,
        "source": source,
    }


def run_rework_cycle(
    run_id: str,
    *,
    workers: list[str],
    cycle: int,
    max_reworks: int | None,
    base_loc_target: int | None,
    loc_increment: int | None,
    policy_path: Path | None,
    task_bank_path: Path | None,
    auto_cleanup: bool = True,
    update_prompts: bool = True,
) -> dict[str, Any]:
    if cycle < 1:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "error": "cycle must be >= 1",
        }

    policy = _read_rework_policy(policy_path)
    configured_max = max(1, _to_int(max_reworks if max_reworks is not None else policy.get("max_reworks"), 3))
    base_target = max(0, _to_int(base_loc_target if base_loc_target is not None else policy.get("base_loc_target"), 10000))
    increment = max(0, _to_int(loc_increment if loc_increment is not None else policy.get("loc_increment_per_rework"), 5000))
    required_level = str(policy.get("required_sanction_level", "OK")).upper()
    use_local_when_stub = bool(policy.get("use_local_sanction_when_stub", True))

    bank_rel = str(policy.get("task_bank_path", "")).strip()
    resolved_bank = task_bank_path
    if resolved_bank is None:
        resolved_bank = (REPO_ROOT / bank_rel).resolve(strict=False) if bank_rel else REWORK_TASK_BANK_PATH
    task_bank = _read_task_bank(resolved_bank)

    assignments = _load_rework_assignments(run_id)
    decisions: list[dict[str, Any]] = []
    rework_workers: list[str] = []
    blocked_workers: list[str] = []

    for worker in workers:
        worker_root = RUNS_ROOT / run_id / worker
        target_mloc = int(base_target + (cycle * increment))
        if not worker_root.exists():
            blocked_workers.append(worker)
            decisions.append(
                {
                    "worker": worker,
                    "decision": BLOCKED,
                    "error": f"worker bundle missing: {worker_root.as_posix()}",
                    "target_mloc": target_mloc,
                }
            )
            continue

        metrics = _effective_worker_metrics(run_id, worker, use_local_when_stub=use_local_when_stub)
        sanction_level = str(metrics.get("sanction_level", "WARN")).upper()
        sanction_score = _to_float(metrics.get("sanction_score"), 1.0)
        effective_loc = max(0, _to_int(metrics.get("effective_loc_delta"), 0))
        artifacts_ok = _artifacts_present(worker_root)
        loc_ok = effective_loc >= target_mloc
        sanction_ok = sanction_level == required_level
        shortfall_mloc = max(0, target_mloc - effective_loc)

        if artifacts_ok and loc_ok and sanction_ok:
            state_payload = {
                "schema_version": 1,
                "run_id": run_id,
                "worker_id": worker,
                "cycle": cycle,
                "status": PASS,
                "target_mloc": target_mloc,
                "effective_mloc": effective_loc,
                "shortfall_mloc": shortfall_mloc,
                "sanction_level": sanction_level,
                "sanction_score": sanction_score,
                "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            }
            _write_rework_state(worker_root, state_payload)
            request_existing = worker_root / "REWORK_REQUEST.json"
            if request_existing.exists():
                try:
                    request_existing.unlink()
                except OSError:
                    pass
            decisions.append(
                {
                    "worker": worker,
                    "decision": PASS,
                    "target_mloc": target_mloc,
                    "effective_mloc": effective_loc,
                    "shortfall_mloc": shortfall_mloc,
                    "sanction_level": sanction_level,
                    "sanction_score": sanction_score,
                    "metrics_source": metrics.get("source", "score"),
                    "rework_state_file": (worker_root / "REWORK_STATE.json").as_posix(),
                }
            )
            continue

        reasons: list[str] = []
        if not artifacts_ok:
            reasons.append("missing evolutionary artifacts")
        if not loc_ok:
            reasons.append(f"effective_mloc={effective_loc} below target_mloc={target_mloc}")
        if not sanction_ok:
            reasons.append(f"sanction_level={sanction_level} expected={required_level}")

        used = set(assignments.get(worker, []))
        selected_tasks, covered_mloc, remaining_mloc = _select_rework_tasks(
            worker=worker,
            shortfall_mloc=shortfall_mloc,
            task_bank=task_bank,
            used_task_ids=used,
        )
        for task in selected_tasks:
            used.add(str(task.get("id", "")).strip())
        assignments[worker] = sorted(item for item in used if item)

        request_payload = {
            "schema_version": 1,
            "run_id": run_id,
            "worker_id": worker,
            "rework_cycle": cycle,
            "max_reworks": configured_max,
            "target_mloc": target_mloc,
            "effective_mloc": effective_loc,
            "shortfall_mloc": shortfall_mloc,
            "required_sanction_level": required_level,
            "sanction_level": sanction_level,
            "sanction_score": sanction_score,
            "metrics_source": metrics.get("source", "score"),
            "reasons": reasons,
            "fallback_tasks": selected_tasks,
            "fallback_coverage_mloc": covered_mloc,
            "fallback_remaining_mloc": remaining_mloc,
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        }
        request_path = worker_root / "REWORK_REQUEST.json"
        request_path.write_text(json.dumps(request_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        _write_rework_state(
            worker_root,
            {
                "schema_version": 1,
                "run_id": run_id,
                "worker_id": worker,
                "cycle": cycle,
                "status": "REWORK_REQUIRED",
                "target_mloc": target_mloc,
                "effective_mloc": effective_loc,
                "shortfall_mloc": shortfall_mloc,
                "sanction_level": sanction_level,
                "sanction_score": sanction_score,
                "request_file": request_path.as_posix(),
                "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
            },
        )

        history_row = dict(request_payload)
        history_row["kind"] = "rework_request"
        _append_jsonl(worker_root / "LOGS" / "rework_history.jsonl", history_row)

        if cycle >= configured_max:
            _write_rework_state(
                worker_root,
                {
                    "schema_version": 1,
                    "run_id": run_id,
                    "worker_id": worker,
                    "cycle": cycle,
                    "status": BLOCKED,
                    "target_mloc": target_mloc,
                    "effective_mloc": effective_loc,
                    "shortfall_mloc": shortfall_mloc,
                    "sanction_level": sanction_level,
                    "sanction_score": sanction_score,
                    "request_file": request_path.as_posix(),
                    "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                },
            )
            blocked_workers.append(worker)
            decisions.append(
                {
                    "worker": worker,
                    "decision": BLOCKED,
                    "target_mloc": target_mloc,
                    "effective_mloc": effective_loc,
                    "shortfall_mloc": shortfall_mloc,
                    "sanction_level": sanction_level,
                    "sanction_score": sanction_score,
                    "request_file": request_path.as_posix(),
                    "reasons": reasons + ["max rework cycles reached"],
                    "fallback_tasks_assigned": [str(task.get("id", "")).strip() for task in selected_tasks],
                }
            )
            continue

        cleanup = {"skipped": True, "errors": []}
        if auto_cleanup:
            cleanup = _cleanup_worker_failed_changes(run_id, worker)
        prompt_update = {"updated": False, "prompt_file": ""}
        if update_prompts:
            prompt_update = _inject_rework_prompt_request(run_id, worker, request_payload)

        marker = worker_root / "DONE.marker"
        if marker.exists():
            try:
                marker.unlink()
            except OSError:
                pass

        if isinstance(cleanup, dict) and cleanup.get("errors"):
            _write_rework_state(
                worker_root,
                {
                    "schema_version": 1,
                    "run_id": run_id,
                    "worker_id": worker,
                    "cycle": cycle,
                    "status": BLOCKED,
                    "target_mloc": target_mloc,
                    "effective_mloc": effective_loc,
                    "shortfall_mloc": shortfall_mloc,
                    "sanction_level": sanction_level,
                    "sanction_score": sanction_score,
                    "request_file": request_path.as_posix(),
                    "cleanup_errors": list(cleanup.get("errors", [])),
                    "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
                },
            )
            blocked_workers.append(worker)
            decisions.append(
                {
                    "worker": worker,
                    "decision": BLOCKED,
                    "target_mloc": target_mloc,
                    "effective_mloc": effective_loc,
                    "shortfall_mloc": shortfall_mloc,
                    "sanction_level": sanction_level,
                    "sanction_score": sanction_score,
                    "request_file": request_path.as_posix(),
                    "cleanup": cleanup,
                    "prompt_update": prompt_update,
                    "reasons": reasons + ["cleanup failed"],
                    "fallback_tasks_assigned": [str(task.get("id", "")).strip() for task in selected_tasks],
                }
            )
            continue

        rework_workers.append(worker)
        decisions.append(
            {
                "worker": worker,
                "decision": "REWORK_REQUIRED",
                "target_mloc": target_mloc,
                "effective_mloc": effective_loc,
                "shortfall_mloc": shortfall_mloc,
                "sanction_level": sanction_level,
                "sanction_score": sanction_score,
                "request_file": request_path.as_posix(),
                "cleanup": cleanup,
                "prompt_update": prompt_update,
                "fallback_tasks_assigned": [str(task.get("id", "")).strip() for task in selected_tasks],
                "fallback_remaining_mloc": remaining_mloc,
                "rework_state_file": (worker_root / "REWORK_STATE.json").as_posix(),
            }
        )

    _save_rework_assignments(run_id, assignments)
    payload = {
        "status": BLOCKED if blocked_workers else PASS,
        "run_id": run_id,
        "cycle": cycle,
        "max_reworks": configured_max,
        "base_loc_target": base_target,
        "loc_increment": increment,
        "required_sanction_level": required_level,
        "task_bank_path": resolved_bank.as_posix(),
        "workers": decisions,
        "rework_workers": sorted(set(rework_workers)),
        "rework_workers_csv": ",".join(sorted(set(rework_workers))),
        "blocked_workers": sorted(set(blocked_workers)),
        "blocked_workers_count": len(sorted(set(blocked_workers))),
        "needs_redispatch": len(rework_workers) > 0 and len(blocked_workers) == 0,
    }
    return payload


def _cmd_validate_run_id(args: argparse.Namespace) -> int:
    errors = validate_run_id(args.run_id)
    payload = {
        "status": PASS if not errors else BLOCKED,
        "run_id": args.run_id,
        "errors": errors,
    }
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_extract_zip(args: argparse.Namespace) -> int:
    payload = extract_prompt_zip(args.run_id)
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_validate_prompts(args: argparse.Namespace) -> int:
    payload = validate_prompt_folder(args.run_id)
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_wait_done(args: argparse.Namespace) -> int:
    try:
        chosen_workers = _parse_workers_subset(args.workers)
    except ValueError as exc:
        payload = {
            "status": BLOCKED,
            "run_id": args.run_id,
            "error": str(exc),
        }
        _emit(payload)
        return _status_code(payload["status"])

    payload = wait_for_done_markers(
        args.run_id,
        workers=chosen_workers,
        timeout_seconds=int(args.timeout_seconds),
        poll_seconds=float(args.poll_seconds),
    )
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_validate_guardrails(args: argparse.Namespace) -> int:
    payload = validate_guardrails(args.run_id)
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_rework_cycle(args: argparse.Namespace) -> int:
    try:
        chosen_workers = _parse_workers_subset(args.workers)
    except ValueError as exc:
        payload = {
            "status": BLOCKED,
            "run_id": args.run_id,
            "error": str(exc),
        }
        _emit(payload)
        return _status_code(payload["status"])

    policy_path = Path(args.policy).resolve(strict=False) if args.policy else None
    task_bank_path = Path(args.task_bank).resolve(strict=False) if args.task_bank else None
    payload = run_rework_cycle(
        args.run_id,
        workers=chosen_workers,
        cycle=int(args.cycle),
        max_reworks=int(args.max_reworks) if args.max_reworks is not None else None,
        base_loc_target=int(args.base_loc_target) if args.base_loc_target is not None else None,
        loc_increment=int(args.loc_increment) if args.loc_increment is not None else None,
        policy_path=policy_path,
        task_bank_path=task_bank_path,
        auto_cleanup=not bool(args.no_cleanup),
        update_prompts=not bool(args.no_prompt_update),
    )
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_next_run_id(args: argparse.Namespace) -> int:
    payload = next_run_id()
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_materialize_pack(args: argparse.Namespace) -> int:
    payload = materialize_prompt_pack(args.run_id, Path(args.pack_path))
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_prepare_manual_run(args: argparse.Namespace) -> int:
    run_id = str(args.run_id).strip() if args.run_id else ""
    if not run_id:
        generated = next_run_id()
        if str(generated.get("status", BLOCKED)).upper() != PASS:
            payload = {
                "status": BLOCKED,
                "error": "unable to generate run id",
                "generator": generated,
            }
            _emit(payload)
            return _status_code(payload["status"])
        run_id = str(generated.get("run_id", "")).strip()

    run_errors = validate_run_id(run_id)
    if run_errors:
        payload = {
            "status": BLOCKED,
            "run_id": run_id,
            "error": "invalid run id",
            "errors": run_errors,
        }
        _emit(payload)
        return _status_code(payload["status"])

    pack_path = Path(args.pack_path).resolve(strict=False)
    materialized = materialize_prompt_pack(run_id, pack_path)
    if str(materialized.get("status", BLOCKED)).upper() != PASS:
        payload = {
            "status": BLOCKED,
            "run_id": run_id,
            "pack_path": pack_path.as_posix(),
            "materialize": materialized,
        }
        _emit(payload)
        return _status_code(payload["status"])

    prompt_validation = validate_prompt_folder(run_id)
    expected = expected_prompt_files(run_id)
    prompt_files = {
        worker: (PROMPTS_ROOT / run_id / expected[worker]).as_posix()
        for worker in CODEX_IDS
    }
    payload = {
        "status": PASS if str(prompt_validation.get("status", BLOCKED)).upper() == PASS else BLOCKED,
        "run_id": run_id,
        "pack_path": pack_path.as_posix(),
        "prompt_dir": (PROMPTS_ROOT / run_id).as_posix(),
        "prompt_files": prompt_files,
        "validate_prompts": prompt_validation,
        "next_step": (
            "Distribute prompt_files to workers manually, then run "
            "pwsh -NoProfile -ExecutionPolicy Bypass -File tools/codex/dispatch/run_manual_flow.ps1 "
            f"-RunId {run_id} -PromptsPackPath {pack_path.as_posix()}"
        ),
    }
    _emit(payload)
    return _status_code(payload["status"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RUN_ID prompt system validator")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_run_id_cmd = sub.add_parser("validate-run-id", help="Validate RUN_ID format")
    validate_run_id_cmd.add_argument("--run-id", required=True)
    validate_run_id_cmd.set_defaults(func=_cmd_validate_run_id)

    extract_zip_cmd = sub.add_parser("extract-zip", help="Extract strict prompt zip")
    extract_zip_cmd.add_argument("--run-id", required=True)
    extract_zip_cmd.set_defaults(func=_cmd_extract_zip)

    validate_prompts_cmd = sub.add_parser("validate-prompts", help="Validate prompt folder and files")
    validate_prompts_cmd.add_argument("--run-id", required=True)
    validate_prompts_cmd.set_defaults(func=_cmd_validate_prompts)

    wait_done_cmd = sub.add_parser("wait-done", help="Wait for all DONE.marker files")
    wait_done_cmd.add_argument("--run-id", required=True)
    wait_done_cmd.add_argument("--workers", help="Comma-separated worker IDs subset")
    wait_done_cmd.add_argument("--timeout-seconds", type=int, default=3600)
    wait_done_cmd.add_argument("--poll-seconds", type=float, default=2.0)
    wait_done_cmd.set_defaults(func=_cmd_wait_done)

    guardrails_cmd = sub.add_parser("validate-guardrails", help="Validate worker docs/bundles and publish root FINAL_REPORT.md")
    guardrails_cmd.add_argument("--run-id", required=True)
    guardrails_cmd.set_defaults(func=_cmd_validate_guardrails)

    rework_cmd = sub.add_parser("rework-cycle", help="Evaluate worker output and auto-prepare rework requests")
    rework_cmd.add_argument("--run-id", required=True)
    rework_cmd.add_argument("--workers", help="Comma-separated worker IDs subset")
    rework_cmd.add_argument("--cycle", required=True, type=int, help="Rework cycle number (starts at 1)")
    rework_cmd.add_argument("--max-reworks", type=int, help="Maximum rework cycles before hard block")
    rework_cmd.add_argument("--base-loc-target", type=int, help="Base target meaningful LOC before rework increments")
    rework_cmd.add_argument("--loc-increment", type=int, help="Additional LOC target per rework cycle")
    rework_cmd.add_argument("--policy", help="Optional policy json path")
    rework_cmd.add_argument("--task-bank", help="Optional task bank json path")
    rework_cmd.add_argument("--no-cleanup", action="store_true", help="Do not auto-clean failed worker mutations")
    rework_cmd.add_argument("--no-prompt-update", action="store_true", help="Do not inject rework instructions into prompts")
    rework_cmd.set_defaults(func=_cmd_rework_cycle)

    next_run_id_cmd = sub.add_parser("next-run-id", help="Generate next RUN_ID in YYYYMMDD_HHMMSS_RAND4 format")
    next_run_id_cmd.set_defaults(func=_cmd_next_run_id)

    materialize_pack_cmd = sub.add_parser("materialize-pack", help="Parse a pack file and write canonical worker prompt files")
    materialize_pack_cmd.add_argument("--run-id", required=True)
    materialize_pack_cmd.add_argument("--pack-path", required=True)
    materialize_pack_cmd.set_defaults(func=_cmd_materialize_pack)

    prepare_manual_cmd = sub.add_parser("prepare-manual-run", help="Generate RUN_ID + materialize/validate prompts for manual distribution")
    prepare_manual_cmd.add_argument("--pack-path", required=True)
    prepare_manual_cmd.add_argument("--run-id", help="Optional explicit RUN_ID")
    prepare_manual_cmd.set_defaults(func=_cmd_prepare_manual_run)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
