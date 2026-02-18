from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .common import RUNS_DIR, stable_sha256_bytes


def _hash_file(path: Path) -> str:
    return stable_sha256_bytes(path.read_bytes())


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    files = [path for path in root.rglob("*") if path.is_file()]
    files.sort(key=lambda item: item.as_posix().lower())
    return files


def _render_manifest(entries: Iterable[tuple[str, str]]) -> str:
    sorted_entries = sorted(entries, key=lambda item: item[1])
    return "".join(f"{sha256}  {rel}\n" for sha256, rel in sorted_entries)


def _write_manifest(path: Path, entries: Iterable[tuple[str, str]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_manifest(entries), encoding="utf-8", newline="\n")
    return path


def write_bundle_attestation(run_id: str) -> Path:
    run_root = RUNS_DIR / run_id
    entries: list[tuple[str, str]] = []
    for file_path in _iter_files(run_root):
        rel = file_path.relative_to(run_root).as_posix()
        if rel.startswith("attestations/"):
            continue
        entries.append((_hash_file(file_path), rel))
    target = run_root / "attestations" / "bundles.sha256"
    return _write_manifest(target, entries)


def write_ledger_attestation(run_id: str, *, ledger_path: Path | None = None) -> Path:
    run_root = RUNS_DIR / run_id
    actual_ledger_path = ledger_path or (RUNS_DIR / "factory_ledger.jsonl")
    if actual_ledger_path.exists():
        digest = _hash_file(actual_ledger_path)
        rel = actual_ledger_path.relative_to(RUNS_DIR).as_posix()
        entries = [(digest, rel)]
    else:
        entries = []
    target = run_root / "attestations" / "ledger.sha256"
    return _write_manifest(target, entries)


def write_report_attestation(run_id: str, *, report_path: Path | None = None) -> Path:
    run_root = RUNS_DIR / run_id
    actual_report = report_path or (run_root / "Z_integrator" / "FINAL_REPORT.txt")
    entries: list[tuple[str, str]] = []
    if actual_report.exists():
        rel = actual_report.relative_to(run_root).as_posix()
        entries.append((_hash_file(actual_report), rel))
    target = run_root / "attestations" / "report.sha256"
    return _write_manifest(target, entries)


def write_all_attestations(run_id: str, *, report_path: Path | None = None, ledger_path: Path | None = None) -> dict[str, str]:
    bundle = write_bundle_attestation(run_id)
    ledger = write_ledger_attestation(run_id, ledger_path=ledger_path)
    report = write_report_attestation(run_id, report_path=report_path)
    return {
        "bundles": bundle.as_posix(),
        "ledger": ledger.as_posix(),
        "report": report.as_posix(),
    }

