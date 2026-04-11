from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys
from dataclasses import asdict

if __package__ in (None, ""):
    _repo_hint = pathlib.Path(__file__).resolve().parents[2]
    if str(_repo_hint) not in sys.path:
        sys.path.insert(0, str(_repo_hint))
    from tools.meta.constants import (  # type: ignore
        FINAL_REPORT_REL,
        LATEST_REL,
        META_ROOT_REL,
        RUNS_REL,
        STABLE_SORT_RULES,
        STATUS_DEGRADED,
        STATUS_OFFLINE,
        STATUS_OK,
        TIMEZONE_NAME,
    )
    from tools.meta.debt_parser import debt_totals, parse_repo_debt  # type: ignore
    from tools.meta.federation import RepoEvaluation, evaluate_federation_status, evaluate_repo  # type: ignore
    from tools.meta.hashing import canonical_json, combine_hashes  # type: ignore
    from tools.meta.io_ops import atomic_write_json, atomic_write_text, copy_latest, ensure_dir, write_latest_run_pointer  # type: ignore
    from tools.meta.pathing import as_posix, detect_repo_root, now_local_timestamp  # type: ignore
    from tools.meta.registry import ensure_default_registry, load_registry  # type: ignore
    from tools.meta.report_writer import build_meta_report  # type: ignore
else:
    from .constants import (
        FINAL_REPORT_REL,
        LATEST_REL,
        META_ROOT_REL,
        RUNS_REL,
        STABLE_SORT_RULES,
        STATUS_DEGRADED,
        STATUS_OFFLINE,
        STATUS_OK,
        TIMEZONE_NAME,
    )
    from .debt_parser import debt_totals, parse_repo_debt
    from .federation import RepoEvaluation, evaluate_federation_status, evaluate_repo
    from .hashing import canonical_json, combine_hashes
    from .io_ops import atomic_write_json, atomic_write_text, copy_latest, ensure_dir, write_latest_run_pointer
    from .pathing import as_posix, detect_repo_root, now_local_timestamp
    from .registry import ensure_default_registry, load_registry
    from .report_writer import build_meta_report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HITECH federation meta-governance orchestrator")
    parser.add_argument("--registry", default="docs/meta-gov/REPO_REGISTRY.yaml")
    parser.add_argument("--repo-root", default="")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--no-run-docs-doctor", action="store_true")
    return parser.parse_args(argv)


def progress(step: int, total: int, message: str) -> None:
    percent = int((step / total) * 100)
    print(f"[{step}/{total}] {percent}% {message}", flush=True)


def orchestrate(ns: argparse.Namespace) -> int:
    total_steps = 9
    progress(1, total_steps, "Detecting repository root and registry path")
    repo_root = detect_repo_root(ns.repo_root or None)
    registry_path = pathlib.Path(ns.registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    ensure_dir(registry_path.parent)
    ensure_default_registry(registry_path)

    progress(2, total_steps, "Loading registry")
    registry = load_registry(registry_path)
    run_id, timestamp_iso = now_local_timestamp()
    if ns.run_id:
        run_id = ns.run_id.strip()
    run_docs_doctor = not ns.no_run_docs_doctor

    progress(3, total_steps, "Evaluating repositories")
    repo_states: list[RepoEvaluation] = []
    for entry in registry.repos:
        repo_states.append(evaluate_repo(entry, run_docs_doctor=run_docs_doctor))
    repo_states.sort(key=lambda r: r.name.lower())

    progress(4, total_steps, "Aggregating debt from reports")
    all_debt_items: list[dict] = []
    for state in repo_states:
        if not state.online:
            continue
        repo_root_path = pathlib.Path(state.path)
        items = parse_repo_debt(state.name, repo_root_path)
        state.debt_items = [asdict(item) for item in items]
        all_debt_items.extend(state.debt_items)
    all_debt_items = sorted(all_debt_items, key=lambda item: item["debt_id"])
    totals = debt_totals(all_debt_items)

    progress(5, total_steps, "Evaluating federation law")
    federation_status = evaluate_federation_status(repo_states, strict=ns.strict)
    blockers = {
        "constitutional": sorted(
            f"{repo.name}: {line}"
            for repo in repo_states
            for line in repo.blockers["constitutional"]
        ),
        "policy": sorted(
            f"{repo.name}: {line}"
            for repo in repo_states
            for line in repo.blockers["policy"]
        ),
        "tooling": sorted(
            f"{repo.name}: {line}"
            for repo in repo_states
            for line in repo.blockers["tooling"]
        ),
    }

    summary_counts = {
        "repos_total": len(repo_states),
        "online_total": sum(1 for r in repo_states if r.online),
        "offline_total": sum(1 for r in repo_states if not r.online),
        "ok_total": sum(1 for r in repo_states if r.status == STATUS_OK),
        "degraded_total": sum(1 for r in repo_states if r.status == STATUS_DEGRADED),
        "blocked_total": sum(1 for r in repo_states if r.status == "BLOCKED"),
        "missing_tooling_total": sum(1 for r in repo_states if r.status == "MISSING_TOOLING"),
    }

    progress(6, total_steps, "Building deterministic outputs")
    repo_dicts = [asdict(state) for state in repo_states]
    federation_status_doc = {
        "federation": {
            "run_id": run_id,
            "timestamp_iso": timestamp_iso,
            "timezone": TIMEZONE_NAME,
            "status": federation_status,
            "summary_counts": summary_counts,
        },
        "repos": repo_dicts,
        "blockers": blockers,
        "debt": {
            "global_debt_items": all_debt_items,
            "totals": totals,
        },
        "next_actions": {
            "immediate": [],
            "suggested": [],
        },
        "determinism": {
            "inputs_hash": "",
            "outputs_hash": "",
            "stable_sort_rules": STABLE_SORT_RULES,
        },
    }

    input_parts = [
        registry_path.read_text(encoding="utf-8"),
        json.dumps([asdict(r) for r in repo_states], sort_keys=True),
        str(ns.strict),
        str(run_docs_doctor),
    ]
    federation_status_doc["determinism"]["inputs_hash"] = combine_hashes(input_parts)

    meta_report_text = build_meta_report(
        run_id=run_id,
        timestamp_iso=timestamp_iso,
        timezone_name=TIMEZONE_NAME,
        federation_status=federation_status,
        repos=repo_dicts,
        blockers=blockers,
        debt_summary={"totals": totals},
    )

    global_debt_doc = {
        "run_id": run_id,
        "timezone": TIMEZONE_NAME,
        "items": all_debt_items,
        "totals": totals,
    }

    status_without_output_hash = canonical_json(federation_status_doc)
    debt_text = canonical_json(global_debt_doc)
    outputs_hash = combine_hashes([status_without_output_hash, debt_text, meta_report_text])
    federation_status_doc["determinism"]["outputs_hash"] = outputs_hash

    progress(7, total_steps, "Writing docs/meta-gov artifacts")
    meta_root = repo_root / META_ROOT_REL
    runs_root = repo_root / RUNS_REL
    latest_root = repo_root / LATEST_REL
    run_root = runs_root / run_id
    ensure_dir(meta_root)
    ensure_dir(runs_root)
    ensure_dir(run_root)

    latest_run_path = meta_root / "LATEST_RUN.txt"
    status_path = meta_root / "FEDERATION_STATUS.json"
    debt_path = meta_root / "GLOBAL_DEBT_LOG.json"
    report_path = meta_root / "META_REPORT.md"

    run_status_path = run_root / "FEDERATION_STATUS.json"
    run_debt_path = run_root / "GLOBAL_DEBT_LOG.json"
    run_report_path = run_root / "META_REPORT.md"

    if ns.write:
        atomic_write_json(status_path, federation_status_doc)
        atomic_write_json(debt_path, global_debt_doc)
        atomic_write_text(report_path, meta_report_text)

        atomic_write_json(run_status_path, federation_status_doc)
        atomic_write_json(run_debt_path, global_debt_doc)
        atomic_write_text(run_report_path, meta_report_text)

        write_latest_run_pointer(latest_run_path, run_id)
        copy_latest(latest_root, [run_status_path, run_debt_path, run_report_path])

    progress(8, total_steps, "Applying open-folder behavior")
    if ns.open:
        target = latest_root.resolve()
        _open_folder(target)

    progress(9, total_steps, "Completed")
    print(f"RESULT: {federation_status}")
    print(f"REPO_ROOT: {as_posix(repo_root)}")
    print(f"META_ROOT: {as_posix(meta_root)}")
    print(f"RUN_ID: {run_id}")
    print(f"LATEST: {as_posix(latest_root)}")
    return 0 if federation_status in (STATUS_OK, STATUS_DEGRADED) else 2


def _open_folder(path: pathlib.Path) -> None:
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif shutil.which("xdg-open"):
            subprocess.run(["xdg-open", str(path)], check=False)
        else:
            print(f"open not supported on this platform; target: {path}")
    except Exception as exc:
        print(f"open failed: {exc}")


def main(argv: list[str] | None = None) -> int:
    ns = parse_args(argv or sys.argv[1:])
    return orchestrate(ns)


if __name__ == "__main__":
    raise SystemExit(main())
