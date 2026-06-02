# PRISMO Learning Core V1.1 F2
# Generated package: prismo learn2 3005 1100 fix1
# Operation model: evidence-intake-real, local store writes only, read-only against repo/DB/secrets.
# This file intentionally uses only Python standard library modules.

"""F2 real evidence intake orchestration.

The goal is to make Evidence Vault useful immediately by scanning known safe roots,
prioritizing PRISMO-related evidence, inspecting ZIPs without extraction/execution,
and writing only deterministic local-store registry/report artifacts.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from typing import Any, Callable, Iterable

from .atomic_io import atomic_write_json
from .clock import now_iso
from .evidence_ingestor import ingest_path
from .evidence_registry import load_registry
from .evidence_summary import summarize_records, summarize_intake_report
from .intake_policy import IntakeLimits, candidate_rank, is_priority_candidate, planned_roots, policy_snapshot
from .paths import ensure_store
from .reports import write_ingestion_reports
from .safety import is_forbidden_path

ProgressFn = Callable[[int, int, str], None]


def _noop_progress(step: int, total: int, label: str) -> None:
    return None


def _iter_files(root: Path, limit: int) -> Iterable[Path]:
    count = 0
    for p in root.rglob("*"):
        if count >= limit:
            break
        if not p.is_file():
            continue
        if is_forbidden_path(p):
            continue
        count += 1
        yield p


def collect_candidates(repo_root: str | Path | None = None, limits: IntakeLimits | None = None, include_downloads: bool = True) -> dict[str, Any]:
    limits = limits or IntakeLimits()
    roots = [r for r in planned_roots(repo_root, include_downloads=include_downloads) if r.exists]
    candidates: list[Path] = []
    skipped = 0
    root_stats: list[dict[str, Any]] = []
    zip_count = 0
    for root in roots:
        rp = Path(root.path)
        seen_here = 0
        accepted_here = 0
        for p in _iter_files(rp, limit=limits.max_files_per_root):
            seen_here += 1
            if not is_priority_candidate(p):
                skipped += 1
                continue
            if p.suffix.lower() == ".zip":
                if zip_count >= limits.max_zips:
                    skipped += 1
                    continue
                zip_count += 1
            candidates.append(p)
            accepted_here += 1
        root_stats.append({"root": root.to_dict(), "seen": seen_here, "accepted": accepted_here})
    # Highest operational value first, then recency if available.
    def sort_key(p: Path) -> tuple[int, float, str]:
        try: mtime = p.stat().st_mtime
        except Exception: mtime = 0
        return (candidate_rank(p), mtime, p.name.lower())
    candidates = sorted(dict.fromkeys(candidates), key=sort_key, reverse=True)
    return {
        "ok": True,
        "status": "PLANNED",
        "read_only": True,
        "mutation_allowed": False,
        "roots": [r.to_dict() for r in roots],
        "root_stats": root_stats,
        "candidate_count": len(candidates),
        "skipped_non_priority": skipped,
        "candidates_preview": [str(p) for p in candidates[:160]],
        "limits": limits.to_dict(),
    }


def intake_status(base: str | Path | None = None, repo_root: str | Path | None = None) -> dict[str, Any]:
    registry = load_registry(base)
    records = registry.get("records") or []
    store = ensure_store(base)
    last_report = store / "05_REPORTS" / "f2_intake_report.json"
    payload = {
        "ok": True,
        "status": "AVAILABLE",
        "schema_version": "f2.1",
        "read_only": True,
        "mutation_allowed": False,
        "evidence_count": len(records),
        "summary": summarize_records(records),
        "policy": policy_snapshot(repo_root),
        "last_report_path": str(last_report),
        "last_report_exists": last_report.exists(),
    }
    if last_report.exists():
        try:
            payload["last_report"] = json.loads(last_report.read_text(encoding="utf-8"))
        except Exception as exc:
            payload["last_report_error"] = str(exc)
    return payload


def run_intake(repo_root: str | Path | None = None, base: str | Path | None = None, limits: IntakeLimits | None = None, progress: ProgressFn | None = None, include_downloads: bool = True) -> dict[str, Any]:
    progress = progress or _noop_progress
    limits = limits or IntakeLimits()
    started = time.time()
    store = ensure_store(base)
    progress(1, 6, "planificando raíces seguras")
    plan = collect_candidates(repo_root, limits, include_downloads=include_downloads)
    candidates = [Path(p) for p in plan.get("candidates_preview", [])]
    # The preview is capped; for the real pass recollect full prioritized list under the same caps.
    full_candidates: list[Path] = []
    for r in planned_roots(repo_root, include_downloads=include_downloads):
        if not r.exists:
            continue
        for p in _iter_files(Path(r.path), limit=limits.max_files_per_root):
            if is_priority_candidate(p):
                full_candidates.append(p)
    full_candidates = sorted(dict.fromkeys(full_candidates), key=lambda p: (candidate_rank(p), p.stat().st_mtime if p.exists() else 0), reverse=True)
    progress(2, 6, f"candidatos priorizados: {len(full_candidates)}")
    inserted: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    warnings: list[str] = []
    total = max(len(full_candidates), 1)
    for idx, path in enumerate(full_candidates, start=1):
        if time.time() - started > limits.max_total_seconds:
            warnings.append("intake_time_budget_exhausted")
            break
        try:
            rec = ingest_path(path, base=base)
            rec.setdefault("intake_phase", "F2")
            rec.setdefault("intake_rank", candidate_rank(path))
            inserted.append(rec)
        except Exception as exc:
            errors.append({"path": str(path), "error": str(exc)})
        if idx % 25 == 0 or idx == total:
            progress(2 + min(3, int((idx / total) * 3)), 6, f"ingesta {idx}/{total}")
    registry = load_registry(base)
    records = registry.get("records") or []
    summary = summarize_records(records)
    report = {
        "ok": True,
        "status": "PASS" if inserted else "PARTIAL",
        "schema_version": "f2.1",
        "generated_at": now_iso(),
        "read_only": True,
        "mutation_allowed": False,
        "operation_class": "local_learning_store_write_only",
        "store_root": str(store),
        "candidates_scanned": len(full_candidates),
        "inserted": len(inserted),
        "errors": errors[:200],
        "warnings": warnings,
        "summary": summary,
        "plan": plan,
    }
    progress(5, 6, "escribiendo reportes F2")
    reports_dir = store / "05_REPORTS"
    atomic_write_json(reports_dir / "f2_intake_report.json", report)
    (reports_dir / "f2_intake_report.md").write_text(summarize_intake_report(report), encoding="utf-8", newline="\n")
    write_ingestion_reports(report, base=base)
    progress(6, 6, "F2 intake completo")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PRISMO Learning F2 evidence intake")
    parser.add_argument("--repo", default=None)
    parser.add_argument("--base", default=None)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--max-files-per-root", type=int, default=None)
    parser.add_argument("--max-zips", type=int, default=None)
    parser.add_argument("--max-seconds", type=int, default=None)
    args = parser.parse_args(argv)
    limits = IntakeLimits(
        max_files_per_root=args.max_files_per_root or IntakeLimits().max_files_per_root,
        max_zips=args.max_zips or IntakeLimits().max_zips,
        max_total_seconds=args.max_seconds or IntakeLimits().max_total_seconds,
    )
    if args.status:
        print(json.dumps(intake_status(args.base, args.repo), ensure_ascii=False, indent=2))
        return 0
    if args.plan:
        print(json.dumps(collect_candidates(args.repo, limits), ensure_ascii=False, indent=2))
        return 0
    def cli_progress(step: int, total: int, label: str) -> None:
        pct = int((step / max(total, 1)) * 100)
        print(f"[F2 intake] {pct:3d}% | restante {100-pct:3d}% | {label}", flush=True)
    result = run_intake(args.repo, args.base, limits, progress=cli_progress)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"PASS", "PARTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
