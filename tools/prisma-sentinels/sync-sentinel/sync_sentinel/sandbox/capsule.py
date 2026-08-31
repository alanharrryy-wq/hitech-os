from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .dependency_probe import probe_dependencies
from .prisma_runtime import install_workspace
from .processes import OwnedProcessRegistry
from .source_guard import repository_snapshot, snapshots_match


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git(repo: Path, *args: str, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


@dataclass
class CapsuleResult:
    source_head: str
    worktree_head: str | None = None
    install_ok: bool = False
    dependency_ok: bool = False
    cleanup_pass: bool = False
    source_drift: bool = False
    orphan_processes: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    manifest: dict[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return (
            self.install_ok
            and self.dependency_ok
            and self.cleanup_pass
            and not self.source_drift
            and not self.orphan_processes
            and not self.errors
        )


class RuntimeCapsule:
    """Sentinel-owned detached worktree and runtime resources.

    The operator checkout is treated as immutable evidence. All dependency install,
    Prisma generation, temporary databases and owned processes live under a disposable
    capsule rooted in the system temporary directory.
    """

    def __init__(self, source_repo: Path, source_sha: str | None = None, *, keep: bool = False):
        self.source_repo = source_repo.resolve()
        head_cp = _git(self.source_repo, "rev-parse", "HEAD", timeout=30)
        if head_cp.returncode:
            raise RuntimeError(f"BLOCKED_CAPSULE_SOURCE_HEAD:{head_cp.stderr.strip()[:300]}")
        self.source_sha = source_sha or head_cp.stdout.strip()
        self.keep = keep
        self.temp_root: Path | None = None
        self.worktree: Path | None = None
        self.data_root: Path | None = None
        self.logs_root: Path | None = None
        self.before = repository_snapshot(self.source_repo)
        self.processes = OwnedProcessRegistry()
        self.result = CapsuleResult(source_head=self.source_sha)
        self._setup_complete = False
        self._cleaned = False

    def setup(self) -> CapsuleResult:
        if self._setup_complete:
            return self.result
        if str(self.before.get("head")) != self.source_sha:
            raise RuntimeError(
                f"BLOCKED_CAPSULE_SOURCE_SHA_MISMATCH:{self.source_sha}:{self.before.get('head')}"
            )
        self.temp_root = Path(tempfile.mkdtemp(prefix="prisma-sync-sentinel-capsule-"))
        self.worktree = self.temp_root / "worktree"
        self.data_root = self.temp_root / "data"
        self.logs_root = self.temp_root / "logs"
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.logs_root.mkdir(parents=True, exist_ok=True)
        cp = _git(self.source_repo, "worktree", "add", "--detach", str(self.worktree), self.source_sha, timeout=180)
        if cp.returncode:
            self.result.errors.append("WORKTREE_ADD_FAILED:" + (cp.stderr or cp.stdout)[-800:])
            raise RuntimeError(self.result.errors[-1])
        head_cp = _git(self.worktree, "rev-parse", "HEAD", timeout=30)
        self.result.worktree_head = head_cp.stdout.strip() if head_cp.returncode == 0 else None
        if self.result.worktree_head != self.source_sha:
            self.result.errors.append(
                f"WORKTREE_HEAD_MISMATCH:{self.source_sha}:{self.result.worktree_head}"
            )
            raise RuntimeError(self.result.errors[-1])

        install = install_workspace(self.worktree)
        self.result.install_ok = bool(install.get("ok"))
        dependencies = probe_dependencies(self.worktree) if self.result.install_ok else {
            "schemaVersion": "prisma.sync-sentinel.dependency-resolution.v1",
            "ok": False,
            "blockedBy": "workspace_install",
        }
        self.result.dependency_ok = bool(dependencies.get("ok"))
        self.result.manifest = {
            "schemaVersion": "prisma.sync-sentinel.sandbox.v1",
            "createdAt": _now(),
            "sourceHead": self.source_sha,
            "worktreeHead": self.result.worktree_head,
            # Preserve owner-by-owner frozen-install output. Evidence bundling performs
            # sanitization later, so future dependency failures remain causal instead
            # of collapsing to a bare return code.
            "workspaceInstall": install,
            "dependencyResolution": dependencies,
            "ownership": {
                "worktree": "sentinel-owned-temporary",
                "databases": "sentinel-owned-temporary-sqlite-only",
                "processes": "sentinel-owned-only",
                "ports": "loopback-only",
            },
            "guards": {
                "prismaAutoInstall": False,
                "manifestMutationAllowed": False,
                "lockfileMutationAllowed": False,
                "liveDatabaseMutationAllowed": False,
                "globalProcessKillAllowed": False,
                "productionCertified": False,
            },
            "paths": {
                "worktree": "SENTINEL_CAPSULE/worktree",
                "data": "SENTINEL_CAPSULE/data",
                "logs": "SENTINEL_CAPSULE/logs",
            },
        }
        if not self.result.install_ok:
            self.result.errors.append("WORKSPACE_INSTALL_FAILED")
        if not self.result.dependency_ok:
            self.result.errors.append("DEPENDENCY_RESOLUTION_FAILED")
        self._setup_complete = True
        return self.result

    def cleanup(self) -> CapsuleResult:
        if self._cleaned:
            return self.result
        cleanup = self.processes.stop_all()
        self.result.orphan_processes = [int(pid) for pid in cleanup.get("orphanPids", [])]

        capsule_status: list[str] = []
        if self.worktree and self.worktree.exists():
            cp = _git(self.worktree, "status", "--porcelain=v1", "--untracked-files=all", timeout=60)
            if cp.returncode == 0:
                capsule_status = [line for line in cp.stdout.splitlines() if line.strip()]

        removed = False
        cleanup_error: str | None = None
        if not self.keep and self.temp_root:
            try:
                if self.worktree and self.worktree.exists():
                    shutil.rmtree(self.worktree)
                _git(self.source_repo, "worktree", "prune", timeout=60)
                if self.temp_root.exists():
                    shutil.rmtree(self.temp_root)
                removed = not self.temp_root.exists()
            except Exception as exc:  # cleanup must be evidence, not hidden
                cleanup_error = f"{type(exc).__name__}:{exc}"
        elif self.keep:
            cleanup_error = "FORENSIC_KEEP_REQUESTED"

        after = repository_snapshot(self.source_repo)
        self.result.source_drift = not snapshots_match(self.before, after, ignore_status=True)
        self.result.cleanup_pass = (
            removed
            and cleanup_error is None
            and not self.result.source_drift
            and not self.result.orphan_processes
        )
        if cleanup_error:
            self.result.errors.append("CAPSULE_CLEANUP:" + cleanup_error)
        if self.result.source_drift:
            self.result.errors.append("SOURCE_OR_LOCKFILE_DRIFT")
        if self.result.orphan_processes:
            self.result.errors.append("ORPHAN_SENTINEL_PROCESSES")
        self.result.manifest["cleanup"] = {
            "completedAt": _now(),
            "capsuleStatusCountBeforeDestroy": len(capsule_status),
            "capsuleRemoved": removed,
            "sourceDrift": self.result.source_drift,
            "orphanProcesses": self.result.orphan_processes,
            "pass": self.result.cleanup_pass,
            "forensicKeepRequested": self.keep,
        }
        self._cleaned = True
        return self.result

    def __enter__(self) -> "RuntimeCapsule":
        self.setup()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None:
            self.result.errors.append(f"CAPSULE_RUNTIME:{exc_type.__name__ if exc_type else 'Error'}:{exc}")
        self.cleanup()
