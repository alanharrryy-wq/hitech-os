# PRISMO Learning Core V1.1 F2
# Generated package: prismo learn2 3005 1100 fix1
# Operation model: evidence-intake-real, local store writes only, read-only against repo/DB/secrets.
# This file intentionally uses only Python standard library modules.

"""ZIP inspector that never extracts or executes payloads."""
from __future__ import annotations
import zipfile
from pathlib import Path
from typing import Any
from .constants import MAX_TOTAL_ZIP_READ_BYTES, MAX_ZIP_ENTRIES, MAX_ZIP_TEXT_ENTRY_BYTES
from .manifest_detector import is_manifest_name, is_report_name, is_playwright_name
from .pass_fail_detector import detect_status_from_text
from .secret_scanner import scan_text, redact

SAFE_ZIP_TEXT_SUFFIXES = (".md", ".txt", ".json", ".log", ".csv", ".html", ".xml", ".yml", ".yaml")
FORBIDDEN_ZIP_NAMES = (".env", "secrets", "credentials", "id_rsa", "private-key", "service-account", "sk-proj", "token")


def read_small_text_entry(zip_path: str | Path, entry: str) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(entry)
        if info.file_size > MAX_ZIP_TEXT_ENTRY_BYTES:
            return {"ok": False, "entry": entry, "reason": "entry_too_large", "size_bytes": info.file_size}
        if not entry.lower().endswith(SAFE_ZIP_TEXT_SUFFIXES):
            return {"ok": False, "entry": entry, "reason": "not_safe_text_suffix", "size_bytes": info.file_size}
        text = zf.read(entry).decode("utf-8", errors="replace")
    return {"ok": True, "entry": entry, "text": redact(text), "secret_scan": scan_text(text), "status": detect_status_from_text(text)}


def find_manifest_entries(zip_path: str | Path) -> list[str]:
    with zipfile.ZipFile(zip_path) as zf:
        return [n for n in zf.namelist() if is_manifest_name(n)][:160]


def classify_zip_by_entries(entries: list[str]) -> dict[str, Any]:
    low = "\n".join(entries[:2000]).lower()
    classes: list[str] = []
    if "playwright" in low or "trace.zip" in low or "screenshot" in low:
        classes.append("playwright_evidence")
    if "governance" in low or "canon" in low:
        classes.append("governance_canon")
    if "verify" in low or "verification" in low or "result" in low:
        classes.append("prismo_verify_report")
    if "dependency" in low or "atlas" in low:
        classes.append("dependency_atlas")
    if "descargasf" in low or "files/descargasf" in low:
        classes.append("downloads_inventory")
    if "files/repo" in low or "prisma-control-center" in low:
        classes.append("repo_inventory")
    if "codex" in low:
        classes.append("codex_report")
    return {"classes": classes or ["unknown_prismo_related"]}


def _pick_text_entries(entries: list[str]) -> list[str]:
    priority: list[str] = []
    for e in entries:
        low = e.lower()
        if not low.endswith(SAFE_ZIP_TEXT_SUFFIXES):
            continue
        if is_manifest_name(e) or is_report_name(e) or any(k in low for k in ("continuation", "readme", "install", "result", "fail", "summary", "verification", "verify")):
            priority.append(e)
    # Dedup while preserving order; cap keeps RAM sane.
    out = []
    seen = set()
    for e in priority:
        if e not in seen:
            seen.add(e); out.append(e)
        if len(out) >= 140:
            break
    return out


def inspect_zip(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    report: dict[str, Any] = {
        "ok": False,
        "source_path": str(p),
        "entry_count": 0,
        "total_uncompressed_bytes": 0,
        "entries_preview": [],
        "manifest_entries": [],
        "report_entries": [],
        "playwright_entries": [],
        "forbidden_entries": [],
        "small_text_samples": [],
        "status": "UNKNOWN",
        "warnings": [],
        "read_only": True,
        "executed": False,
        "extracted": False,
    }
    try:
        with zipfile.ZipFile(p) as zf:
            infos = zf.infolist()
            report["ok"] = True
            report["entry_count"] = len(infos)
            report["total_uncompressed_bytes"] = sum(i.file_size for i in infos)
            entries = [i.filename for i in infos]
            report["entries_preview"] = entries[:360]
            report["manifest_entries"] = [e for e in entries if is_manifest_name(e)][:120]
            report["report_entries"] = [e for e in entries if is_report_name(e)][:120]
            report["playwright_entries"] = [e for e in entries if is_playwright_name(e)][:120]
            report["forbidden_entries"] = [e for e in entries if any(h in e.lower() for h in FORBIDDEN_ZIP_NAMES)][:120]
            if len(infos) > MAX_ZIP_ENTRIES:
                report["warnings"].append("zip_entry_limit_exceeded_sampled_metadata_only")
            if report["total_uncompressed_bytes"] and p.exists() and p.stat().st_size:
                report["compression_ratio"] = round(report["total_uncompressed_bytes"] / max(p.stat().st_size, 1), 2)
                if report["compression_ratio"] > 50:
                    report["warnings"].append("high_compression_ratio_review_only")
            total_read = 0
            for entry in _pick_text_entries(entries):
                if total_read >= MAX_TOTAL_ZIP_READ_BYTES:
                    report["warnings"].append("zip_text_read_budget_exhausted")
                    break
                try:
                    info = zf.getinfo(entry)
                    if info.file_size <= MAX_ZIP_TEXT_ENTRY_BYTES:
                        text = zf.read(entry).decode("utf-8", errors="replace")
                        total_read += len(text.encode("utf-8", errors="replace"))
                        sample = {"entry": entry, "size_bytes": info.file_size, "status": detect_status_from_text(text), "preview": redact(text)[:3200]}
                        sample["secret_scan"] = scan_text(text)
                        report["small_text_samples"].append(sample)
                except Exception as exc:
                    report["warnings"].append(f"entry_read_failed:{entry}:{exc}")
            statuses = [s.get("status") for s in report["small_text_samples"]]
            if "FAIL" in statuses:
                report["status"] = "FAIL"
            elif "PARTIAL" in statuses or "WARN" in statuses:
                report["status"] = "PARTIAL"
            elif "PASS" in statuses:
                report["status"] = "PASS"
            report.update(classify_zip_by_entries(entries))
    except Exception as exc:
        report["error"] = str(exc)
    return report
