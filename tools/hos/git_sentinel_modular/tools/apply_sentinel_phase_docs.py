\
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Git Sentinel phase docs installer and validator.

What it does
------------
- Finds the repo root and modular scaffold root automatically.
- Finds phase ZIPs passed as args or auto-discovers `sentinel_phase_*.zip`.
- Validates each phase manifest and every file checksum.
- Extracts documents into the scaffold root in the documented locations.
- Produces JSON and Markdown reports.
- Runs validation tests:
  * expected files exist
  * markdown internal links are valid
  * target paths stay inside the scaffold root
  * referenced module targets from manifests exist or are explicitly planned

Exit code
---------
0 = success
1 = validation/install error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

DEFAULT_REPO = Path(r"F:\repos\hitech-os")
DEFAULT_OUT = Path(r"F:\OneDrive\Descargas")

PHASE_PATTERN = "sentinel_phase_*.zip"
SCAFFOLD_CANONICAL = Path("tools/hos/git_sentinel_modular")


@dataclass
class Finding:
    level: str
    phase: str
    path: str
    message: str


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_repo_root() -> Path:
    """
    Detect the repository root by checking for .git and tools/hos markers.
    
    Searches upward from the script's location first (portable), then falls back
    to DEFAULT_REPO (environment-specific hardcoded path) as a last resort.
    Avoids dependency on current working directory.
    """
    candidates = []
    
    # Start from script location and search upward (portable)
    script_location = Path(__file__).resolve().parent
    candidates.append(script_location)
    candidates.extend(script_location.parents)
    
    # Fallback to DEFAULT_REPO (environment-local, for development shortcut)
    candidates.append(DEFAULT_REPO)

    for cand in candidates:
        if (cand / ".git").exists() and (cand / "tools" / "hos").exists():
            return cand.resolve()

    raise FileNotFoundError(
        f"Could not detect repo root. Searched upward from {script_location} and fallback {DEFAULT_REPO}. "
        f"No .git and tools/hos markers found."
    )


def detect_scaffold_root(repo_root: Path) -> Path:
    canonical = repo_root / SCAFFOLD_CANONICAL
    if canonical.exists():
        return canonical.resolve()

    parent = repo_root / "tools" / "hos"
    if not parent.exists():
        raise FileNotFoundError(f"No existe `{parent}`.")

    matches = sorted(parent.glob("git_sentinel_modular*"))
    if matches:
        return matches[-1].resolve()

    raise FileNotFoundError(
        f"No encontré scaffold modular en `{parent}`. Esperaba `{canonical}` o un variante timestamped."
    )


def discover_zip_candidates(search_roots: Iterable[Path]) -> list[Path]:
    found: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        for p in sorted(root.glob(PHASE_PATTERN)):
            if p.is_file():
                found.append(p.resolve())
    return found


def load_manifest_from_zip(zip_path: Path) -> dict:
    with zipfile.ZipFile(zip_path, "r") as zf:
        try:
            raw = zf.read("phase_manifest.json").decode("utf-8")
        except KeyError as exc:
            raise ValueError(f"Falta `phase_manifest.json` en `{zip_path}`.") from exc
    return json.loads(raw)


def extract_zip(zip_path: Path, dst: Path) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dst)


def validate_manifest_files(extracted: Path, manifest: dict, phase: str) -> list[Finding]:
    findings: list[Finding] = []
    for item in manifest.get("documents", []):
        src = extracted / item["zip_path"]
        if not src.exists():
            findings.append(Finding("ERROR", phase, str(src), "Archivo esperado por manifest no existe."))
            continue
        digest = sha256_file(src)
        if digest != item["sha256"]:
            findings.append(
                Finding(
                    "ERROR",
                    phase,
                    str(src),
                    f"Checksum no coincide. esperado={item['sha256']} actual={digest}",
                )
            )
    return findings


def safe_join(base: Path, rel: str) -> Path:
    candidate = (base / rel).resolve()
    if str(candidate).startswith(str(base.resolve())):
        return candidate
    raise ValueError(f"Ruta objetivo sale del scaffold permitido: `{rel}` -> `{candidate}`")


def install_phase_docs(extracted: Path, scaffold_root: Path, manifest: dict, phase: str) -> tuple[list[str], list[Finding]]:
    installed: list[str] = []
    findings: list[Finding] = []
    for item in manifest.get("documents", []):
        src = extracted / item["zip_path"]
        if item["zip_path"] == "phase_manifest.json":
            target = scaffold_root / "docs" / "phases" / phase / "phase_manifest.json"
        else:
            try:
                target = safe_join(scaffold_root, item["target_relative_path"])
            except ValueError as exc:
                findings.append(Finding("ERROR", phase, item["target_relative_path"], str(exc)))
                continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        installed.append(str(target))
    return installed, findings


def markdown_links(md_text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", md_text)


def validate_markdown_links(scaffold_root: Path, phase: str) -> list[Finding]:
    findings: list[Finding] = []
    phase_docs = scaffold_root / "docs" / "phases" / phase
    if not phase_docs.exists():
        findings.append(Finding("ERROR", phase, str(phase_docs), "No existe carpeta de docs de fase instalada."))
        return findings

    for md in phase_docs.rglob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        for link in markdown_links(text):
            if link.startswith("http://") or link.startswith("https://") or link.startswith("#"):
                continue
            target = (md.parent / link).resolve()
            if not target.exists():
                findings.append(Finding("ERROR", phase, str(md), f"Broken markdown link -> {link}"))
    return findings


def validate_expected_targets(scaffold_root: Path, manifest: dict, phase: str) -> list[Finding]:
    findings: list[Finding] = []
    for rel in manifest.get("expected_targets", []):
        target = scaffold_root / rel
        # target may not exist yet as code and that's acceptable if it's documented/planned under scaffold
        parent_ok = target.parent.exists()
        if not parent_ok:
            findings.append(Finding("ERROR", phase, str(target), "Target documentado cae en carpeta inexistente."))
    return findings


def render_markdown_report(report: dict) -> str:
    lines = [
        "# Sentinel phase docs install report",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- repo_root: `{report['repo_root']}`",
        f"- scaffold_root: `{report['scaffold_root']}`",
        f"- success: `{report['success']}`",
        "",
        "## Installed files",
    ]
    for phase, items in report["installed_files"].items():
        lines.append(f"### {phase}")
        for item in items:
            lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Findings")
    if not report["findings"]:
        lines.append("- none")
    else:
        for f in report["findings"]:
            lines.append(f"- **{f['level']}** | `{f['phase']}` | `{f['path']}` | {f['message']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Install and validate Sentinel phase docs zips.")
    parser.add_argument("zips", nargs="*", help="Optional explicit phase zip paths.")
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    parser.add_argument("--scaffold-root", default="", help="Optional scaffold root override.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT), help="Directory for reports.")
    args = parser.parse_args(argv)

    findings: list[Finding] = []
    installed_files: dict[str, list[str]] = {}

    try:
        repo_root = Path(args.repo_root).resolve() if args.repo_root else detect_repo_root()
        scaffold_root = Path(args.scaffold_root).resolve() if args.scaffold_root else detect_scaffold_root(repo_root)
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    zip_paths: list[Path] = []
    if args.zips:
        zip_paths = [Path(z).resolve() for z in args.zips]
    else:
        search_roots = [Path.cwd(), Path(__file__).resolve().parent, DEFAULT_OUT]
        zip_paths = discover_zip_candidates(search_roots)

    if not zip_paths:
        print("[FAIL] No encontré phase zips. Pásalos explícitamente o colócalos junto al script / en Descargas.", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory(prefix="sentinel_phase_docs_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        for zip_path in zip_paths:
            if not zip_path.exists():
                findings.append(Finding("ERROR", "unknown", str(zip_path), "ZIP no existe."))
                continue

            try:
                manifest = load_manifest_from_zip(zip_path)
            except Exception as exc:
                findings.append(Finding("ERROR", "unknown", str(zip_path), str(exc)))
                continue

            phase = manifest.get("phase_tag", "unknown")
            extract_dir = tmp_root / phase
            extract_dir.mkdir(parents=True, exist_ok=True)
            try:
                extract_zip(zip_path, extract_dir)
            except Exception as exc:
                findings.append(Finding("ERROR", phase, str(zip_path), f"No pude extraer ZIP: {exc}"))
                continue

            findings.extend(validate_manifest_files(extract_dir, manifest, phase))
            installed, install_findings = install_phase_docs(extract_dir, scaffold_root, manifest, phase)
            installed_files[phase] = installed
            findings.extend(install_findings)
            findings.extend(validate_markdown_links(scaffold_root, phase))
            findings.extend(validate_expected_targets(scaffold_root, manifest, phase))

    success = not any(f.level == "ERROR" for f in findings)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(repo_root),
        "scaffold_root": str(scaffold_root),
        "installed_files": installed_files,
        "findings": [asdict(f) for f in findings],
        "success": success,
    }

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"sentinel_phase_install_report_{stamp}.json"
    md_path = out_dir / f"sentinel_phase_install_report_{stamp}.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown_report(report), encoding="utf-8")

    print(f"[OK] JSON report: {json_path}")
    print(f"[OK] Markdown report: {md_path}")

    if success:
        print("[OK] Instalación y validación completadas sin errores.")
        return 0

    print("[FAIL] Hay errores. Revisa el reporte para ruta exacta, fase exacta y mensaje puntual.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
