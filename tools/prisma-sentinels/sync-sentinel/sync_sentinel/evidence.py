from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .safety import sanitize_text, scan_secrets_text


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# PRISMA Sync Sentinel Evidence",
        "",
        f"- status: **{report.get('status', report.get('verdict', 'UNKNOWN'))}**",
        f"- generatedAt: `{report.get('generatedAt', '')}`",
        f"- repoHead: `{report.get('repoHead', '')}`",
        f"- liveDbTouched: `{str(report.get('liveDbTouched')).lower()}`",
        f"- sourceDrift: `{str(report.get('sourceDrift')).lower()}`",
        f"- cleanupPass: `{str(report.get('cleanupPass')).lower()}`",
        f"- orphanProcesses: `{str(report.get('orphanProcesses')).lower()}`",
        f"- secretFindings: `{report.get('secretFindings', 0)}`",
        f"- productionCertified: `{str(report.get('productionCertified', False)).lower()}`",
        "",
        "## Checks",
        "",
    ]
    for check in report.get("checks", []):
        lines.append(f"- **{check.get('id')}**: `{check.get('verdict')}` — {check.get('detail')}")
    lines.extend([
        "",
        "## Scope statement",
        "",
        "This bundle certifies an isolated synthetic Tablet↔PC sync exercise and repository/native-verifier evidence only. It does not certify hosted/customer production operation.",
        "",
    ])
    return "\n".join(lines)


def build_bundle(out_dir: Path, report: dict[str, Any], extra_files: list[Path] | None = None) -> tuple[Path, int, list[str]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    report = dict(report)
    report.setdefault("generatedAt", now_iso())
    json_path = out_dir / "SYNC_SENTINEL_REPORT.json"
    md_path = out_dir / "SYNC_SENTINEL_REPORT.md"
    atomic_write_json(json_path, report)
    atomic_write_text(md_path, render_markdown(report))

    files = [json_path, md_path]
    for p in extra_files or []:
        if p.is_file():
            files.append(p)

    sanitized_findings: list[str] = []
    for p in files:
        if p.suffix.lower() in {".json", ".md", ".txt", ".log"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            local_findings = scan_secrets_text(text)
            if local_findings:
                sanitized_findings.extend(f"{p.name}:{item}" for item in local_findings)
                atomic_write_text(p, sanitize_text(text))

    remaining_findings: list[str] = []
    for p in files:
        if p.suffix.lower() in {".json", ".md", ".txt", ".log"}:
            for item in scan_secrets_text(p.read_text(encoding="utf-8", errors="replace")):
                remaining_findings.append(f"{p.name}:{item}")

    manifest = {
        "schemaVersion": "prisma.sync-sentinel.evidence.v1",
        "createdAt": now_iso(),
        "sanitizedFindingCount": len(sanitized_findings),
        "remainingSecretFindings": len(remaining_findings),
        "files": [],
    }
    for p in files:
        raw = p.read_bytes()
        manifest["files"].append({"name": p.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    manifest_path = out_dir / "SYNC_SENTINEL_MANIFEST.json"
    atomic_write_json(manifest_path, manifest)
    files.append(manifest_path)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    final_zip = out_dir / f"SYNC_SENTINEL_EVIDENCE_{stamp}.zip"
    tmp_zip = out_dir / (final_zip.name + ".tmp")
    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zf.write(p, arcname=p.name)
    os.replace(tmp_zip, final_zip)
    return final_zip, len(remaining_findings), remaining_findings
