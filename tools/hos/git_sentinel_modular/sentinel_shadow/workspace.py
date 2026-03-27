from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from .config import shadow_root

@dataclass(slots=True)
class ShadowWorkspace:
    run_id: str
    workspace_root: Path
    baseline_root: Path
    candidate_root: Path
    overlay_root: Path
    metadata_root: Path

    def to_dict(self) -> dict[str, str]:
        return {
            "run_id": self.run_id,
            "workspace_root": str(self.workspace_root),
            "baseline_root": str(self.baseline_root),
            "candidate_root": str(self.candidate_root),
            "overlay_root": str(self.overlay_root),
            "metadata_root": str(self.metadata_root),
        }

def _copy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        return
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        destination = target / relative
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)

def create_shadow_workspace(run_id: str, source_root: str | Path | None = None) -> ShadowWorkspace:
    root = shadow_root() / run_id
    baseline_root = root / "baseline"
    candidate_root = root / "candidate"
    overlay_root = root / "overlay"
    metadata_root = root / "metadata"
    for path in (baseline_root, candidate_root, overlay_root, metadata_root):
        path.mkdir(parents=True, exist_ok=True)
    if source_root:
        source_path = Path(source_root)
        _copy_tree(source_path, baseline_root)
        _copy_tree(source_path, candidate_root)
    return ShadowWorkspace(
        run_id=run_id,
        workspace_root=root,
        baseline_root=baseline_root,
        candidate_root=candidate_root,
        overlay_root=overlay_root,
        metadata_root=metadata_root,
    )

def bootstrap_from_modular_source(source_root: str | Path | None = None, run_id: str = "bootstrap") -> ShadowWorkspace:
    return create_shadow_workspace(run_id=run_id, source_root=source_root)
