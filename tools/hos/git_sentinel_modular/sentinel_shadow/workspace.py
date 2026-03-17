from dataclasses import dataclass
from pathlib import Path
import shutil
import time
import uuid

from .config import shadow_root, modular_root

IGNORE_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

@dataclass
class ShadowWorkspace:
    run_id: str
    root: Path
    baseline_dir: Path
    candidate_dir: Path
    manifests_dir: Path

def _copy_tree(src: Path, dst: Path):
    src = Path(src)
    dst = Path(dst)

    for path in src.rglob("*"):
        rel = path.relative_to(src)

        if any(part in IGNORE_NAMES for part in rel.parts):
            continue

        target = dst / rel

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

def create_shadow_workspace(run_id: str | None = None) -> ShadowWorkspace:
    if not run_id:
        run_id = time.strftime("shadow_%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:8]

    root = shadow_root() / run_id
    baseline_dir = root / "baseline"
    candidate_dir = root / "candidate"
    manifests_dir = root / "manifests"

    baseline_dir.mkdir(parents=True, exist_ok=True)
    candidate_dir.mkdir(parents=True, exist_ok=True)
    manifests_dir.mkdir(parents=True, exist_ok=True)

    return ShadowWorkspace(
        run_id=run_id,
        root=root,
        baseline_dir=baseline_dir,
        candidate_dir=candidate_dir,
        manifests_dir=manifests_dir,
    )

def bootstrap_from_modular_source(
    run_id: str | None = None,
    source_root: Path | None = None,
) -> ShadowWorkspace:
    source_root = Path(source_root or modular_root())
    workspace = create_shadow_workspace(run_id=run_id)

    _copy_tree(source_root, workspace.baseline_dir)
    _copy_tree(source_root, workspace.candidate_dir)

    return workspace
