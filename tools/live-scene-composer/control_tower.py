#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Sequence

DEFAULT_REPO_ROOT = Path(r"F:\\repos\\hitech-os")
TOOLS_NAMESPACE = Path("tools") / "live-scene-composer"
DOCS_NAMESPACE = Path("docs") / "live-scene-composer"

INVENTORY_EXTENSIONS = {
    ".py", ".sh", ".bat", ".md", ".json", ".dot", ".svg", ".txt"
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def detect_repo_root(cli_value: str | None) -> Path:
    candidates: List[Path] = []
    if cli_value:
        candidates.append(Path(cli_value))
    env_value = None
    try:
        env_value = __import__("os").environ.get("HITECH_OS_REPO")
    except Exception:
        env_value = None
    if env_value:
        candidates.append(Path(env_value))
    candidates.append(DEFAULT_REPO_ROOT)
    for base in [Path.cwd(), Path(__file__).resolve().parent]:
        candidates.extend([base, *base.parents])

    seen = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except Exception:
            continue
        key = str(resolved).lower()
        if key in seen or not resolved.exists():
            continue
        seen.add(key)
        if (resolved / ".git").exists() and (resolved / "tools").exists():
            return resolved
        if (resolved / "docs").exists() and (resolved / "apps").exists():
            return resolved
        if resolved.name.lower() == "hitech-os":
            return resolved
    raise SystemExit(r"[ERROR] No pude detectar el repo root. Usa --repo-root F:\repos\hitech-os")


def normalize(path: Path) -> str:
    return str(path).replace("\\", "/")


def iter_files(base: Path) -> List[Path]:
    files: List[Path] = []
    if not base.exists():
        return files
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        if "_local/backups" in normalize(path.relative_to(base.parent if base.name == "live-scene-composer" else base)):
            continue
        if path.suffix.lower() in INVENTORY_EXTENSIONS:
            files.append(path)
    return files


def gather_real_inventory(repo_root: Path) -> Dict[str, object]:
    tools_root = repo_root / TOOLS_NAMESPACE
    docs_root = repo_root / DOCS_NAMESPACE
    tools_files = iter_files(tools_root)
    docs_files = iter_files(docs_root)
    return {
        "generated_at_utc": utc_now(),
        "repo_root": str(repo_root),
        "tools_root": str(tools_root),
        "docs_root": str(docs_root),
        "tools_files": [normalize(path.relative_to(repo_root)) for path in tools_files],
        "docs_files": [normalize(path.relative_to(repo_root)) for path in docs_files],
        "tools_count": len(tools_files),
        "docs_count": len(docs_files),
    }


def resolve_script(repo_root: Path, candidates: Sequence[Path]) -> Path:
    for rel in candidates:
        path = repo_root / rel
        if path.exists() and path.is_file():
            return path
    searched = "\n - ".join(normalize(repo_root / item) for item in candidates)
    raise FileNotFoundError("No encontre script canonico. Busque en:\n - " + searched)


def run_python(script_path: Path, args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(script_path), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control tower de Live Scene Composer")
    parser.add_argument("--repo-root", default=None, help="Raiz del repo")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("inventory-real", help="Inventario real del filesystem")
    sub.add_parser("artifacts", help="Genera artifacts de arquitectura")
    sub.add_parser("guard", help="Ejecuta el guard documental/arquitectonico")
    sub.add_parser("full", help="Inventario real + artifacts + guard")
    return parser


def command_inventory_real(repo_root: Path) -> int:
    payload = gather_real_inventory(repo_root)
    evidence_dir = repo_root / TOOLS_NAMESPACE / "_local" / "evidence"
    write_text(evidence_dir / "control_tower_real_inventory.json", json.dumps(payload, indent=2, ensure_ascii=False))
    print("Inventario real generado:")
    print(f"- tools: {payload['tools_count']} archivos")
    print(f"- docs : {payload['docs_count']} archivos")
    print(f"- {evidence_dir / 'control_tower_real_inventory.json'}")
    return 0


def command_artifacts(repo_root: Path) -> int:
    script_path = resolve_script(repo_root, [
        TOOLS_NAMESPACE / "architecture" / "generate_architecture_artifacts.py",
        TOOLS_NAMESPACE / "generate_architecture_artifacts.py",
    ])
    result = run_python(script_path, ["--repo-root", str(repo_root)])
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode


def command_guard(repo_root: Path) -> int:
    script_path = resolve_script(repo_root, [
        TOOLS_NAMESPACE / "policy" / "validate_docs_architecture_guard.py",
        TOOLS_NAMESPACE / "validate_docs_architecture_guard.py",
    ])
    result = run_python(script_path, ["--repo-root", str(repo_root), "--docs-root", "docs/live-scene-composer", "--write-report"])
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)
    return result.returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = detect_repo_root(args.repo_root)

    if args.command == "inventory-real":
        return command_inventory_real(repo_root)
    if args.command == "artifacts":
        return command_artifacts(repo_root)
    if args.command == "guard":
        return command_guard(repo_root)
    if args.command == "full":
        code = command_inventory_real(repo_root)
        if code != 0:
            return code
        code = command_artifacts(repo_root)
        if code != 0:
            return code
        return command_guard(repo_root)
    parser.error("Comando no soportado")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
