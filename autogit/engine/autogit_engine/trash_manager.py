from __future__ import annotations
from pathlib import Path
import datetime as dt, hashlib, json, os, shutil
from .paths import repo_path

class TrashManager:
    def __init__(self, repo: Path, trash_root: Path, run_id: str):
        self.repo = repo
        self.root = trash_root / f"autogit {run_id}"
        self.rows = []

    def _ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def sha(self, path: Path) -> str:
        if not path.is_file():
            return ""
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def move(self, rel_path: str, reason: str) -> dict:
        self._ensure_root()
        src = repo_path(self.repo, rel_path)
        dst = repo_path(self.root, rel_path)
        if not src.exists():
            row = {"rel_path": rel_path, "missing": True, "reason": reason}
            self.rows.append(row)
            return row
        dst.parent.mkdir(parents=True, exist_ok=True)
        row = {"rel_path": rel_path, "original_path": str(src), "trash_path": str(dst), "sha256": self.sha(src), "reason": reason}
        shutil.move(str(src), str(dst))
        self.rows.append(row)
        return row

    def write_manifest(self) -> None:
        if not self.rows:
            return
        self._ensure_root()
        (self.root / "manifest.json").write_text(json.dumps(self.rows, indent=2, ensure_ascii=False), encoding="utf-8")
        lines = ["# AutoGit Trash Manifest", "", f"Created: {dt.datetime.now().isoformat(timespec='seconds')}", ""]
        for row in self.rows:
            lines.append(f"- `{row.get('rel_path')}` -> `{row.get('trash_path')}` : {row.get('reason')}")
        (self.root / "manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
