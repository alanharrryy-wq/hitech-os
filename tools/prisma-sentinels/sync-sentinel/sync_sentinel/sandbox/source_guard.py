from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Iterable

WATCHED_DEFAULT = (
    Path("pnpm-lock.yaml"),
    Path("package.json"),
    Path("apps/terminal-de-venta-system/package.json"),
    Path("apps/terminal-de-venta-system/products/pc/app/package.json"),
    Path("apps/terminal-de-venta-system/products/tablet/app/package.json"),
)


def _git(repo: Path, *args: str, timeout: int = 60) -> str:
    cp = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if cp.returncode:
        raise RuntimeError(f"GIT_FAILED:{' '.join(args)}:{cp.stderr.strip()[:500]}")
    return cp.stdout.strip()


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def repository_snapshot(repo: Path, watched: Iterable[Path] = WATCHED_DEFAULT) -> dict[str, object]:
    repo = repo.resolve()
    files: dict[str, object] = {}
    for rel in watched:
        p = repo / rel
        files[rel.as_posix()] = {
            "exists": p.is_file(),
            "sha256": _sha256(p),
            "bytes": p.stat().st_size if p.is_file() else None,
        }
    status = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return {
        "head": _git(repo, "rev-parse", "HEAD"),
        "tree": _git(repo, "rev-parse", "HEAD^{tree}"),
        "trackedDiff": _git(repo, "diff", "--name-only").splitlines(),
        "status": [line for line in status.splitlines() if line.strip()],
        "files": files,
    }


def snapshots_match(before: dict[str, object], after: dict[str, object], *, ignore_status: bool = False) -> bool:
    left = dict(before)
    right = dict(after)
    if ignore_status:
        left.pop("status", None)
        right.pop("status", None)
    return json.dumps(left, sort_keys=True, separators=(",", ":")) == json.dumps(right, sort_keys=True, separators=(",", ":"))
