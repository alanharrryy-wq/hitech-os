from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from .registry import APP_REL, KNOWN_LIVE_DB_CANDIDATES, SENTINEL_REL

SECRET_PATTERNS = [
    re.compile(r"(?i)(?:token|secret|password|passwd|api[_-]?key)\s*[:=]\s*['\"]?([^\s'\"]{8,})"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bsk-proj-[A-Za-z0-9_-]{16,}\b"),
]


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        shell=False,
    )


def detect_repo(candidate: str | Path | None = None) -> Path:
    starts = []
    if candidate:
        starts.append(Path(candidate).resolve())
    starts.append(Path.cwd().resolve())
    for start in starts:
        cp = run(["git", "-C", str(start), "rev-parse", "--show-toplevel"], timeout=20)
        if cp.returncode == 0 and cp.stdout.strip():
            root = Path(cp.stdout.strip()).resolve()
            if (root / APP_REL).is_dir() and (root / "PRISMA Factory Ledger").is_dir():
                return root
    raise RuntimeError("BLOCKED_INVALID_REPO_ROOT: canonical hitech-os markers were not found")


def ensure_below(path: Path, root: Path, label: str) -> Path:
    p = path.resolve()
    r = root.resolve()
    try:
        p.relative_to(r)
    except ValueError as exc:
        raise RuntimeError(f"BLOCKED_PATH_ESCAPE:{label}:{p}") from exc
    return p


def ensure_temp_db(path: Path, temp_root: Path, label: str) -> Path:
    p = ensure_below(path, temp_root, label)
    if p.suffix.lower() not in {".db", ".sqlite", ".sqlite3"}:
        raise RuntimeError(f"BLOCKED_NON_SQLITE_TEMP_DB:{label}:{p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def git_head(repo: Path) -> str:
    cp = run(["git", "-C", str(repo), "rev-parse", "HEAD"], timeout=20)
    if cp.returncode != 0:
        raise RuntimeError(f"git rev-parse failed: {cp.stderr.strip()}")
    return cp.stdout.strip()


def git_tree(repo: Path) -> str:
    cp = run(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], timeout=20)
    return cp.stdout.strip() if cp.returncode == 0 else ""


def tracked_diff(repo: Path) -> list[str]:
    cp = run(["git", "-C", str(repo), "diff", "--name-only", "--"], timeout=30)
    if cp.returncode != 0:
        raise RuntimeError(f"git diff failed: {cp.stderr.strip()}")
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def untracked(repo: Path) -> list[str]:
    cp = run(["git", "-C", str(repo), "ls-files", "--others", "--exclude-standard"], timeout=30)
    if cp.returncode != 0:
        return []
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def hash_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def snapshot_files(repo: Path, rels: Iterable[Path]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for rel in rels:
        p = repo / rel
        key = rel.as_posix()
        out[key] = {
            "exists": p.exists(),
            "size": p.stat().st_size if p.is_file() else None,
            "sha256": hash_file(p),
            "mtime_ns": p.stat().st_mtime_ns if p.exists() else None,
        }
    return out


def known_live_db_snapshot(repo: Path) -> dict[str, dict[str, object]]:
    return snapshot_files(repo, KNOWN_LIVE_DB_CANDIDATES)


def snapshots_equal(a: dict, b: dict) -> bool:
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def scan_secrets_text(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(match.group(0)[:24] + "…")
    return findings


def sanitize_text(text: str) -> str:
    clean = text
    for pattern in SECRET_PATTERNS:
        clean = pattern.sub("[REDACTED_SECRET]", clean)
    clean = re.sub(r"(?i)Authorization:\s*Bearer\s+\S+", "Authorization: Bearer [REDACTED]", clean)
    return clean


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def repo_clean_for_certification(repo: Path) -> tuple[bool, dict[str, list[str]]]:
    diff = tracked_diff(repo)
    others = untracked(repo)
    permitted_untracked_prefix = SENTINEL_REL.as_posix().rstrip("/") + "/"
    bad_untracked = [p for p in others if not p.startswith(permitted_untracked_prefix)]
    return not diff and not bad_untracked, {"trackedDiff": diff, "untrackedOutsideSentinel": bad_untracked}


def stop_owned_process(proc, timeout: float = 8.0) -> dict[str, object]:
    if proc.poll() is not None:
        return {"pid": proc.pid, "alreadyExited": True, "returncode": proc.returncode}
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
        return {"pid": proc.pid, "terminated": True, "returncode": proc.returncode}
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
        return {"pid": proc.pid, "killed": True, "returncode": proc.returncode}
