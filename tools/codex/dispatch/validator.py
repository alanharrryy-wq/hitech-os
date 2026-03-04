from __future__ import annotations

import argparse
import datetime as dt
import hashlib
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
PROMPT_SOURCE_SNAPSHOT_FILE = "PROMPTS_PACK_SOURCE.txt"
PROMPT_RESOLVED_SNAPSHOT_FILE = "PROMPTS_PACK_RESOLVED.txt"
PROMPT_MATERIALIZATION_MANIFEST = "PROMPT_MATERIALIZATION.json"
PROMPT_DISTRIBUTION_CHECKLIST_FILE = "MANUAL_DISTRIBUTION_CHECKLIST.md"
PROMPT_AUXILIARY_FILES: tuple[str, ...] = (
    PROMPT_SOURCE_SNAPSHOT_FILE,
    PROMPT_RESOLVED_SNAPSHOT_FILE,
    PROMPT_MATERIALIZATION_MANIFEST,
    PROMPT_DISTRIBUTION_CHECKLIST_FILE,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_DIR = REPO_ROOT / "tools" / "codex"
WORKTREES_ROOT = CODEX_DIR / "worktrees"
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
AGGREGATOR_FINAL_REPORT_REL = "FINAL_REPORT.txt"
AGGREGATOR_FINAL_REPORT_LEGACY_REL = "FILES/FINAL_REPORT.txt"
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
TASK_BANK_REFRESH_SCRIPT = REPO_ROOT / "tools" / "codex" / "dispatch" / "task_bank_refresh.py"
CONTEXT_LAYER_SCRIPT = REPO_ROOT / "tools" / "codex" / "factory" / "context_layer.py"
REWORK_MARKER_BEGIN = "### REWORK_INSTRUCTION_BEGIN"
REWORK_MARKER_END = "### REWORK_INSTRUCTION_END"
REWORK_DEFAULT_MAX_CYCLES = 3
REWORK_DEFAULT_LOC_INCREMENT = 5000
QUEUE_KIND_REWORK = "rework"
EXECUTION_RULES_PATH = REPO_ROOT / "tools" / "codex" / "dispatch" / "execution_rules.json"
CONTEXT_REQUIRED_READS: tuple[str, ...] = (
    "KERNEL_CONTEXT.md",
    "docs/factory/FACTORY_RUNTIME_EXPLAINED.md",
    "MODULE_BOUNDARIES.md",
    "ARCHITECTURE_DECISIONS.md",
)
SKILLS_BLOCK_HEADER = "Available Skills for this worker:"
SKILLS_USAGE_RULE = "Use only your role's skills; do not use other roles' skills."
SKILLS_Z_READ_ONLY_RULE = "Do NOT modify code; only read bundles."
REAL_CODE_EXTENSIONS: tuple[str, ...] = (".ts", ".tsx", ".js", ".mjs", ".py", ".ps1")
ARTIFACT_EXTENSIONS: tuple[str, ...] = (".json", ".md", ".snapshot", ".lock", ".generated")
GENERIC_UTILITY_NAMES: tuple[str, ...] = (
    "utils.ts",
    "helpers.ts",
    "common.ts",
    "shared.ts",
    "utils.js",
    "helpers.js",
    "common.js",
    "shared.js",
    "utils.py",
    "helpers.py",
    "common.py",
    "shared.py",
)
LOCKFILE_NAMES: tuple[str, ...] = (
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "bun.lockb",
    "npm-shrinkwrap.json",
)

_SKILLS_INDEX_CACHE: dict[str, Any] | None = None


def _fallback_factory_role(worker: str) -> str:
    mapping = {
        "A_core": "A_core",
        "A_worker": "A_core",
        "B_tooling": "B_tooling",
        "B_worker": "B_tooling",
        "C_features": "C_features",
        "C_worker": "C_features",
        "D_validation": "D_validation",
        "D_worker": "D_validation",
        "Z_aggregator": "Z_aggregator",
        "Z_integrator": "Z_aggregator",
    }
    value = str(worker).strip()
    return mapping.get(value, value)


def _load_skills_index() -> dict[str, Any]:
    global _SKILLS_INDEX_CACHE
    if _SKILLS_INDEX_CACHE is not None:
        return _SKILLS_INDEX_CACHE
    try:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from tools.codex.factory.skills_index import build_skills_index, write_skills_index

        index = build_skills_index(repo_root=REPO_ROOT)
        write_skills_index(index, repo_root=REPO_ROOT)
        if isinstance(index, dict):
            _SKILLS_INDEX_CACHE = index
            return index
    except Exception:
        pass
    _SKILLS_INDEX_CACHE = {
        "version": 1,
        "skills_root": ".codex/skills",
        "roles": {},
        "role_sources": {},
    }
    return _SKILLS_INDEX_CACHE


def _factory_role_for_worker(worker: str) -> str:
    value = str(worker).strip()
    try:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from tools.codex.factory.skills_index import factory_role_for_worker

        return str(factory_role_for_worker(value)).strip()
    except Exception:
        return _fallback_factory_role(value)


def _available_skills_block(worker: str) -> str:
    index = _load_skills_index()
    role = _factory_role_for_worker(worker)
    roles = index.get("roles", {}) if isinstance(index, dict) else {}
    role_skills = list(roles.get(role, [])) if isinstance(roles, dict) else []
    lines = [SKILLS_BLOCK_HEADER]
    if role_skills:
        for row in role_skills:
            name = str(row.get("name", "")).strip()
            doc_path = str(row.get("doc_path", "")).strip()
            lines.append(f"- {name}: {doc_path}")
    else:
        lines.append(f"- (none discovered for role {role})")
    lines.append(f"Rule: {SKILLS_USAGE_RULE}")
    if role == "Z_aggregator":
        lines.append(f"Rule: {SKILLS_Z_READ_ONLY_RULE}")
    return "\n".join(lines).strip()


def _prompt_contract_header(run_id: str, worker: str) -> str:
    done_marker = f"tools/codex/runs/{run_id}/{worker}/DONE.marker"
    lines = [
        f"YOU ARE CODEX WORKER: {worker}",
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
        (
            "MANDATORY_READS: "
            "KERNEL_CONTEXT.md,docs/factory/FACTORY_RUNTIME_EXPLAINED.md,"
            "MODULE_BOUNDARIES.md,ARCHITECTURE_DECISIONS.md"
        ),
        "EXECUTION_GOVERNANCE_PATH: tools/codex/dispatch/execution_rules.json",
        "SELF_CHECK_REQUIRED: ORPHAN_MODULES,UNUSED_EXPORTS,FILES_CREATED,REAL_CODE_LOC,ARTIFACT_LOC",
        "PRODUCT_IMPACT_REQUIRED_PATHS: apps/,packages/",
        "REWORK_AUTONOMY_REQUIRED: true",
        f"REWORK_REQUEST_PATH: tools/codex/runs/{run_id}/{worker}/REWORK_REQUEST.json",
        f"REWORK_QUEUE_INBOX_PATH: tools/codex/runs/{run_id}/_queue/rework/inbox/",
        f"REWORK_QUEUE_OUTBOX_PATH: tools/codex/runs/{run_id}/_queue/rework/outbox/",
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
    lines.extend(
        [
            "",
            _available_skills_block(worker),
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


def _worktree_run_root(run_id: str, worker: str) -> Path:
    return WORKTREES_ROOT / worker / "tools" / "codex" / "runs" / run_id


def _copy_file_if_newer(source_path: Path, target_path: Path) -> bool:
    if not source_path.exists() or not source_path.is_file():
        return False
    target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        source_stat = source_path.stat()
        if target_path.exists():
            target_stat = target_path.stat()
            if source_stat.st_size == target_stat.st_size and source_stat.st_mtime_ns <= target_stat.st_mtime_ns:
                return False
        shutil.copy2(source_path, target_path)
        return True
    except OSError:
        return False


def _sync_worker_bundle_from_worktree(run_id: str, worker: str, *, required_only: bool) -> dict[str, Any]:
    source_root = _worktree_run_root(run_id, worker) / worker
    target_root = RUNS_ROOT / run_id / worker
    target_root.mkdir(parents=True, exist_ok=True)

    if not source_root.exists() or not source_root.is_dir():
        return {
            "worker": worker,
            "source_root": source_root.as_posix(),
            "target_root": target_root.as_posix(),
            "source_found": False,
            "copied": 0,
            "checked": 0,
        }

    if required_only:
        rel_files = ["DONE.marker"]
    else:
        rel_files = [path.relative_to(source_root).as_posix() for path in source_root.rglob("*") if path.is_file()]

    copied = 0
    for rel_path in rel_files:
        source_path = source_root / Path(rel_path)
        target_path = target_root / Path(rel_path)
        if _copy_file_if_newer(source_path, target_path):
            copied += 1

    return {
        "worker": worker,
        "source_root": source_root.as_posix(),
        "target_root": target_root.as_posix(),
        "source_found": True,
        "copied": copied,
        "checked": len(rel_files),
    }


def _sync_rework_queue_from_worktrees(run_id: str, *, kind: str = QUEUE_KIND_REWORK) -> dict[str, Any]:
    target_paths = _queue_paths(run_id, kind)
    target_root = target_paths["root"]
    target_root.mkdir(parents=True, exist_ok=True)

    copied = 0
    sources: list[str] = []
    seen_sources: set[str] = set()
    for worker in [*CODEX_IDS, "Z_integrator"]:
        source_root = _worktree_run_root(run_id, worker) / "_queue" / kind
        if not source_root.exists() or not source_root.is_dir():
            continue
        source_key = source_root.as_posix().lower()
        if source_key in seen_sources:
            continue
        seen_sources.add(source_key)
        sources.append(source_root.as_posix())
        for source_path in source_root.rglob("*"):
            if not source_path.is_file():
                continue
            rel_path = source_path.relative_to(source_root)
            target_path = target_root / rel_path
            if _copy_file_if_newer(source_path, target_path):
                copied += 1

    return {
        "run_id": run_id,
        "kind": kind,
        "target_root": target_root.as_posix(),
        "sources": sources,
        "copied": copied,
    }


def _sync_run_from_worktrees(
    run_id: str,
    *,
    workers: list[str] | None,
    required_only: bool,
    include_queue: bool,
) -> dict[str, Any]:
    chosen_workers = workers or list(CODEX_IDS)
    worker_payload = [_sync_worker_bundle_from_worktree(run_id, worker, required_only=required_only) for worker in chosen_workers]
    queue_payload: dict[str, Any] | None = None
    if include_queue:
        queue_payload = _sync_rework_queue_from_worktrees(run_id, kind=QUEUE_KIND_REWORK)
    copied_total = sum(int(item.get("copied", 0)) for item in worker_payload)
    if queue_payload is not None:
        copied_total += int(queue_payload.get("copied", 0))
    payload = {
        "run_id": run_id,
        "workers": worker_payload,
        "copied_total": copied_total,
    }
    if queue_payload is not None:
        payload["queue"] = queue_payload
    return payload


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


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _manual_distribution_checklist(
    *,
    run_id: str,
    workers_csv: str,
    source_pack_path: str,
    source_pack_sha256: str,
    prompt_rows: dict[str, dict[str, Any]],
) -> str:
    lines = [
        f"# Manual Distribution Checklist - {run_id}",
        "",
        "Use this file to preserve task integrity when distributing prompts manually.",
        "",
        f"- RUN_ID: `{run_id}`",
        f"- Source pack: `{source_pack_path}`",
        f"- Source pack sha256: `{source_pack_sha256}`",
        "",
        "## Worker Prompt Integrity",
    ]
    for worker in CODEX_IDS:
        row = prompt_rows.get(worker, {})
        path = str(row.get("prompt_file", "")).strip()
        digest = str(row.get("sha256", "")).strip()
        line_count = _to_int(row.get("line_count"), 0)
        lines.append(f"- `{worker}` -> `{path}` (sha256: `{digest}`, lines: `{line_count}`)")

    lines.extend(
        [
            "",
            "## Dispatch Steps",
            f"1. Send each worker only its dedicated prompt file for `{run_id}`.",
            "2. Require each worker to return full bundle artifacts including `FILES_CHANGED.json` and `DIFF.patch`.",
            "3. Do not accept partial updates without corresponding artifact evidence.",
            "",
            "## Closeout Commands",
            f"1. `python tools/codex/dispatch/validator.py wait-done --run-id {run_id} --workers {workers_csv}`",
            f"2. `python tools/codex/dispatch/validator.py execution-audit --run-id {run_id} --workers {workers_csv}`",
            f"3. `python tools/codex/dispatch/validator.py validate-guardrails --run-id {run_id}`",
            "",
        ]
    )
    return "\n".join(lines)


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
        raw_bytes = pack_path.read_bytes()
    except Exception as exc:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "pack_path": pack_path.as_posix(),
            "prompt_dir": prompt_dir.as_posix(),
            "error": f"prompts pack cannot be read: {exc}",
        }

    try:
        raw_text = raw_bytes.decode("utf-8")
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
    resolved_prompts: dict[str, str] = {}
    worker_rows: dict[str, dict[str, Any]] = {}
    for worker in CODEX_IDS:
        file_name = expected[worker]
        target = prompt_dir / file_name
        resolved_text = parsed[worker].replace("{{RUN_ID}}", run_id)
        resolved_text = _apply_prompt_contract(run_id, worker, resolved_text)
        target.write_text(resolved_text, encoding="utf-8", newline="\n")
        resolved_prompts[worker] = resolved_text
        worker_rows[worker] = {
            "prompt_file": target.as_posix(),
            "sha256": _sha256_text(resolved_text),
            "line_count": len(resolved_text.splitlines()),
            "char_count": len(resolved_text),
        }
        written.append(target.as_posix())

    source_snapshot = prompt_dir / PROMPT_SOURCE_SNAPSHOT_FILE
    source_snapshot.write_bytes(raw_bytes)

    resolved_pack_lines: list[str] = []
    for worker in CODEX_IDS:
        resolved_pack_lines.append(PACK_WORKER_HEADERS.get(worker, f"=== {worker} PROMPT ==="))
        resolved_pack_lines.append(resolved_prompts.get(worker, "").rstrip("\n"))
        resolved_pack_lines.append("")
    resolved_pack_text = "\n".join(resolved_pack_lines).rstrip() + "\n"
    resolved_snapshot = prompt_dir / PROMPT_RESOLVED_SNAPSHOT_FILE
    resolved_snapshot.write_text(resolved_pack_text, encoding="utf-8", newline="\n")

    source_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    workers_csv = ",".join(CODEX_IDS)
    checklist_path = prompt_dir / PROMPT_DISTRIBUTION_CHECKLIST_FILE
    checklist_path.write_text(
        _manual_distribution_checklist(
            run_id=run_id,
            workers_csv=workers_csv,
            source_pack_path=pack_path.as_posix(),
            source_pack_sha256=source_sha256,
            prompt_rows=worker_rows,
        ),
        encoding="utf-8",
        newline="\n",
    )

    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "pack_source": {
            "path": pack_path.as_posix(),
            "sha256": source_sha256,
            "size_bytes": len(raw_bytes),
        },
        "prompt_dir": prompt_dir.as_posix(),
        "workers": worker_rows,
        "workers_csv": workers_csv,
        "source_snapshot_file": source_snapshot.as_posix(),
        "resolved_snapshot_file": resolved_snapshot.as_posix(),
        "checklist_file": checklist_path.as_posix(),
        "contract_header_injected": True,
    }
    manifest_path = prompt_dir / PROMPT_MATERIALIZATION_MANIFEST
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")

    prompt_validation = validate_prompt_folder(run_id)
    final_status = PASS if str(prompt_validation.get("status", BLOCKED)).upper() == PASS else BLOCKED
    return {
        "status": final_status,
        "run_id": run_id,
        "pack_path": pack_path.as_posix(),
        "prompt_dir": prompt_dir.as_posix(),
        "source_pack_sha256": source_sha256,
        "written": sorted(written),
        "source_snapshot_file": source_snapshot.as_posix(),
        "resolved_snapshot_file": resolved_snapshot.as_posix(),
        "materialization_manifest": manifest_path.as_posix(),
        "distribution_checklist": checklist_path.as_posix(),
        "validate_prompts": prompt_validation,
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

    worker_banner = f"YOU ARE CODEX WORKER: {worker}"
    if worker_banner not in text:
        errors.append(f"missing worker identity banner: {worker_banner}")

    marker_path = f"tools/codex/runs/{run_id}/{worker}/DONE.marker"
    if marker_path not in normalized_text:
        errors.append(f"missing DONE.marker path instruction: {marker_path}")

    if "SESSION_POLICY: CLEAN_START_REQUIRED" not in text:
        errors.append("missing session hygiene contract: SESSION_POLICY: CLEAN_START_REQUIRED")
    if "AUTO_REPORT_REQUIRED: true" not in text:
        errors.append("missing auto-report contract: AUTO_REPORT_REQUIRED: true")
    if "PRE_DONE_EVOLUTIONARY_CHECK_REQUIRED: true" not in text:
        errors.append("missing pre-DONE evolutionary contract: PRE_DONE_EVOLUTIONARY_CHECK_REQUIRED: true")
    required_reads_line = (
        "MANDATORY_READS: "
        "KERNEL_CONTEXT.md,docs/factory/FACTORY_RUNTIME_EXPLAINED.md,"
        "MODULE_BOUNDARIES.md,ARCHITECTURE_DECISIONS.md"
    )
    if required_reads_line not in text:
        errors.append(f"missing mandatory reads contract: {required_reads_line}")
    if "EXECUTION_GOVERNANCE_PATH: tools/codex/dispatch/execution_rules.json" not in text:
        errors.append("missing execution governance contract path")
    if "SELF_CHECK_REQUIRED: ORPHAN_MODULES,UNUSED_EXPORTS,FILES_CREATED,REAL_CODE_LOC,ARTIFACT_LOC" not in text:
        errors.append("missing execution self-check contract")
    if "PRODUCT_IMPACT_REQUIRED_PATHS: apps/,packages/" not in text:
        errors.append("missing product impact contract: PRODUCT_IMPACT_REQUIRED_PATHS: apps/,packages/")
    if "REWORK_AUTONOMY_REQUIRED: true" not in text:
        errors.append("missing rework autonomy contract: REWORK_AUTONOMY_REQUIRED: true")
    rework_path = f"tools/codex/runs/{run_id}/{worker}/REWORK_REQUEST.json"
    if rework_path not in normalized_text:
        errors.append(f"missing REWORK_REQUEST path instruction: {rework_path}")
    queue_inbox = f"tools/codex/runs/{run_id}/_queue/rework/inbox/"
    queue_outbox = f"tools/codex/runs/{run_id}/_queue/rework/outbox/"
    if queue_inbox not in normalized_text:
        errors.append(f"missing rework queue inbox path instruction: {queue_inbox}")
    if queue_outbox not in normalized_text:
        errors.append(f"missing rework queue outbox path instruction: {queue_outbox}")

    if SKILLS_BLOCK_HEADER not in text:
        errors.append(f"missing skills block header: {SKILLS_BLOCK_HEADER}")
    skills_rule_line = f"Rule: {SKILLS_USAGE_RULE}"
    if skills_rule_line not in text:
        errors.append(f"missing skills usage rule: {skills_rule_line}")
    if "SKILL.md" not in text and "(none discovered for role " not in text:
        errors.append("missing skills entries in Available Skills block")
    if _factory_role_for_worker(worker) == "Z_aggregator":
        z_rule_line = f"Rule: {SKILLS_Z_READ_ONLY_RULE}"
        if z_rule_line not in text:
            errors.append(f"missing Z read-only rule: {z_rule_line}")

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
        if entry.name not in expected_names and entry.name not in PROMPT_AUXILIARY_FILES:
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
            required_tokens = [
                "SESSION_POLICY: CLEAN_START_REQUIRED",
                "AUTO_REPORT_REQUIRED: true",
                f"YOU ARE CODEX WORKER: {worker}",
                SKILLS_BLOCK_HEADER,
                f"Rule: {SKILLS_USAGE_RULE}",
            ]
            if _factory_role_for_worker(worker) == "Z_aggregator":
                required_tokens.append(f"Rule: {SKILLS_Z_READ_ONLY_RULE}")
            if any(token not in current_text for token in required_tokens):
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


def _queue_paths(run_id: str, kind: str = QUEUE_KIND_REWORK) -> dict[str, Path]:
    root = RUNS_ROOT / run_id / "_queue" / kind
    return {
        "root": root,
        "inbox": root / "inbox",
        "outbox": root / "outbox",
        "deadletter": root / "deadletter",
        "state": root / "state",
        "index": root / "state" / "index.json",
    }


def _ensure_queue_dirs(run_id: str, kind: str = QUEUE_KIND_REWORK) -> dict[str, Path]:
    paths = _queue_paths(run_id, kind)
    for key in ("root", "inbox", "outbox", "deadletter", "state"):
        paths[key].mkdir(parents=True, exist_ok=True)
    if not paths["index"].exists():
        payload = {
            "schema_version": 1,
            "run_id": run_id,
            "kind": kind,
            "messages": {},
            "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        }
        paths["index"].write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return paths


def _load_queue_index(run_id: str, kind: str = QUEUE_KIND_REWORK) -> dict[str, Any]:
    paths = _ensure_queue_dirs(run_id, kind)
    payload = _safe_read_json(paths["index"])
    if not payload:
        return {
            "schema_version": 1,
            "run_id": run_id,
            "kind": kind,
            "messages": {},
            "updated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        }
    messages = payload.get("messages", {})
    if not isinstance(messages, dict):
        messages = {}
    return {
        "schema_version": 1,
        "run_id": run_id,
        "kind": kind,
        "messages": dict(messages),
        "updated_at_utc": str(payload.get("updated_at_utc", "")),
    }


def _save_queue_index(run_id: str, payload: dict[str, Any], kind: str = QUEUE_KIND_REWORK) -> Path:
    paths = _ensure_queue_dirs(run_id, kind)
    payload = dict(payload)
    payload["schema_version"] = 1
    payload["run_id"] = run_id
    payload["kind"] = kind
    payload["updated_at_utc"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    if not isinstance(payload.get("messages"), dict):
        payload["messages"] = {}
    paths["index"].write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return paths["index"]


def _safe_queue_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    token = token.strip("._-")
    return token or "token"


def _path_posix(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _queue_message_id(run_id: str, worker: str, cycle: int, request_payload: dict[str, Any]) -> str:
    stable = json.dumps(request_payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()[:12]
    return f"{run_id}:{worker}:c{cycle}:{digest}"


def _enqueue_rework_request(
    *,
    run_id: str,
    worker: str,
    cycle: int,
    request_payload: dict[str, Any],
) -> dict[str, Any]:
    paths = _ensure_queue_dirs(run_id, QUEUE_KIND_REWORK)
    index_payload = _load_queue_index(run_id, QUEUE_KIND_REWORK)
    messages = dict(index_payload.get("messages", {}))
    message_id = _queue_message_id(run_id, worker, cycle, request_payload)
    now_utc = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    worker_token = _safe_queue_token(worker)
    file_name = f"{stamp}_{worker_token}_c{cycle}_{message_id.split(':')[-1]}.request.json"
    request_file = paths["inbox"] / file_name

    existing = messages.get(message_id)
    if isinstance(existing, dict):
        existing_file = str(existing.get("request_file", "")).strip()
        if existing_file:
            candidate = REPO_ROOT / existing_file
            if candidate.exists():
                return {
                    "message_id": message_id,
                    "request_file": existing_file.replace("\\", "/"),
                    "outbox_pattern": f"*_{worker_token}_c{cycle}_{message_id.split(':')[-1]}.done.json",
                    "status": str(existing.get("status", "queued")),
                    "created_at_utc": str(existing.get("created_at_utc", now_utc)),
                    "reused": True,
                }

    payload = {
        "schema_version": 1,
        "kind": QUEUE_KIND_REWORK,
        "run_id": run_id,
        "worker_id": worker,
        "cycle": int(cycle),
        "message_id": message_id,
        "request": request_payload,
        "created_at_utc": now_utc,
    }
    request_file.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    request_rel = _path_posix(request_file)
    outbox_pattern = f"*_{worker_token}_c{cycle}_{message_id.split(':')[-1]}.done.json"
    messages[message_id] = {
        "worker_id": worker,
        "cycle": int(cycle),
        "status": "queued",
        "request_file": request_rel,
        "outbox_pattern": outbox_pattern,
        "created_at_utc": now_utc,
        "updated_at_utc": now_utc,
    }
    index_payload["messages"] = messages
    _save_queue_index(run_id, index_payload, QUEUE_KIND_REWORK)
    return {
        "message_id": message_id,
        "request_file": request_rel,
        "outbox_pattern": outbox_pattern,
        "status": "queued",
        "created_at_utc": now_utc,
        "reused": False,
    }


def _find_queue_done_ack(run_id: str, worker: str, cycle: int) -> dict[str, Any] | None:
    paths = _ensure_queue_dirs(run_id, QUEUE_KIND_REWORK)
    worker_token = _safe_queue_token(worker)
    pattern = f"*_{worker_token}_c{cycle}_*.done.json"
    candidates = sorted(paths["outbox"].glob(pattern), key=lambda path: path.name)
    for candidate in candidates:
        payload = _safe_read_json(candidate)
        if not payload:
            continue
        if str(payload.get("run_id", "")).strip() != run_id:
            continue
        if str(payload.get("worker_id", "")).strip() != worker:
            continue
        if _to_int(payload.get("cycle"), -1) != int(cycle):
            continue
        return {
            "file": candidate.relative_to(REPO_ROOT).as_posix(),
            "payload": payload,
        }
    return None


def wait_for_rework_queue_outbox(
    run_id: str,
    *,
    workers: list[str],
    cycle: int,
    timeout_seconds: int,
    poll_seconds: float = 2.0,
) -> dict[str, Any]:
    if cycle < 1:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "cycle": cycle,
            "error": "cycle must be >= 1",
        }
    if timeout_seconds < 1:
        timeout_seconds = 1
    if poll_seconds <= 0:
        poll_seconds = 0.5

    deadline = time.time() + float(timeout_seconds)
    pending = {worker for worker in workers}
    acked: list[dict[str, Any]] = []
    while pending and time.time() < deadline:
        _sync_run_from_worktrees(
            run_id,
            workers=workers,
            required_only=True,
            include_queue=True,
        )
        done_now: list[str] = []
        for worker in sorted(pending):
            ack = _find_queue_done_ack(run_id, worker, cycle)
            if ack is None:
                continue
            acked.append(
                {
                    "worker": worker,
                    "cycle": cycle,
                    "outbox_file": ack["file"],
                    "status": str(ack["payload"].get("status", "PASS")).upper(),
                    "message_id": str(ack["payload"].get("message_id", "")).strip(),
                }
            )
            done_now.append(worker)
        for worker in done_now:
            pending.discard(worker)
        if pending:
            time.sleep(poll_seconds)

    if pending:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "cycle": cycle,
            "error": f"queue outbox timeout after {int(timeout_seconds)}s; pending_workers={','.join(sorted(pending))}",
            "acked": sorted(acked, key=lambda item: item["worker"]),
            "pending_workers": sorted(pending),
            "queue_root": _queue_paths(run_id, QUEUE_KIND_REWORK)["root"].as_posix(),
        }

    return {
        "status": PASS,
        "run_id": run_id,
        "cycle": cycle,
        "acked": sorted(acked, key=lambda item: item["worker"]),
        "pending_workers": [],
        "queue_root": _queue_paths(run_id, QUEUE_KIND_REWORK)["root"].as_posix(),
    }


def post_rework_queue_ack(
    run_id: str,
    *,
    worker: str,
    cycle: int,
    status: str,
    message_id: str,
    note: str,
) -> dict[str, Any]:
    if cycle < 1:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "worker": worker,
            "error": "cycle must be >= 1",
        }
    if worker not in CODEX_IDS:
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "worker": worker,
            "error": f"unknown worker '{worker}'",
        }

    paths = _ensure_queue_dirs(run_id, QUEUE_KIND_REWORK)
    worker_token = _safe_queue_token(worker)
    compact_id = _safe_queue_token(message_id) if message_id else "none"
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ack_file = paths["outbox"] / f"{stamp}_{worker_token}_c{cycle}_{compact_id}.done.json"
    payload = {
        "schema_version": 1,
        "kind": QUEUE_KIND_REWORK,
        "run_id": run_id,
        "worker_id": worker,
        "cycle": int(cycle),
        "status": str(status).strip().upper() or PASS,
        "message_id": str(message_id).strip(),
        "note": str(note).strip(),
        "acked_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
    }
    ack_file.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    index_payload = _load_queue_index(run_id, QUEUE_KIND_REWORK)
    messages = dict(index_payload.get("messages", {}))
    if message_id and isinstance(messages.get(message_id), dict):
        row = dict(messages[message_id])
        row["status"] = "acked"
        row["ack_file"] = _path_posix(ack_file)
        row["updated_at_utc"] = payload["acked_at_utc"]
        messages[message_id] = row
        index_payload["messages"] = messages
        _save_queue_index(run_id, index_payload, QUEUE_KIND_REWORK)

    return {
        "status": PASS,
        "run_id": run_id,
        "worker": worker,
        "cycle": int(cycle),
        "outbox_file": _path_posix(ack_file),
        "message_id": str(message_id).strip(),
    }


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
        _sync_run_from_worktrees(
            run_id,
            workers=chosen_workers,
            required_only=True,
            include_queue=False,
        )
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
    execution_audit: dict[str, Any] = {}

    if not run_root.exists():
        return {
            "status": BLOCKED,
            "run_id": run_id,
            "error": f"run folder missing: {run_root.as_posix()}",
        }

    _sync_run_from_worktrees(
        run_id,
        workers=[*CODEX_IDS, "Z_integrator"],
        required_only=False,
        include_queue=True,
    )

    for worker in DOC_WORKERS:
        worker_root = run_root / worker
        docs_dir = worker_root / "FILES" / "docs_test"
        docs = sorted(
            [path.as_posix() for path in docs_dir.glob("*.md") if path.is_file()],
            key=lambda value: value,
        ) if docs_dir.exists() else []
        missing_bundle = _bundle_missing_entries(run_id, worker)
        docs_count = len(docs)
        docs_ok = docs_count in {0, 3}
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

    execution_audit = run_execution_audit(run_id, workers=list(CODEX_IDS))
    if str(execution_audit.get("status", BLOCKED)).upper() != PASS:
        worker_reports = execution_audit.get("workers", []) if isinstance(execution_audit.get("workers", []), list) else []
        for report in worker_reports:
            if not isinstance(report, dict):
                continue
            if str(report.get("status", BLOCKED)).upper() == PASS:
                continue
            worker_name = str(report.get("worker_id", "worker")).strip() or "worker"
            fail_rows = report.get("failures", []) if isinstance(report.get("failures", []), list) else []
            if not fail_rows:
                errors.append(f"{worker_name}: execution governance failed")
                continue
            for row in fail_rows:
                if not isinstance(row, dict):
                    continue
                code = str(row.get("code", "UNKNOWN")).strip()
                detail = str(row.get("detail", "")).strip()
                path = str(row.get("path", "")).strip()
                suffix = f" path={path}" if path else ""
                errors.append(f"{worker_name}: {code}{suffix} {detail}".strip())
        run_failures = execution_audit.get("run_failures", []) if isinstance(execution_audit.get("run_failures", []), list) else []
        for row in run_failures:
            if not isinstance(row, dict):
                continue
            code = str(row.get("code", "UNKNOWN")).strip()
            detail = str(row.get("detail", "")).strip()
            errors.append(f"run_execution_governance: {code} {detail}".strip())

    report_candidates = [
        run_root / "Z_aggregator" / AGGREGATOR_FINAL_REPORT_REL,
        run_root / "Z_aggregator" / AGGREGATOR_FINAL_REPORT_LEGACY_REL,
    ]
    aggregator_report = report_candidates[0]
    for candidate in report_candidates:
        if candidate.exists():
            aggregator_report = candidate
            break
    if not aggregator_report.exists():
        joined_candidates = ", ".join(candidate.as_posix() for candidate in report_candidates)
        errors.append(f"missing aggregator report; checked: {joined_candidates}")
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
        "execution_audit": execution_audit,
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
        "task_bank_sources_path": "tools/codex/dispatch/task_bank_sources.json",
        "task_bank_state_path": "tools/codex/dispatch/task_bank_state.json",
        "task_bank_report_path": "tools/codex/dispatch/reports/task_bank_health.json",
        "task_bank_auto_refresh": True,
        "task_bank_min_value_score": 70,
        "file_queue_poll_seconds": 2.0,
        "execution_rules_path": "tools/codex/dispatch/execution_rules.json",
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
        status_raw = str(item.get("status", "ready")).strip().lower()
        status = status_raw if status_raw in {"ready", "assigned", "backlog", "paused", "expired"} else "ready"
        category = str(item.get("category", "automation")).strip().lower() or "automation"
        source = str(item.get("source", "legacy_bank")).strip() or "legacy_bank"
        owner = str(item.get("owner", "factory")).strip() or "factory"
        expires_at = str(item.get("expires_at", "")).strip()
        value_score = _to_int(item.get("value_score"), priority if priority > 0 else 50)
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
                "status": status,
                "category": category,
                "source": source,
                "owner": owner,
                "expires_at": expires_at,
                "value_score": value_score,
                "worker_affinity": [value for value in worker_affinity if value],
                "allowed_paths": [value for value in allowed_paths if value],
                "acceptance_checks": [value for value in acceptance_checks if value],
            }
        )
    eligible = [
        row
        for row in normalized
        if bool(row.get("active", True)) and str(row.get("status", "ready")).lower() in {"ready", "assigned"}
    ]
    return sorted(
        eligible,
        key=lambda row: (
            -int(row.get("value_score", 0)),
            -int(row.get("priority", 0)),
            -int(row.get("estimated_mloc", 0)),
            str(row.get("id", "")),
        ),
    )


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


def _parse_patch_stats(path: Path) -> dict[str, dict[str, int]]:
    if not path.exists() or not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}

    stats: dict[str, dict[str, int]] = {}
    current_path: str | None = None
    diff_re = re.compile(r"^diff --git a/(.+?) b/(.+)$")

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        diff_match = diff_re.match(line)
        if diff_match:
            current_path = _safe_rel_path(diff_match.group(2))
            if current_path:
                stats.setdefault(current_path, {"added": 0, "removed": 0})
            continue

        if line.startswith("+++ "):
            plus_path = line[4:].strip()
            if plus_path.startswith("b/"):
                candidate = _safe_rel_path(plus_path[2:])
            elif plus_path == "/dev/null":
                candidate = None
            else:
                candidate = _safe_rel_path(plus_path)
            if candidate:
                current_path = candidate
                stats.setdefault(current_path, {"added": 0, "removed": 0})
            continue

        if current_path is None:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            stats[current_path]["added"] = int(stats[current_path]["added"]) + 1
            continue
        if line.startswith("-") and not line.startswith("---"):
            stats[current_path]["removed"] = int(stats[current_path]["removed"]) + 1

    return stats


def _is_test_path(path: str) -> bool:
    rel = f"/{str(path).replace('\\', '/').strip('/').lower()}/"
    return any(
        token in rel
        for token in (
            "/test/",
            "/tests/",
            ".test.",
            ".spec.",
            "_test.",
            "_spec.",
            ".guard.",
            "/integration/",
        )
    )


def _path_top_domain(path: str) -> str:
    normalized = str(path).replace("\\", "/").strip().lstrip("./").strip("/")
    if not normalized:
        return ""
    return normalized.split("/", 1)[0].strip().lower()


def _path_matches_domains(path: str, domains: set[str]) -> bool:
    if not domains:
        return False
    top = _path_top_domain(path)
    if top in domains:
        return True
    normalized = f"/{str(path).replace('\\', '/').strip('/').lower()}/"
    return any(f"/{domain.strip().lower().strip('/')}/" in normalized for domain in domains if str(domain).strip())


def _file_line_count(path: Path) -> int:
    if not path.exists() or not path.is_file():
        return 0
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").splitlines())
    except Exception:
        return 0


def _git_grep_paths(token: str) -> set[str]:
    value = str(token).strip()
    if not value:
        return set()
    proc = subprocess.run(
        [
            "git",
            "grep",
            "-n",
            "-I",
            "--fixed-strings",
            "--",
            value,
            "--",
            "apps",
            "packages",
            "tools",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if proc.returncode not in {0, 1}:
        return set()
    matches: set[str] = set()
    for line in (proc.stdout or "").splitlines():
        path_part = str(line).split(":", 1)[0].strip()
        rel = _safe_rel_path(path_part)
        if rel:
            matches.add(rel)
    return matches


def _read_execution_rules(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or EXECUTION_RULES_PATH
    defaults: dict[str, Any] = {
        "version": "1.0.0",
        "policy_path": policy_path.as_posix(),
        "mandatory_reads": list(CONTEXT_REQUIRED_READS),
        "allowed_top_level_domains": ["apps", "packages", "tools", "docs"],
        "forbidden_top_level_layers": ["engine", "framework", "runtime", "platform", "orchestrator", "manager", "controller", "pipeline"],
        "product_impact_required_domains": ["apps", "packages"],
        "low_product_impact_domains": ["tools", "scripts", "infra"],
        "max_new_files_per_run": 20,
        "file_size_recommended_min_loc": 200,
        "file_size_recommended_max_loc": 800,
        "file_size_hard_max_loc": 1500,
        "generic_utility_names": list(GENERIC_UTILITY_NAMES),
        "real_code_extensions": list(REAL_CODE_EXTENSIONS),
        "artifact_extensions": list(ARTIFACT_EXTENSIONS),
        "min_real_code_ratio": 0.40,
        "max_artifact_ratio": 0.30,
        "min_test_ratio": 0.10,
        "max_test_ratio": 0.30,
        "change_density_min_files": 10,
        "change_density_max_files": 80,
        "module_rules": {
            "min_import_usages": 2,
            "require_runtime_or_test_path": True,
            "require_test_reference": True,
            "strict_orphan_fail": False,
        },
    }
    payload = _safe_read_json(policy_path)
    if not payload:
        return defaults

    merged = dict(defaults)
    for key, value in payload.items():
        if key == "module_rules" and isinstance(value, dict):
            nested = dict(defaults["module_rules"])
            for nested_key, nested_value in value.items():
                if nested_key in nested:
                    nested[nested_key] = nested_value
            merged["module_rules"] = nested
            continue
        if key in merged:
            merged[key] = value
    merged["policy_path"] = policy_path.as_posix()
    return merged


def _load_worker_declared_changes(worker_root: Path) -> list[dict[str, str]]:
    payload = _safe_read_json(worker_root / "FILES_CHANGED.json")
    changes_raw = payload.get("changes", []) if isinstance(payload.get("changes", []), list) else []
    rows: list[dict[str, str]] = []
    for item in changes_raw:
        if not isinstance(item, dict):
            continue
        rel = _safe_rel_path(str(item.get("path", "")))
        if not rel:
            continue
        change_type = str(item.get("change_type", "modified")).strip().lower()
        if change_type not in {"added", "modified", "deleted", "renamed", "copied"}:
            change_type = "modified"
        rows.append({"path": rel, "change_type": change_type})
    return rows


def _write_execution_rules_report(
    *,
    run_id: str,
    worker: str,
    payload: dict[str, Any],
) -> str:
    worker_root = RUNS_ROOT / run_id / worker
    if not worker_root.exists():
        return ""
    target = worker_root / "EXECUTION_RULES_REPORT.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return target.as_posix()


def _evaluate_worker_execution_rules(
    *,
    run_id: str,
    worker: str,
    rules: dict[str, Any],
) -> dict[str, Any]:
    worker_root = RUNS_ROOT / run_id / worker
    declared_rows = _load_worker_declared_changes(worker_root)
    declared_by_path: dict[str, str] = {row["path"]: row["change_type"] for row in declared_rows}
    patch_stats = _parse_patch_stats(worker_root / "DIFF.patch")

    changed_paths = sorted(set([*declared_by_path.keys(), *patch_stats.keys()]))
    new_paths = sorted([path for path, change_type in declared_by_path.items() if change_type == "added"])
    deleted_paths = sorted([path for path, change_type in declared_by_path.items() if change_type == "deleted"])

    allowed_domains = {str(item).strip().lower() for item in (rules.get("allowed_top_level_domains", []) if isinstance(rules.get("allowed_top_level_domains", []), list) else []) if str(item).strip()}
    forbidden_layers = {str(item).strip().lower() for item in (rules.get("forbidden_top_level_layers", []) if isinstance(rules.get("forbidden_top_level_layers", []), list) else []) if str(item).strip()}
    product_domains = {str(item).strip().lower() for item in (rules.get("product_impact_required_domains", []) if isinstance(rules.get("product_impact_required_domains", []), list) else []) if str(item).strip()}
    low_impact_domains = {str(item).strip().lower() for item in (rules.get("low_product_impact_domains", []) if isinstance(rules.get("low_product_impact_domains", []), list) else []) if str(item).strip()}
    generic_names = {str(item).strip().lower() for item in (rules.get("generic_utility_names", []) if isinstance(rules.get("generic_utility_names", []), list) else []) if str(item).strip()}
    real_code_exts = {str(item).strip().lower() for item in (rules.get("real_code_extensions", []) if isinstance(rules.get("real_code_extensions", []), list) else []) if str(item).strip()}
    artifact_exts = {str(item).strip().lower() for item in (rules.get("artifact_extensions", []) if isinstance(rules.get("artifact_extensions", []), list) else []) if str(item).strip()}

    hard_max_loc = max(1, _to_int(rules.get("file_size_hard_max_loc"), 1500))
    recommended_min_loc = max(1, _to_int(rules.get("file_size_recommended_min_loc"), 200))
    recommended_max_loc = max(recommended_min_loc, _to_int(rules.get("file_size_recommended_max_loc"), 800))
    min_real_ratio = max(0.0, min(1.0, _to_float(rules.get("min_real_code_ratio"), 0.4)))
    max_artifact_ratio = max(0.0, min(1.0, _to_float(rules.get("max_artifact_ratio"), 0.3)))
    min_test_ratio = max(0.0, min(1.0, _to_float(rules.get("min_test_ratio"), 0.1)))
    max_test_ratio = max(0.0, min(1.0, _to_float(rules.get("max_test_ratio"), 0.3)))
    density_min = max(0, _to_int(rules.get("change_density_min_files"), 10))
    density_max = max(density_min, _to_int(rules.get("change_density_max_files"), 80))

    module_rules = rules.get("module_rules", {}) if isinstance(rules.get("module_rules", {}), dict) else {}
    min_import_usages = max(1, _to_int(module_rules.get("min_import_usages"), 2))
    require_runtime_or_test = bool(module_rules.get("require_runtime_or_test_path", True))
    require_test_reference = bool(module_rules.get("require_test_reference", True))
    strict_orphan_fail = bool(module_rules.get("strict_orphan_fail", False))

    failures: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    for rel in new_paths:
        parts = rel.split("/")
        top = parts[0].lower() if parts else ""
        if top and top in forbidden_layers:
            failures.append({"code": "FORBIDDEN_LAYER", "path": rel, "detail": f"top-level layer '{top}' is forbidden"})
        if top and allowed_domains and top not in allowed_domains and len(parts) > 1:
            failures.append({"code": "DISALLOWED_TOP_LEVEL", "path": rel, "detail": f"top-level domain '{top}' is not allowed"})
        if Path(rel).name.lower() in generic_names:
            failures.append({"code": "GENERIC_UTILITY_FORBIDDEN", "path": rel, "detail": "generic utility filename is forbidden"})

    real_code_loc = 0
    artifact_loc = 0
    test_code_loc = 0
    file_sizes: list[dict[str, Any]] = []
    touched_product = False
    touched_low_impact = False

    for rel in changed_paths:
        top = _path_top_domain(rel)
        if top in product_domains:
            touched_product = True
        if top in low_impact_domains:
            touched_low_impact = True

        change_type = str(declared_by_path.get(rel, "modified")).strip().lower()
        is_new_file = change_type == "added"
        base_name = Path(rel).name.lower()
        is_lockfile = base_name in LOCKFILE_NAMES
        ext = Path(rel).suffix.lower()
        stats = patch_stats.get(rel, {})
        patch_loc = max(0, _to_int(stats.get("added"), 0)) + max(0, _to_int(stats.get("removed"), 0))
        effective_loc = patch_loc
        file_loc = 0
        if ext in real_code_exts:
            abs_path = REPO_ROOT / rel
            file_loc = _file_line_count(abs_path)
            effective_loc = max(patch_loc, file_loc) if is_new_file else patch_loc
            real_code_loc += patch_loc
            if _is_test_path(rel):
                test_code_loc += patch_loc
        elif not is_lockfile:
            artifact_loc += patch_loc
            if ext and artifact_exts and ext not in artifact_exts:
                warnings.append(
                    {
                        "code": "UNKNOWN_ARTIFACT_EXTENSION",
                        "path": rel,
                        "detail": f"extension '{ext}' counted as artifact but not listed in policy artifact_extensions",
                    }
                )
        file_sizes.append(
            {
                "path": rel,
                "change_type": change_type,
                "loc": int(effective_loc),
                "patch_loc": int(patch_loc),
                "file_loc": int(file_loc),
                "ext": ext,
                "artifact_exempt_lockfile": bool(is_lockfile),
            }
        )
        if ext in real_code_exts:
            if is_new_file and effective_loc > hard_max_loc:
                failures.append(
                    {
                        "code": "FILE_SIZE_HARD_LIMIT",
                        "path": rel,
                        "detail": f"new_file_loc={effective_loc} exceeds hard_max={hard_max_loc}",
                    }
                )
            elif not is_new_file and patch_loc > hard_max_loc:
                failures.append(
                    {
                        "code": "PATCH_SIZE_HARD_LIMIT",
                        "path": rel,
                        "detail": f"patch_loc={patch_loc} exceeds hard_max={hard_max_loc}",
                    }
                )
            if is_new_file and (effective_loc < recommended_min_loc or effective_loc > recommended_max_loc):
                warnings.append(
                    {
                        "code": "FILE_SIZE_RECOMMENDATION",
                        "path": rel,
                        "detail": f"new_file_loc={effective_loc} outside recommended_range={recommended_min_loc}-{recommended_max_loc}",
                    }
                )
            elif not is_new_file and patch_loc > recommended_max_loc:
                warnings.append(
                    {
                        "code": "PATCH_SIZE_RECOMMENDATION",
                        "path": rel,
                        "detail": f"patch_loc={patch_loc} above recommended_max={recommended_max_loc}",
                    }
                )

    total_loc = max(0, int(real_code_loc + artifact_loc))
    real_ratio = _to_float(real_code_loc / total_loc if total_loc > 0 else 0.0, 0.0)
    artifact_ratio = _to_float(artifact_loc / total_loc if total_loc > 0 else 0.0, 0.0)
    test_ratio = _to_float(test_code_loc / real_code_loc if real_code_loc > 0 else 0.0, 0.0)

    if total_loc > 0 and real_ratio < min_real_ratio:
        failures.append(
            {
                "code": "REAL_CODE_RATIO_LOW",
                "path": "",
                "detail": f"real_code_ratio={real_ratio:.3f} below min={min_real_ratio:.3f}",
            }
        )
    if total_loc > 0 and artifact_ratio > max_artifact_ratio:
        failures.append(
            {
                "code": "ARTIFACT_RATIO_HIGH",
                "path": "",
                "detail": f"artifact_ratio={artifact_ratio:.3f} above max={max_artifact_ratio:.3f}",
            }
        )
    if real_code_loc > 0 and (test_ratio < min_test_ratio or test_ratio > max_test_ratio):
        warnings.append(
            {
                "code": "TEST_RATIO_OUT_OF_RANGE",
                "path": "",
                "detail": f"test_ratio={test_ratio:.3f} expected_range={min_test_ratio:.3f}-{max_test_ratio:.3f}",
            }
        )

    changed_files_count = len(changed_paths)
    if changed_files_count > 0 and (changed_files_count < density_min or changed_files_count > density_max):
        warnings.append(
            {
                "code": "CHANGE_DENSITY_OUT_OF_RANGE",
                "path": "",
                "detail": f"files_changed={changed_files_count} expected_range={density_min}-{density_max}",
            }
        )

    if changed_files_count > 0 and touched_low_impact and not touched_product:
        warnings.append(
            {
                "code": "LOW_PRODUCT_IMPACT_WORKER",
                "path": "",
                "detail": "worker changes touched only tools/scripts/infra; run-level enforcement still requires apps/ or packages/",
            }
        )

    module_checks: list[dict[str, Any]] = []
    for rel in new_paths:
        ext = Path(rel).suffix.lower()
        if ext not in real_code_exts or _is_test_path(rel) or rel in deleted_paths:
            continue
        no_ext = rel[:-len(ext)] if ext and rel.endswith(ext) else rel
        stem = Path(rel).stem
        tokens = [no_ext, f"./{stem}", f"../{stem}", f"/{stem}"]
        matches: set[str] = set()
        for token in tokens:
            matches.update(_git_grep_paths(token))
        if rel in matches:
            matches.remove(rel)
        ref_count = len(matches)
        test_ref_count = len([value for value in matches if _is_test_path(value)])
        runtime_or_test_ok = ref_count > 0 or test_ref_count > 0
        module_row = {
            "path": rel,
            "reference_count": ref_count,
            "test_reference_count": test_ref_count,
            "runtime_or_test_ok": runtime_or_test_ok,
        }
        module_checks.append(module_row)

        if ref_count < min_import_usages:
            issue = {
                "code": "ORPHAN_MODULE_RISK",
                "path": rel,
                "detail": f"reference_count={ref_count} below min_import_usages={min_import_usages}",
            }
            if strict_orphan_fail:
                failures.append(issue)
            else:
                warnings.append(issue)
        if require_runtime_or_test and not runtime_or_test_ok:
            issue = {
                "code": "EXECUTION_PATH_MISSING",
                "path": rel,
                "detail": "new module has no runtime/test execution path evidence",
            }
            if strict_orphan_fail:
                failures.append(issue)
            else:
                warnings.append(issue)
        if require_test_reference and test_ref_count < 1:
            issue = {
                "code": "TEST_REFERENCE_MISSING",
                "path": rel,
                "detail": "new module has no test/integration references",
            }
            if strict_orphan_fail:
                failures.append(issue)
            else:
                warnings.append(issue)

    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "policy_path": str(rules.get("policy_path", EXECUTION_RULES_PATH.as_posix())),
        "status": PASS if not failures else BLOCKED,
        "checks": {
            "context_first_required_reads": list(rules.get("mandatory_reads", [])),
            "new_files_count": len(new_paths),
            "changed_files_count": changed_files_count,
            "real_code_loc": int(real_code_loc),
            "artifact_loc": int(artifact_loc),
            "total_loc": int(total_loc),
            "real_code_ratio": real_ratio,
            "artifact_ratio": artifact_ratio,
            "test_loc_ratio": test_ratio,
            "touched_product_domains": touched_product,
            "touched_low_impact_domains": touched_low_impact,
            "module_checks": module_checks,
        },
        "paths": {
            "changed": changed_paths,
            "new": new_paths,
            "deleted": deleted_paths,
        },
        "limits": {
            "file_size_hard_max_loc": hard_max_loc,
            "file_size_recommended_min_loc": recommended_min_loc,
            "file_size_recommended_max_loc": recommended_max_loc,
            "min_real_code_ratio": min_real_ratio,
            "max_artifact_ratio": max_artifact_ratio,
            "min_test_ratio": min_test_ratio,
            "max_test_ratio": max_test_ratio,
            "change_density_min_files": density_min,
            "change_density_max_files": density_max,
        },
        "file_sizes": sorted(file_sizes, key=lambda row: str(row.get("path", ""))),
        "failures": sorted(failures, key=lambda row: (str(row.get("code", "")), str(row.get("path", "")), str(row.get("detail", "")))),
        "warnings": sorted(warnings, key=lambda row: (str(row.get("code", "")), str(row.get("path", "")), str(row.get("detail", "")))),
    }
    report_path = _write_execution_rules_report(run_id=run_id, worker=worker, payload=payload)
    payload["report_file"] = report_path
    return payload


def run_execution_audit(
    run_id: str,
    *,
    workers: list[str] | None = None,
    rules_path: Path | None = None,
) -> dict[str, Any]:
    chosen_workers = workers or list(CODEX_IDS)
    _sync_run_from_worktrees(
        run_id,
        workers=chosen_workers,
        required_only=False,
        include_queue=False,
    )
    rules = _read_execution_rules(rules_path)

    worker_reports: list[dict[str, Any]] = []
    all_changed_paths: set[str] = set()
    total_new_files = 0
    for worker in chosen_workers:
        report = _evaluate_worker_execution_rules(run_id=run_id, worker=worker, rules=rules)
        worker_reports.append(report)
        paths_payload = report.get("paths", {}) if isinstance(report.get("paths", {}), dict) else {}
        changed = paths_payload.get("changed", []) if isinstance(paths_payload.get("changed", []), list) else []
        new_files = paths_payload.get("new", []) if isinstance(paths_payload.get("new", []), list) else []
        all_changed_paths.update(str(path).replace("\\", "/") for path in changed if str(path).strip())
        total_new_files += len([item for item in new_files if str(item).strip()])

    run_failures: list[dict[str, str]] = []
    product_domains = {str(item).strip().lower() for item in (rules.get("product_impact_required_domains", []) if isinstance(rules.get("product_impact_required_domains", []), list) else []) if str(item).strip()}
    touched_product = any((str(path).split("/", 1)[0].lower() in product_domains) for path in all_changed_paths if "/" in str(path))
    if all_changed_paths and not touched_product:
        run_failures.append(
            {
                "code": "RUN_LOW_PRODUCT_IMPACT",
                "detail": "run changes did not touch apps/ or packages/",
            }
        )

    max_new_files = max(1, _to_int(rules.get("max_new_files_per_run"), 20))
    if total_new_files > max_new_files:
        run_failures.append(
            {
                "code": "RUN_MAX_NEW_FILES_EXCEEDED",
                "detail": f"new_files={total_new_files} exceeds max_new_files_per_run={max_new_files}",
            }
        )

    run_root = RUNS_ROOT / run_id
    summary_path = run_root / "_debug" / "EXECUTION_RULES_SUMMARY.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "policy_path": str(rules.get("policy_path", EXECUTION_RULES_PATH.as_posix())),
        "status": PASS if not run_failures and all(str(row.get("status", BLOCKED)).upper() == PASS for row in worker_reports) else BLOCKED,
        "workers": worker_reports,
        "run_checks": {
            "touched_product_domains": touched_product,
            "total_new_files": total_new_files,
            "max_new_files_per_run": max_new_files,
        },
        "run_failures": run_failures,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    summary_payload["summary_file"] = summary_path.as_posix()
    return summary_payload


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


def _task_touches_product_domains(task: dict[str, Any], product_domains: set[str]) -> bool:
    if not product_domains:
        return False
    allowed_paths = task.get("allowed_paths", [])
    if not isinstance(allowed_paths, list):
        return False
    for item in allowed_paths:
        candidate = str(item).strip()
        if candidate and _path_matches_domains(candidate, product_domains):
            return True
    return False


def _select_rework_tasks(
    *,
    worker: str,
    shortfall_mloc: int,
    task_bank: list[dict[str, Any]],
    used_task_ids: set[str],
    min_value_score: int,
    product_domains: set[str] | None = None,
    require_product_paths: bool = False,
) -> tuple[list[dict[str, Any]], int, int]:
    if shortfall_mloc <= 0:
        return [], 0, 0
    product_domain_set = set(product_domains or set())
    filtered: list[dict[str, Any]] = []
    for task in task_bank:
        if not bool(task.get("active", True)):
            continue
        status = str(task.get("status", "ready")).strip().lower()
        if status not in {"ready", "assigned"}:
            continue
        task_id = str(task.get("id", "")).strip()
        if not task_id or task_id in used_task_ids:
            continue
        source = str(task.get("source", "")).strip()
        owner = str(task.get("owner", "")).strip()
        expires_at = str(task.get("expires_at", "")).strip()
        value_score = _to_int(task.get("value_score"), 0)
        if value_score < max(0, int(min_value_score)):
            continue
        if not source or not owner or not expires_at:
            continue
        affinity = task.get("worker_affinity", [])
        if isinstance(affinity, list) and affinity and worker not in affinity:
            continue
        allowed_paths = task.get("allowed_paths", [])
        acceptance_checks = task.get("acceptance_checks", [])
        if not isinstance(allowed_paths, list) or not [str(item).strip() for item in allowed_paths if str(item).strip()]:
            continue
        if not isinstance(acceptance_checks, list) or not [str(item).strip() for item in acceptance_checks if str(item).strip()]:
            continue
        task_row = dict(task)
        task_row["_touches_product"] = _task_touches_product_domains(task_row, product_domain_set)
        if require_product_paths and not bool(task_row.get("_touches_product", False)):
            continue
        filtered.append(task_row)

    filtered.sort(
        key=lambda row: (
            0 if bool(row.get("_touches_product", False)) else 1,
            -_to_int(row.get("value_score"), 0),
            -_to_int(row.get("priority"), 0),
            -_to_int(row.get("estimated_mloc"), 0),
            str(row.get("id", "")),
        )
    )

    selected: list[dict[str, Any]] = []
    covered = 0
    for task in filtered:
        clean = dict(task)
        clean.pop("_touches_product", None)
        selected.append(clean)
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
    queue_request_file = str(request_payload.get("queue_request_file", "")).strip()
    queue_outbox_dir = str(request_payload.get("queue_outbox_dir", "")).strip()
    queue_message_id = str(request_payload.get("queue_message_id", "")).strip()
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
        f"REWORK_QUEUE_REQUEST_FILE: {queue_request_file}",
        f"REWORK_QUEUE_OUTBOX_DIR: {queue_outbox_dir}",
        f"REWORK_QUEUE_MESSAGE_ID: {queue_message_id}",
        (
            "REWORK_QUEUE_ACK_COMMAND: "
            "python tools/codex/dispatch/validator.py queue-ack "
            f"--run-id {request_payload.get('run_id', '')} --worker {request_payload.get('worker_id', '')} "
            f"--cycle {request_payload.get('rework_cycle', 1)} --message-id {queue_message_id} --status PASS"
        ),
        "REWORK_MISSION: Replace failed output with meaningful code. Avoid filler.",
        "REWORK_ACTIONS:",
        "- Rebuild or replace your failed changes with deterministic, testable artifacts.",
        "- Keep scope ownership explicit in SCOPE_LOCK.json.",
        "- Update FILES_CHANGED.json and DIFF.patch to match real mutations.",
        "- End with DONE.marker only after quality checks pass.",
        "- After finishing, write queue outbox ACK using REWORK_QUEUE_ACK_COMMAND.",
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


def _refresh_task_bank(
    *,
    run_id: str,
    policy: dict[str, Any],
    task_bank_path: Path,
) -> dict[str, Any]:
    if not bool(policy.get("task_bank_auto_refresh", True)):
        return {"status": "SKIPPED", "reason": "task_bank_auto_refresh=false"}
    if not TASK_BANK_REFRESH_SCRIPT.exists():
        return {"status": "SKIPPED", "reason": f"refresh script missing: {TASK_BANK_REFRESH_SCRIPT.as_posix()}"}

    sources_rel = str(policy.get("task_bank_sources_path", "tools/codex/dispatch/task_bank_sources.json")).strip()
    state_rel = str(policy.get("task_bank_state_path", "tools/codex/dispatch/task_bank_state.json")).strip()
    report_rel = str(policy.get("task_bank_report_path", "tools/codex/dispatch/reports/task_bank_health.json")).strip()
    min_value = max(0, _to_int(policy.get("task_bank_min_value_score"), 70))
    sources_path = (REPO_ROOT / sources_rel).resolve(strict=False) if sources_rel else Path("")
    state_path = (REPO_ROOT / state_rel).resolve(strict=False) if state_rel else Path("")
    report_path = (REPO_ROOT / report_rel).resolve(strict=False) if report_rel else Path("")

    cmd = [
        sys.executable or "python",
        TASK_BANK_REFRESH_SCRIPT.as_posix(),
        "--repo",
        REPO_ROOT.as_posix(),
        "--task-bank",
        task_bank_path.as_posix(),
        "--min-value-score",
        str(min_value),
        "--apply",
        "--run-id",
        run_id,
    ]
    if sources_path:
        cmd.extend(["--sources", sources_path.as_posix()])
    if state_path:
        cmd.extend(["--state", state_path.as_posix()])
    if report_path:
        cmd.extend(["--report", report_path.as_posix()])

    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    payload = {
        "status": PASS if proc.returncode == 0 else BLOCKED,
        "rc": int(proc.returncode),
        "command": " ".join(cmd),
        "stdout_tail": stdout[-500:],
        "stderr_tail": stderr[-500:],
    }
    return payload


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
    min_value_score = max(0, _to_int(policy.get("task_bank_min_value_score"), 70))

    bank_rel = str(policy.get("task_bank_path", "")).strip()
    resolved_bank = task_bank_path
    if resolved_bank is None:
        resolved_bank = (REPO_ROOT / bank_rel).resolve(strict=False) if bank_rel else REWORK_TASK_BANK_PATH
    refresh_payload = _refresh_task_bank(run_id=run_id, policy=policy, task_bank_path=resolved_bank)
    task_bank = _read_task_bank(resolved_bank)
    rules_rel = str(policy.get("execution_rules_path", "tools/codex/dispatch/execution_rules.json")).strip()
    rules_path = (REPO_ROOT / rules_rel).resolve(strict=False) if rules_rel else EXECUTION_RULES_PATH
    execution_rules = _read_execution_rules(rules_path)
    product_domains = {
        str(item).strip().lower()
        for item in (
            execution_rules.get("product_impact_required_domains", [])
            if isinstance(execution_rules.get("product_impact_required_domains", []), list)
            else []
        )
        if str(item).strip()
    }
    execution_preflight = run_execution_audit(run_id, workers=workers, rules_path=rules_path)
    preflight_workers = execution_preflight.get("workers", []) if isinstance(execution_preflight.get("workers", []), list) else []
    preflight_by_worker: dict[str, dict[str, Any]] = {}
    for row in preflight_workers:
        if not isinstance(row, dict):
            continue
        worker_id = str(row.get("worker_id", "")).strip()
        if worker_id:
            preflight_by_worker[worker_id] = row
    execution_run_failures = (
        execution_preflight.get("run_failures", [])
        if isinstance(execution_preflight.get("run_failures", []), list)
        else []
    )
    run_low_product_impact = any(
        isinstance(row, dict) and str(row.get("code", "")).strip().upper() == "RUN_LOW_PRODUCT_IMPACT"
        for row in execution_run_failures
    )

    assignments = _load_rework_assignments(run_id)
    decisions: list[dict[str, Any]] = []
    rework_workers: list[str] = []
    blocked_workers: list[str] = []
    product_rework_assigned = False

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
        execution_report = preflight_by_worker.get(worker)
        if not isinstance(execution_report, dict):
            execution_report = _evaluate_worker_execution_rules(run_id=run_id, worker=worker, rules=execution_rules)
        require_product_paths = run_low_product_impact and worker != "Z_aggregator" and not product_rework_assigned
        execution_ok = str(execution_report.get("status", BLOCKED)).upper() == PASS
        if require_product_paths and execution_ok:
            execution_ok = False
        shortfall_mloc = max(0, target_mloc - effective_loc)

        if artifacts_ok and loc_ok and sanction_ok and execution_ok:
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
                "execution_rules_status": str(execution_report.get("status", PASS)),
                "execution_report_file": str(execution_report.get("report_file", "")),
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
                    "execution_rules_status": str(execution_report.get("status", PASS)),
                    "execution_report_file": str(execution_report.get("report_file", "")),
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
        if not execution_ok:
            fail_rows = execution_report.get("failures", []) if isinstance(execution_report.get("failures", []), list) else []
            if fail_rows:
                for row in fail_rows:
                    if not isinstance(row, dict):
                        continue
                    code = str(row.get("code", "EXECUTION_RULE_FAIL")).strip() or "EXECUTION_RULE_FAIL"
                    detail = str(row.get("detail", "")).strip()
                    path = str(row.get("path", "")).strip()
                    suffix = f" path={path}" if path else ""
                    reasons.append(f"{code}{suffix} {detail}".strip())
            elif not require_product_paths:
                reasons.append("execution governance checks failed")
        if require_product_paths:
            reasons.append("RUN_LOW_PRODUCT_IMPACT requires rework touching apps/ or packages/")

        used = set(assignments.get(worker, []))
        selection_shortfall = shortfall_mloc if shortfall_mloc > 0 else (1 if require_product_paths else 0)
        selected_tasks, covered_mloc, remaining_mloc = _select_rework_tasks(
            worker=worker,
            shortfall_mloc=selection_shortfall,
            task_bank=task_bank,
            used_task_ids=used,
            min_value_score=min_value_score,
            product_domains=product_domains,
            require_product_paths=require_product_paths,
        )
        if require_product_paths and not selected_tasks:
            reasons.append("TASK_BANK_PRODUCT_IMPACT_GAP: no eligible tasks with allowed_paths in apps/ or packages/")
            selected_tasks, covered_mloc, remaining_mloc = _select_rework_tasks(
                worker=worker,
                shortfall_mloc=selection_shortfall,
                task_bank=task_bank,
                used_task_ids=used,
                min_value_score=min_value_score,
                product_domains=product_domains,
                require_product_paths=False,
            )
        if require_product_paths and any(_task_touches_product_domains(task, product_domains) for task in selected_tasks):
            product_rework_assigned = True
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
            "execution_rules_status": str(execution_report.get("status", BLOCKED)),
            "execution_report_file": str(execution_report.get("report_file", "")),
            "execution_failures": execution_report.get("failures", []),
            "execution_warnings": execution_report.get("warnings", []),
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        }
        queue_entry = _enqueue_rework_request(
            run_id=run_id,
            worker=worker,
            cycle=cycle,
            request_payload=request_payload,
        )
        queue_outbox_dir = _path_posix(_queue_paths(run_id, QUEUE_KIND_REWORK)["outbox"])
        request_payload["queue_kind"] = QUEUE_KIND_REWORK
        request_payload["queue_message_id"] = queue_entry.get("message_id", "")
        request_payload["queue_request_file"] = queue_entry.get("request_file", "")
        request_payload["queue_outbox_pattern"] = queue_entry.get("outbox_pattern", "")
        request_payload["queue_outbox_dir"] = queue_outbox_dir
        request_payload["queue_status"] = queue_entry.get("status", "queued")
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
                "execution_rules_status": str(execution_report.get("status", BLOCKED)),
                "execution_report_file": str(execution_report.get("report_file", "")),
                "request_file": request_path.as_posix(),
                "queue_message_id": queue_entry.get("message_id", ""),
                "queue_request_file": queue_entry.get("request_file", ""),
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
                    "execution_rules_status": str(execution_report.get("status", BLOCKED)),
                    "execution_report_file": str(execution_report.get("report_file", "")),
                    "queue_message_id": queue_entry.get("message_id", ""),
                    "queue_request_file": queue_entry.get("request_file", ""),
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
                    "execution_rules_status": str(execution_report.get("status", BLOCKED)),
                    "execution_report_file": str(execution_report.get("report_file", "")),
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
                    "execution_rules_status": str(execution_report.get("status", BLOCKED)),
                    "execution_report_file": str(execution_report.get("report_file", "")),
                    "queue_message_id": queue_entry.get("message_id", ""),
                    "queue_request_file": queue_entry.get("request_file", ""),
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
                "execution_rules_status": str(execution_report.get("status", BLOCKED)),
                "execution_report_file": str(execution_report.get("report_file", "")),
                "queue_message_id": queue_entry.get("message_id", ""),
                "queue_request_file": queue_entry.get("request_file", ""),
                "queue_outbox_pattern": queue_entry.get("outbox_pattern", ""),
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
        "task_bank_refresh": refresh_payload,
        "execution_preflight_status": str(execution_preflight.get("status", PASS)),
        "execution_preflight_summary": str(execution_preflight.get("summary_file", "")),
        "execution_run_failures": execution_run_failures,
        "workers": decisions,
        "rework_workers": sorted(set(rework_workers)),
        "rework_workers_csv": ",".join(sorted(set(rework_workers))),
        "blocked_workers": sorted(set(blocked_workers)),
        "blocked_workers_count": len(sorted(set(blocked_workers))),
        "needs_redispatch": len(rework_workers) > 0 and len(blocked_workers) == 0,
        "rework_transport": "file_queue",
        "queue": {
            "kind": QUEUE_KIND_REWORK,
            "root": _path_posix(_queue_paths(run_id, QUEUE_KIND_REWORK)["root"]),
            "inbox": _path_posix(_queue_paths(run_id, QUEUE_KIND_REWORK)["inbox"]),
            "outbox": _path_posix(_queue_paths(run_id, QUEUE_KIND_REWORK)["outbox"]),
        },
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


def _cmd_queue_wait_outbox(args: argparse.Namespace) -> int:
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

    payload = wait_for_rework_queue_outbox(
        args.run_id,
        workers=chosen_workers,
        cycle=int(args.cycle),
        timeout_seconds=int(args.timeout_seconds),
        poll_seconds=float(args.poll_seconds),
    )
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_queue_ack(args: argparse.Namespace) -> int:
    payload = post_rework_queue_ack(
        args.run_id,
        worker=str(args.worker).strip(),
        cycle=int(args.cycle),
        status=str(args.status).strip().upper(),
        message_id=str(args.message_id).strip(),
        note=str(args.note).strip(),
    )
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_validate_guardrails(args: argparse.Namespace) -> int:
    payload = validate_guardrails(args.run_id)
    _emit(payload)
    return _status_code(payload["status"])


def _cmd_execution_audit(args: argparse.Namespace) -> int:
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
    payload = run_execution_audit(args.run_id, workers=chosen_workers)
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
    context_build: dict[str, Any] = {"status": "SKIPPED", "reason": f"context script missing: {CONTEXT_LAYER_SCRIPT.as_posix()}"}
    if CONTEXT_LAYER_SCRIPT.exists():
        context_cmd = [
            sys.executable or "python",
            CONTEXT_LAYER_SCRIPT.as_posix(),
            "--run-id",
            run_id,
            "--workers",
            ",".join(CODEX_IDS),
        ]
        context_proc = subprocess.run(
            context_cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        context_stdout = (context_proc.stdout or "").strip()
        parsed_stdout: Any = {}
        if context_stdout:
            try:
                parsed_stdout = json.loads(context_stdout)
            except Exception:
                parsed_stdout = {"raw_stdout_tail": context_stdout[-500:]}
        context_build = {
            "status": PASS if context_proc.returncode == 0 else BLOCKED,
            "rc": int(context_proc.returncode),
            "command": " ".join(context_cmd),
            "stdout": parsed_stdout,
            "stderr_tail": (context_proc.stderr or "").strip()[-500:],
        }
    expected = expected_prompt_files(run_id)
    workers_csv = ",".join(CODEX_IDS)
    prompt_files = {
        worker: (PROMPTS_ROOT / run_id / expected[worker]).as_posix()
        for worker in CODEX_IDS
    }
    closeout_steps = [
        f"python tools/codex/dispatch/validator.py wait-done --run-id {run_id} --workers {workers_csv}",
        f"python tools/codex/dispatch/validator.py execution-audit --run-id {run_id} --workers {workers_csv}",
        f"python tools/codex/dispatch/validator.py validate-guardrails --run-id {run_id}",
    ]
    payload = {
        "status": (
            PASS
            if str(prompt_validation.get("status", BLOCKED)).upper() == PASS
            and str(context_build.get("status", BLOCKED)).upper() == PASS
            else BLOCKED
        ),
        "run_id": run_id,
        "pack_path": pack_path.as_posix(),
        "prompt_dir": (PROMPTS_ROOT / run_id).as_posix(),
        "prompt_files": prompt_files,
        "materialize": materialized,
        "distribution_checklist": str(materialized.get("distribution_checklist", "")),
        "materialization_manifest": str(materialized.get("materialization_manifest", "")),
        "resolved_snapshot_file": str(materialized.get("resolved_snapshot_file", "")),
        "validate_prompts": prompt_validation,
        "context_build": context_build,
        "closeout_steps": closeout_steps,
        "next_step": (
            "Distribute prompt_files manually and execute closeout_steps in order. "
            "run_manual_flow.ps1 remains optional if you want script-managed waits/reworks."
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

    queue_wait_cmd = sub.add_parser("queue-wait-outbox", help="Wait for rework queue outbox acknowledgements")
    queue_wait_cmd.add_argument("--run-id", required=True)
    queue_wait_cmd.add_argument("--workers", help="Comma-separated worker IDs subset")
    queue_wait_cmd.add_argument("--cycle", required=True, type=int)
    queue_wait_cmd.add_argument("--timeout-seconds", type=int, default=3600)
    queue_wait_cmd.add_argument("--poll-seconds", type=float, default=2.0)
    queue_wait_cmd.set_defaults(func=_cmd_queue_wait_outbox)

    queue_ack_cmd = sub.add_parser("queue-ack", help="Post a rework queue outbox acknowledgement")
    queue_ack_cmd.add_argument("--run-id", required=True)
    queue_ack_cmd.add_argument("--worker", required=True)
    queue_ack_cmd.add_argument("--cycle", required=True, type=int)
    queue_ack_cmd.add_argument("--status", default="PASS")
    queue_ack_cmd.add_argument("--message-id", default="")
    queue_ack_cmd.add_argument("--note", default="")
    queue_ack_cmd.set_defaults(func=_cmd_queue_ack)

    guardrails_cmd = sub.add_parser("validate-guardrails", help="Validate worker docs/bundles and publish root FINAL_REPORT.md")
    guardrails_cmd.add_argument("--run-id", required=True)
    guardrails_cmd.set_defaults(func=_cmd_validate_guardrails)

    execution_audit_cmd = sub.add_parser("execution-audit", help="Run anti-hallucination and metrics governance checks")
    execution_audit_cmd.add_argument("--run-id", required=True)
    execution_audit_cmd.add_argument("--workers", help="Comma-separated worker IDs subset")
    execution_audit_cmd.set_defaults(func=_cmd_execution_audit)

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
