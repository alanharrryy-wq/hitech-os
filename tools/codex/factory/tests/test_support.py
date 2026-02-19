from __future__ import annotations

import json
import shutil
import tempfile
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator
from unittest.mock import patch

from factory import attestations, cli, common, config, contracts, doctor, integrator, ledger, locks, orchestrator, preflight, schemas, worktrees

_REAL_REPO_ROOT = common.REPO_ROOT
_REAL_SCHEMA_DIR = _REAL_REPO_ROOT / "tools" / "codex" / "schemas"
_REAL_CONTRACTS_REGISTRY = _REAL_REPO_ROOT / "tools" / "codex" / "contracts" / "factory" / "contracts_registry.json"


def _copy_schema_dir(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for source in sorted(_REAL_SCHEMA_DIR.glob("*.schema.json")):
        shutil.copy2(source, target / source.name)


def _copy_registry(target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_REAL_CONTRACTS_REGISTRY, target / "contracts_registry.json")


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, (dict, list)):
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        return
    path.write_text(str(payload), encoding="utf-8", newline="\n")


@contextmanager
def isolated_factory_env() -> Iterator[dict[str, Path]]:
    with tempfile.TemporaryDirectory(prefix="factory_env_") as temp_dir:
        root = Path(temp_dir).resolve()
        repo_root = root / "repo"
        codex_dir = repo_root / "tools" / "codex"
        runs_dir = codex_dir / "runs"
        schemas_dir = codex_dir / "schemas"
        contracts_factory_dir = codex_dir / "contracts" / "factory"
        templates_dir = codex_dir / "templates" / "factory"
        factory_dir = codex_dir / "factory"

        runs_dir.mkdir(parents=True, exist_ok=True)
        templates_dir.mkdir(parents=True, exist_ok=True)
        factory_dir.mkdir(parents=True, exist_ok=True)
        (repo_root / ".git").mkdir(parents=True, exist_ok=True)
        (repo_root / "docs").mkdir(parents=True, exist_ok=True)
        (codex_dir / "run.py").write_text("print('ok')\n", encoding="utf-8")
        (codex_dir / "validation.json").write_text("{}\n", encoding="utf-8")

        _copy_schema_dir(schemas_dir)
        _copy_registry(contracts_factory_dir)

        with ExitStack() as stack:
            stack.enter_context(patch.object(common, "REPO_ROOT", repo_root))
            stack.enter_context(patch.object(common, "CODEX_DIR", codex_dir))
            stack.enter_context(patch.object(common, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(common, "SCHEMAS_DIR", schemas_dir))
            stack.enter_context(patch.object(common, "CONTRACTS_DIR", contracts_factory_dir))
            stack.enter_context(patch.object(common, "TEMPLATES_DIR", templates_dir))

            stack.enter_context(patch.object(cli, "CODEX_DIR", codex_dir))
            stack.enter_context(patch.object(cli, "RUNS_DIR", runs_dir))

            stack.enter_context(patch.object(config, "REPO_ROOT", repo_root))
            stack.enter_context(patch.object(config, "FACTORY_DIR", codex_dir / "factory"))
            stack.enter_context(patch.object(config, "DEFAULT_CONFIG_PATH", codex_dir / "factory" / "factory.config.json"))

            stack.enter_context(patch.object(contracts, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(contracts, "CONTRACTS_DIR", contracts_factory_dir))

            stack.enter_context(patch.object(preflight, "REPO_ROOT", repo_root))
            stack.enter_context(patch.object(preflight, "CODEX_DIR", codex_dir))
            stack.enter_context(patch.object(preflight, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(preflight, "CONTRACTS_DIR", contracts_factory_dir))

            stack.enter_context(patch.object(schemas, "SCHEMAS_DIR", schemas_dir))

            stack.enter_context(patch.object(ledger, "LEDGER_PATH", runs_dir / "factory_ledger.jsonl"))
            stack.enter_context(patch.object(ledger, "LEDGER_SIGNATURE_PATH", runs_dir / "factory_ledger.sha256"))
            stack.enter_context(patch.object(ledger, "LEDGER_LOCK_PATH", runs_dir / "factory_ledger.lock"))

            stack.enter_context(patch.object(integrator, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(worktrees, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(worktrees, "CODEX_DIR", codex_dir))
            stack.enter_context(patch.object(worktrees, "REPO_ROOT", repo_root))
            stack.enter_context(patch.object(orchestrator, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(orchestrator, "CODEX_DIR", codex_dir))
            stack.enter_context(patch.object(orchestrator, "REPO_ROOT", repo_root))
            stack.enter_context(patch.object(locks, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(attestations, "RUNS_DIR", runs_dir))
            stack.enter_context(patch.object(doctor, "REPO_ROOT", repo_root))
            stack.enter_context(patch.object(doctor, "RUNS_DIR", runs_dir))

            yield {
                "repo_root": repo_root,
                "codex_dir": codex_dir,
                "runs_dir": runs_dir,
                "schemas_dir": schemas_dir,
                "contracts_dir": contracts_factory_dir,
            }


def make_change(path: str, *, reason: str = "test", sha256: str = "abc123") -> dict[str, Any]:
    return {
        "path": path,
        "change_type": "modified",
        "reason": reason,
        "sha256": sha256,
    }


def write_worker_bundle(
    *,
    run_id: str,
    worker: str,
    changes: Iterable[dict[str, Any]],
    summary: str = "",
    status: str = "PASS",
    allowed_globs: list[str] | None = None,
    blocked_globs: list[str] | None = None,
    allow_shared_paths: list[str] | None = None,
) -> Path:
    contracts.scaffold_worker_bundle(run_id, worker)
    root = contracts.bundle_dir(run_id, worker)

    _write(
        root / "STATUS.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "worker_id": worker,
            "status": status,
            "started_at": "2026-02-18T00:00:00+00:00",
            "ended_at": "2026-02-18T00:00:00+00:00",
            "required_checks": [{"name": "bundle_ready", "status": "PASS"}],
            "optional_checks": [],
            "errors": [],
            "warnings": [],
            "artifacts": ["SUMMARY.md", "FILES_CHANGED.json", "DIFF.patch"],
        },
    )
    _write(
        root / "FILES_CHANGED.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "owner": worker,
            "changes": list(changes),
        },
    )
    _write(
        root / "SCOPE_LOCK.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "worker_id": worker,
            "allowed_globs": allowed_globs or ["apps/**", "tools/**", "docs/**"],
            "blocked_globs": blocked_globs or [],
            "allow_shared_paths": allow_shared_paths or [],
        },
    )
    _write(
        root / "HANDOFF_NOTE.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "worker_id": worker,
            "summary": summary or f"{worker} summary",
            "decisions": [f"{worker} deterministic decision"],
            "risks": [],
            "next_actions": ["integrate"],
        },
    )
    _write(root / "SUMMARY.md", summary or f"# {worker}\n\n- summary\n")
    _write(root / "SUGGESTIONS.md", "# Suggestions\n\n- none\n")
    _write(root / "DIFF.patch", f"diff --git a/{worker}.txt b/{worker}.txt\n")
    _write(
        root / "LOGS" / "INDEX.json",
        {
            "schema_version": 1,
            "run_id": run_id,
            "owner": worker,
            "logs": [{"name": "worker", "path": "LOGS/worker.log.txt", "rc": 0}],
        },
    )
    _write(root / "LOGS" / "worker.log.txt", "ok\n")
    return root


def write_all_worker_bundles(
    run_id: str,
    *,
    per_worker_changes: dict[str, list[dict[str, Any]]],
    allowed_globs: dict[str, list[str]] | None = None,
    blocked_globs: dict[str, list[str]] | None = None,
    allow_shared_paths: dict[str, list[str]] | None = None,
) -> None:
    for worker in common.WORKERS:
        write_worker_bundle(
            run_id=run_id,
            worker=worker,
            changes=per_worker_changes.get(worker, []),
            allowed_globs=(allowed_globs or {}).get(worker),
            blocked_globs=(blocked_globs or {}).get(worker),
            allow_shared_paths=(allow_shared_paths or {}).get(worker),
        )
