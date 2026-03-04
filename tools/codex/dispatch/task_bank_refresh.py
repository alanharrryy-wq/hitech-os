#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

REPO_DEFAULT = Path(__file__).resolve().parents[3]
DEFAULT_TASK_BANK = "tools/codex/dispatch/rework_task_bank.json"
DEFAULT_SOURCES = "tools/codex/dispatch/task_bank_sources.json"
DEFAULT_STATE = "tools/codex/dispatch/task_bank_state.json"
DEFAULT_REPORT = "tools/codex/dispatch/reports/task_bank_health.json"

CATEGORIES = ("automation", "security", "reliability", "performance", "dx")
REQUIRED_FIELDS = (
    "id",
    "source",
    "value_score",
    "estimated_mloc",
    "allowed_paths",
    "acceptance_checks",
    "owner",
    "expires_at",
)


def _utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _iso_utc(value: dt.datetime | None = None) -> str:
    stamp = value or _utc_now()
    return stamp.replace(microsecond=0).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _to_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _category_from_paths(paths: list[str]) -> str:
    joined = " ".join(path.lower() for path in paths)
    if "security" in joined:
        return "security"
    if "perf" in joined or "performance" in joined:
        return "performance"
    if "test" in joined or "validation" in joined:
        return "reliability"
    if "tool" in joined or "dispatch" in joined or "factory" in joined:
        return "automation"
    return "dx"


def _compute_value_score(task: dict[str, Any]) -> int:
    metrics = task.get("metrics", {}) if isinstance(task.get("metrics"), dict) else {}
    impact = _to_float(metrics.get("impact"), _to_float(task.get("priority"), 50) / 10.0)
    risk = _to_float(metrics.get("risk_reduction"), 5.0)
    frequency = _to_float(metrics.get("frequency"), 5.0)
    unblock = _to_float(metrics.get("unblock"), 5.0)
    confidence = _to_float(metrics.get("confidence"), 7.0)
    score = (
        (impact * 3.0)
        + (risk * 2.5)
        + (frequency * 1.5)
        + (unblock * 1.5)
        + (confidence * 1.5)
    )
    text = f"{task.get('title', '')} {task.get('description', '')}".lower()
    if "loc" in text and "useful" not in text:
        score -= 20.0
    if not task.get("acceptance_checks"):
        score -= 30.0
    if not task.get("allowed_paths"):
        score -= 30.0
    return max(0, min(100, int(round(score))))


def _normalize_task(raw: dict[str, Any], *, index: int, min_value_score: int, now: dt.datetime) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    task = dict(raw)

    task_id = str(task.get("id", f"TASK_{index:03d}")).strip() or f"TASK_{index:03d}"
    source = str(task.get("source", "legacy_bank")).strip() or "legacy_bank"
    owner = str(task.get("owner", "factory")).strip() or "factory"
    title = str(task.get("title", task_id)).strip() or task_id
    description = str(task.get("description", "")).strip()

    allowed_paths_raw = task.get("allowed_paths", [])
    acceptance_raw = task.get("acceptance_checks", [])
    worker_affinity_raw = task.get("worker_affinity", [])

    allowed_paths = [str(item).replace("\\", "/").strip() for item in allowed_paths_raw] if isinstance(allowed_paths_raw, list) else []
    acceptance_checks = [str(item).strip() for item in acceptance_raw] if isinstance(acceptance_raw, list) else []
    worker_affinity = [str(item).strip() for item in worker_affinity_raw] if isinstance(worker_affinity_raw, list) else []

    allowed_paths = [item for item in allowed_paths if item]
    acceptance_checks = [item for item in acceptance_checks if item]
    worker_affinity = [item for item in worker_affinity if item]

    estimated_mloc = max(0, _to_int(task.get("estimated_mloc"), 0))
    priority = _to_int(task.get("priority"), 0)
    category = str(task.get("category", "")).strip().lower()
    if not category:
        category = _category_from_paths(allowed_paths)
    if category not in CATEGORIES:
        category = "automation"

    expires_at = str(task.get("expires_at", "")).strip()
    if not expires_at:
        expires_at = (now + dt.timedelta(days=30)).replace(microsecond=0).isoformat()

    active = bool(task.get("active", True))
    status = str(task.get("status", "ready")).strip().lower()
    if status not in {"ready", "assigned", "backlog", "paused", "expired"}:
        status = "ready"

    normalized = {
        "id": task_id,
        "title": title,
        "description": description,
        "category": category,
        "source": source,
        "owner": owner,
        "priority": priority,
        "estimated_mloc": estimated_mloc,
        "value_score": _to_int(task.get("value_score"), 0),
        "active": active,
        "status": status,
        "expires_at": expires_at,
        "worker_affinity": sorted(set(worker_affinity)),
        "allowed_paths": sorted(set(allowed_paths)),
        "acceptance_checks": sorted(set(acceptance_checks)),
        "metrics": task.get("metrics", {}) if isinstance(task.get("metrics"), dict) else {},
        "created_at_utc": str(task.get("created_at_utc", "")).strip() or _iso_utc(now),
        "updated_at_utc": _iso_utc(now),
    }

    if normalized["value_score"] <= 0:
        normalized["value_score"] = _compute_value_score(normalized)

    missing_contract: list[str] = []
    for key in REQUIRED_FIELDS:
        value = normalized.get(key)
        if key in {"allowed_paths", "acceptance_checks"}:
            if not isinstance(value, list) or not value:
                missing_contract.append(key)
        elif key in {"value_score", "estimated_mloc"}:
            if _to_int(value, -1) < 0:
                missing_contract.append(key)
        else:
            if not str(value).strip():
                missing_contract.append(key)
    if missing_contract:
        errors.append(f"{task_id}:missing_required={','.join(missing_contract)}")
        return None, errors

    if normalized["value_score"] < min_value_score:
        normalized["status"] = "backlog"

    fingerprint_material = json.dumps(
        {
            "source": normalized["source"],
            "title": normalized["title"],
            "allowed_paths": normalized["allowed_paths"],
            "acceptance_checks": normalized["acceptance_checks"],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    normalized["fingerprint"] = hashlib.sha256(fingerprint_material.encode("utf-8")).hexdigest()[:20]
    return normalized, errors


def _dedupe(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_fp: dict[str, dict[str, Any]] = {}
    for task in tasks:
        fp = str(task.get("fingerprint", "")).strip()
        if not fp:
            fp = hashlib.sha256(str(task).encode("utf-8")).hexdigest()[:20]
            task["fingerprint"] = fp
        current = by_fp.get(fp)
        if current is None:
            by_fp[fp] = task
            continue
        keep = current
        if _to_int(task.get("value_score"), 0) > _to_int(current.get("value_score"), 0):
            keep = task
        elif _to_int(task.get("priority"), 0) > _to_int(current.get("priority"), 0):
            keep = task
        by_fp[fp] = keep
    return sorted(
        by_fp.values(),
        key=lambda row: (
            str(row.get("status", "ready")) not in {"ready", "assigned"},
            -_to_int(row.get("value_score"), 0),
            -_to_int(row.get("priority"), 0),
            -_to_int(row.get("estimated_mloc"), 0),
            str(row.get("id", "")),
        ),
    )


def _latest_docs_governor_report(repo_root: Path) -> dict[str, Any] | None:
    reports_dir = repo_root / "tools" / "docs_governor" / "reports"
    if not reports_dir.exists():
        return None
    candidates = sorted(reports_dir.glob("*.json"), key=lambda path: path.name)
    if not candidates:
        return None
    payload = _read_json(candidates[-1], {})
    return payload if isinstance(payload, dict) else None


def _build_signal_tasks(repo_root: Path, *, now: dt.datetime, run_id: str) -> list[dict[str, Any]]:
    signal_tasks: list[dict[str, Any]] = []

    docs_report = _latest_docs_governor_report(repo_root)
    if docs_report and str(docs_report.get("status", "")).lower() == "fail":
        violations = docs_report.get("violations", [])
        count = len(violations) if isinstance(violations, list) else 0
        if count > 0:
            fingerprint = hashlib.sha256(f"docs_governor:{count}".encode("utf-8")).hexdigest()[:8]
            signal_tasks.append(
                {
                    "id": f"AUTO-DOCS-{fingerprint}",
                    "title": "Automate docs-governor remediation triage",
                    "description": f"Build deterministic triage/export pipeline for {count} docs governor violations.",
                    "source": "docs_governor_report",
                    "owner": "factory",
                    "priority": 88,
                    "estimated_mloc": 2200,
                    "category": "automation",
                    "allowed_paths": ["tools/docs_governor/**", "tools/codex/dispatch/**", "docs/GOVERNANCE_DOCS.md"],
                    "acceptance_checks": [
                        "python tools/docs_governor/docs_governor.py --repo . --report-dir tools/docs_governor/reports"
                    ],
                    "worker_affinity": ["D_validation", "B_tooling"],
                    "metrics": {
                        "impact": 8,
                        "risk_reduction": 8,
                        "frequency": 7,
                        "unblock": 8,
                        "confidence": 8,
                    },
                    "created_at_utc": _iso_utc(now),
                    "expires_at": (now + dt.timedelta(days=21)).replace(microsecond=0).isoformat(),
                }
            )

    z_status_files = sorted((repo_root / "tools" / "codex" / "runs").glob("*/Z_integrator/STATUS.json"), key=lambda p: p.as_posix())
    if z_status_files:
        latest = _read_json(z_status_files[-1], {})
        anti_blockers = _to_int(latest.get("anti_padding_blockers"), 0)
        if anti_blockers > 0:
            token = hashlib.sha256(f"anti_padding:{anti_blockers}:{run_id}".encode("utf-8")).hexdigest()[:8]
            signal_tasks.append(
                {
                    "id": f"AUTO-ANTI-{token}",
                    "title": "Anti-padding blocker auto-remediation pipeline",
                    "description": "Implement deterministic remediation hints and fallback assignments from integrator blockers.",
                    "source": "integrator_status",
                    "owner": "factory",
                    "priority": 90,
                    "estimated_mloc": 2600,
                    "category": "automation",
                    "allowed_paths": ["tools/codex/factory/**", "tools/codex/dispatch/**", "docs/factory/**"],
                    "acceptance_checks": ["python -m tools.codex.factory integrate --run-id <RUN_ID> --workers A_core,B_tooling,C_features,D_validation,Z_aggregator"],
                    "worker_affinity": ["A_core", "D_validation", "B_tooling"],
                    "metrics": {
                        "impact": 9,
                        "risk_reduction": 9,
                        "frequency": 7,
                        "unblock": 8,
                        "confidence": 7,
                    },
                    "created_at_utc": _iso_utc(now),
                    "expires_at": (now + dt.timedelta(days=30)).replace(microsecond=0).isoformat(),
                }
            )

    return signal_tasks


def _load_seed_templates(sources_payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    templates: dict[str, list[dict[str, Any]]] = {category: [] for category in CATEGORIES}
    raw = sources_payload.get("seed_templates", {}) if isinstance(sources_payload.get("seed_templates", {}), dict) else {}
    for category, entries in raw.items():
        cat = str(category).strip().lower()
        if cat not in templates or not isinstance(entries, list):
            continue
        templates[cat] = [dict(item) for item in entries if isinstance(item, dict)]
    return templates


def _reserve_targets(sources_payload: dict[str, Any]) -> dict[str, int]:
    defaults = {"automation": 3, "security": 2, "reliability": 2, "performance": 2, "dx": 2}
    raw = sources_payload.get("min_ready_per_category", {}) if isinstance(sources_payload.get("min_ready_per_category", {}), dict) else {}
    result = dict(defaults)
    for key, value in raw.items():
        cat = str(key).strip().lower()
        if cat in result:
            result[cat] = max(0, _to_int(value, result[cat]))
    return result


def _inject_seed_if_needed(tasks: list[dict[str, Any]], templates: dict[str, list[dict[str, Any]]], reserve: dict[str, int], now: dt.datetime) -> list[dict[str, Any]]:
    by_category_ready: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    for task in tasks:
        cat = str(task.get("category", "automation")).strip().lower()
        if cat not in by_category_ready:
            continue
        if bool(task.get("active", True)) and str(task.get("status", "ready")).lower() in {"ready", "assigned"}:
            by_category_ready[cat] += 1

    generated: list[dict[str, Any]] = []
    for category in CATEGORIES:
        missing = max(0, _to_int(reserve.get(category), 0) - by_category_ready.get(category, 0))
        if missing <= 0:
            continue
        seeds = templates.get(category, [])
        for idx in range(missing):
            if seeds:
                seed = dict(seeds[idx % len(seeds)])
            else:
                seed = {
                    "title": f"{category} automation fallback",
                    "description": "Auto-seeded deterministic fallback task.",
                    "allowed_paths": ["tools/codex/**"],
                    "acceptance_checks": ["python -m tools.codex.factory doctor"],
                }
            token = hashlib.sha256(f"seed:{category}:{seed.get('title','')}:{idx}".encode("utf-8")).hexdigest()[:8]
            generated.append(
                {
                    "id": f"SEED-{category[:4].upper()}-{token}",
                    "title": str(seed.get("title", f"{category} seed")).strip() or f"{category} seed",
                    "description": str(seed.get("description", "Auto-seeded fallback task")).strip(),
                    "category": category,
                    "source": "auto_seed",
                    "owner": "factory",
                    "priority": _to_int(seed.get("priority"), 70),
                    "estimated_mloc": max(1000, _to_int(seed.get("estimated_mloc"), 1500)),
                    "value_score": max(70, _to_int(seed.get("value_score"), 75)),
                    "active": True,
                    "status": "ready",
                    "expires_at": (now + dt.timedelta(days=30)).replace(microsecond=0).isoformat(),
                    "worker_affinity": [str(item).strip() for item in (seed.get("worker_affinity", []) if isinstance(seed.get("worker_affinity", []), list) else []) if str(item).strip()],
                    "allowed_paths": [str(item).replace("\\", "/").strip() for item in (seed.get("allowed_paths", []) if isinstance(seed.get("allowed_paths", []), list) else []) if str(item).strip()],
                    "acceptance_checks": [str(item).strip() for item in (seed.get("acceptance_checks", []) if isinstance(seed.get("acceptance_checks", []), list) else []) if str(item).strip()],
                    "created_at_utc": _iso_utc(now),
                    "updated_at_utc": _iso_utc(now),
                    "metrics": seed.get("metrics", {}) if isinstance(seed.get("metrics", {}), dict) else {},
                }
            )
    return generated


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh deterministic live task bank")
    parser.add_argument("--repo", default=str(REPO_DEFAULT))
    parser.add_argument("--task-bank", default=DEFAULT_TASK_BANK)
    parser.add_argument("--sources", default=DEFAULT_SOURCES)
    parser.add_argument("--state", default=DEFAULT_STATE)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--min-value-score", type=int, default=70)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo).resolve()
    task_bank_path = (repo_root / args.task_bank).resolve(strict=False) if not Path(args.task_bank).is_absolute() else Path(args.task_bank)
    sources_path = (repo_root / args.sources).resolve(strict=False) if not Path(args.sources).is_absolute() else Path(args.sources)
    state_path = (repo_root / args.state).resolve(strict=False) if not Path(args.state).is_absolute() else Path(args.state)
    report_path = (repo_root / args.report).resolve(strict=False) if not Path(args.report).is_absolute() else Path(args.report)

    now = _utc_now()
    min_value_score = max(0, int(args.min_value_score))

    current_payload = _read_json(task_bank_path, {})
    current_tasks_raw: list[dict[str, Any]]
    if isinstance(current_payload, dict) and isinstance(current_payload.get("tasks"), list):
        current_tasks_raw = [dict(item) for item in current_payload.get("tasks", []) if isinstance(item, dict)]
    elif isinstance(current_payload, list):
        current_tasks_raw = [dict(item) for item in current_payload if isinstance(item, dict)]
    else:
        current_tasks_raw = []

    sources_payload = _read_json(sources_path, {})
    if not isinstance(sources_payload, dict):
        sources_payload = {}
    source_seed_tasks = sources_payload.get("seed_tasks", []) if isinstance(sources_payload.get("seed_tasks", []), list) else []

    candidates: list[dict[str, Any]] = []
    candidates.extend(current_tasks_raw)
    candidates.extend([dict(item) for item in source_seed_tasks if isinstance(item, dict)])
    candidates.extend(_build_signal_tasks(repo_root, now=now, run_id=str(args.run_id).strip()))

    normalized: list[dict[str, Any]] = []
    errors: list[str] = []
    for idx, raw in enumerate(candidates, start=1):
        item, item_errors = _normalize_task(raw, index=idx, min_value_score=min_value_score, now=now)
        errors.extend(item_errors)
        if item is not None:
            normalized.append(item)

    deduped = _dedupe(normalized)
    templates = _load_seed_templates(sources_payload)
    reserve = _reserve_targets(sources_payload)
    deduped.extend(_inject_seed_if_needed(deduped, templates, reserve, now))

    # Normalize once more after seed injection to ensure contract fields and stable ordering.
    final_norm: list[dict[str, Any]] = []
    for idx, raw in enumerate(deduped, start=1):
        item, item_errors = _normalize_task(raw, index=idx, min_value_score=min_value_score, now=now)
        errors.extend(item_errors)
        if item is not None:
            final_norm.append(item)
    final_tasks = _dedupe(final_norm)

    ready_count = len([item for item in final_tasks if str(item.get("status", "")).lower() in {"ready", "assigned"} and bool(item.get("active", True))])
    by_category_ready: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    for item in final_tasks:
        cat = str(item.get("category", "automation")).lower()
        if cat in by_category_ready and str(item.get("status", "")).lower() in {"ready", "assigned"} and bool(item.get("active", True)):
            by_category_ready[cat] += 1

    output_payload = {
        "version": "2.0.0",
        "description": "Live fallback backlog for automatic worker rework with deterministic scoring and reserve targets.",
        "generated_at_utc": _iso_utc(now),
        "min_value_score": min_value_score,
        "summary": {
            "task_count": len(final_tasks),
            "ready_count": ready_count,
            "ready_by_category": by_category_ready,
            "errors": sorted(set(errors)),
            "reserve_targets": reserve,
        },
        "tasks": final_tasks,
    }

    state_payload = _read_json(state_path, {})
    if not isinstance(state_payload, dict):
        state_payload = {}
    state_payload.update(
        {
            "schema_version": 1,
            "last_refresh_utc": _iso_utc(now),
            "run_id": str(args.run_id).strip(),
            "task_count": len(final_tasks),
            "ready_count": ready_count,
            "errors": sorted(set(errors)),
            "ready_by_category": by_category_ready,
        }
    )

    report_payload = {
        "status": "PASS" if not errors else "WARN",
        "generated_at_utc": _iso_utc(now),
        "task_bank_path": task_bank_path.as_posix(),
        "state_path": state_path.as_posix(),
        "sources_path": sources_path.as_posix(),
        "task_count": len(final_tasks),
        "ready_count": ready_count,
        "ready_by_category": by_category_ready,
        "reserve_targets": reserve,
        "errors": sorted(set(errors)),
    }

    if args.apply:
        _write_json(task_bank_path, output_payload)
        _write_json(state_path, state_payload)
    _write_json(report_path, report_payload)

    print(
        json.dumps(
            {
                "status": "PASS" if not errors else "WARN",
                "task_bank_path": task_bank_path.as_posix(),
                "report_path": report_path.as_posix(),
                "task_count": len(final_tasks),
                "ready_count": ready_count,
                "errors": sorted(set(errors)),
                "applied": bool(args.apply),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
