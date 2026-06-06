from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_contracts import build_operation_spec
from capatch_engine import apply as engine_apply
from capatch_engine import preflight, preview


@dataclass(slots=True)
class PatchCtx:
    root_dir: Path
    backup_dir: Path
    checkpoint_dir: Path
    dry_run: bool = False
    auto_support: bool = True
    requested_by: str | None = "qa"
    invocation_mode: str = "patch-run"
    run_id: str | None = None


class FixtureWorkspace:
    def __init__(self, fixture_name: str) -> None:
        self.fixture_name = fixture_name
        self._tmp = tempfile.TemporaryDirectory(prefix=f"capatch_fixture_{fixture_name}_")
        self.root = Path(self._tmp.name) / fixture_name

    def __enter__(self) -> Path:
        source = FIXTURES / self.fixture_name
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copytree(source, self.root, dirs_exist_ok=True)
        return self.root

    def __exit__(self, exc_type, exc, tb) -> None:
        self._tmp.cleanup()


def fixture_workspace(fixture_name: str) -> FixtureWorkspace:
    return FixtureWorkspace(fixture_name)


def backup_root_for(root_dir: Path) -> Path:
    root_dir = Path(root_dir).resolve()
    modern = root_dir / ".capatch" / "backups" / "patches"
    legacy = root_dir / "_chatgpt_patch_backups"
    if modern.exists():
        modern.mkdir(parents=True, exist_ok=True)
        return modern
    legacy.mkdir(parents=True, exist_ok=True)
    return legacy


def make_ctx(root_dir: Path, *, dry_run: bool = False, checkpoint_label: str = "qa_checkpoint") -> PatchCtx:
    root_dir = Path(root_dir).resolve()
    backup_dir = backup_root_for(root_dir)
    checkpoint_dir = backup_dir / checkpoint_label
    return PatchCtx(
        root_dir=root_dir,
        backup_dir=backup_dir,
        checkpoint_dir=checkpoint_dir,
        dry_run=dry_run,
    )


def build_ops(rows: Iterable[dict[str, Any]]) -> list[Any]:
    return [build_operation_spec(row) for row in rows]


def apply_ops(root_dir: Path, rows: Iterable[dict[str, Any]], *, dry_run: bool = False):
    ctx = make_ctx(root_dir, dry_run=dry_run)
    operations = build_ops(rows)
    pf = preflight(ctx, operations)
    pv = preview(ctx, operations)
    results = engine_apply(ctx, operations)
    return ctx, operations, pf, pv, results


def read_text(path_value: Path) -> str:
    return Path(path_value).read_text(encoding="utf-8")


def read_json(path_value: Path) -> Any:
    return json.loads(read_text(path_value))


def write_text(path_value: Path, content: str) -> None:
    path_value = Path(path_value)
    path_value.parent.mkdir(parents=True, exist_ok=True)
    path_value.write_text(content, encoding="utf-8", newline="")


def write_bytes(path_value: Path, content: bytes) -> None:
    path_value = Path(path_value)
    path_value.parent.mkdir(parents=True, exist_ok=True)
    path_value.write_bytes(content)


def repo_python() -> str:
    return sys.executable


def bool_env(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def run_command(argv: list[str], *, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(argv),
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
