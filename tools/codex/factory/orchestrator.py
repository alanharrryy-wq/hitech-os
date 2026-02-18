from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .common import CODEX_DIR, REPO_ROOT, RUNS_DIR, WORKERS, ensure_dir, read_text, stable_sha256_text, write_text
from .path_guard import is_protected_path, normalize_rel_path
from .status_eval import BLOCKED, PASS
from .worktrees import worktree_path

DEFAULT_PHASE = "phase1-extract"
DEFAULT_SLEEP_SEC = 5
DEFAULT_TIMEOUT_MIN = 120
DEFAULT_WORKERS: tuple[str, ...] = tuple(sorted(WORKERS))

WORKER_ARTIFACT_FILES: tuple[str, ...] = (
    "STATUS.json",
    "SUMMARY.md",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "SUGGESTIONS.md",
    "SCOPE_LOCK.json",
    "HANDOFF_NOTE.json",
    "LOGS/INDEX.json",
)


class OperatorError(RuntimeError):
    pass


class OperatorCollisionError(OperatorError):
    pass


PHASE_SPECS: dict[str, dict[str, Any]] = {
    "phase1-extract": {
        "description": "Deterministic phase-1 extraction scaffolding.",
        "default_workers": list(DEFAULT_WORKERS),
        "workers": {
            "A_worker": {
                "scope": "Scaffold packages/render-core, packages/module-registry, packages/desktop-bridge.",
                "repo_scope_globs": [
                    "packages/desktop-bridge/**",
                    "packages/module-registry/**",
                    "packages/render-core/**",
                ],
                "constraints": [
                    "Scaffold only.",
                    "No runtime business logic.",
                ],
            },
            "B_worker": {
                "scope": "Expand packages/tooling/** for Piton-first deterministic tooling utilities.",
                "repo_scope_globs": [
                    "packages/tooling/**",
                ],
                "constraints": [
                    "No business logic.",
                    "Keep utilities deterministic.",
                ],
            },
            "C_worker": {
                "scope": "Create packages/extraction-contracts/** schemas and placeholders.",
                "repo_scope_globs": [
                    "packages/extraction-contracts/**",
                ],
                "constraints": [
                    "Schemas and placeholders only.",
                    "No runtime implementation.",
                ],
            },
            "D_worker": {
                "scope": "Create packages/phase1-smoke/** docs templates and deterministic smoke harness.",
                "repo_scope_globs": [
                    "packages/phase1-smoke/**",
                ],
                "constraints": [
                    "Do not write root CONTRACT.md, STATE.md, or NEXT.md directly.",
                    "Place templates for integrator consumption.",
                ],
            },
        },
    }
}


def normalize_workers(raw: str | Iterable[str] | None, *, fallback: Iterable[str] | None = None) -> list[str]:
    base = list(fallback or DEFAULT_WORKERS)
    if raw is None:
        cleaned = [item.strip() for item in base if item.strip()]
        return sorted(set(cleaned))
    if isinstance(raw, str):
        values = [item.strip() for item in raw.split(",") if item.strip()]
    else:
        values = [str(item).strip() for item in raw if str(item).strip()]
    if not values:
        values = [item.strip() for item in base if item.strip()]
    return sorted(set(values))


def get_phase_spec(phase: str) -> dict[str, Any]:
    spec = PHASE_SPECS.get(phase)
    if spec is None:
        supported = ", ".join(sorted(PHASE_SPECS))
        raise OperatorError(f"unsupported phase: {phase}; supported={supported}")
    return spec


def resolve_phase_workers(phase: str, workers: str | Iterable[str] | None) -> list[str]:
    spec = get_phase_spec(phase)
    chosen = normalize_workers(workers, fallback=spec.get("default_workers", DEFAULT_WORKERS))
    supported = set(spec.get("workers", {}).keys())
    unsupported = sorted(item for item in chosen if item not in supported)
    if unsupported:
        raise OperatorError(f"workers not in phase spec {phase}: {', '.join(unsupported)}")
    return chosen


def prompts_dir(run_id: str) -> Path:
    return CODEX_DIR / "prompts" / run_id


def prompt_path(run_id: str, worker: str) -> Path:
    return prompts_dir(run_id) / f"PROMPT_{worker}.txt"


def worktree_prompt_path(run_id: str, worker: str) -> Path:
    return worktree_path(run_id, worker) / "PROMPT_WORKER.txt"


def runboard_path(run_id: str) -> Path:
    return prompts_dir(run_id) / "RUNBOARD.md"


def worker_status_path(run_id: str, worker: str, *, runs_dir: Path | None = None) -> Path:
    base = runs_dir or RUNS_DIR
    return base / run_id / worker / "STATUS.json"


def _ensure_repo_root() -> None:
    if not REPO_ROOT.exists():
        raise OperatorError(f"repo root does not exist: {REPO_ROOT.as_posix()}")
    if not (REPO_ROOT / ".git").exists():
        raise OperatorError(f"repo root marker missing (.git): {REPO_ROOT.as_posix()}")


def _validate_output_path(path: Path) -> str:
    resolved_root = REPO_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise OperatorError(f"path is outside repo root: {path.as_posix()}")
    rel = resolved.relative_to(resolved_root).as_posix()
    normalized = normalize_rel_path(rel)
    if is_protected_path(normalized):
        raise OperatorError(f"operator output targets protected path: {normalized}")
    return normalized


def _extract_run_id(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("RUN_ID:"):
            return line.partition(":")[2].strip()
    return ""


def _write_if_clean(
    *,
    path: Path,
    content: str,
    run_id: str,
    dry_run: bool,
    require_parent: bool = False,
) -> dict[str, Any]:
    rel_path = _validate_output_path(path)
    if path.exists():
        existing = read_text(path)
        existing_run_id = _extract_run_id(existing)
        if existing_run_id and existing_run_id != run_id:
            raise OperatorCollisionError(
                f"run-id collision at {rel_path}: expected {run_id} found {existing_run_id}"
            )
        if existing != content:
            raise OperatorCollisionError(f"content collision at {rel_path}")
        return {
            "path": rel_path,
            "action": "unchanged",
            "sha256": stable_sha256_text(content),
        }

    if require_parent and not path.parent.exists() and not dry_run:
        raise OperatorError(f"missing parent directory for prompt target: {rel_path}")

    if dry_run:
        return {
            "path": rel_path,
            "action": "planned_write",
            "sha256": stable_sha256_text(content),
        }

    ensure_dir(path.parent)
    write_text(path, content)
    return {
        "path": rel_path,
        "action": "created",
        "sha256": stable_sha256_text(content),
    }


def render_worker_prompt(
    *,
    run_id: str,
    base_ref: str,
    phase: str,
    worker: str,
    worker_spec: Mapping[str, Any],
) -> str:
    scope = str(worker_spec.get("scope", "")).strip()
    repo_scope = sorted(str(item) for item in worker_spec.get("repo_scope_globs", []) if str(item).strip())
    constraints = sorted(str(item) for item in worker_spec.get("constraints", []) if str(item).strip())
    artifact_root = f"tools/codex/runs/{run_id}/{worker}/"
    lines = [
        "# HITECH-OS Worker Prompt",
        f"RUN_ID: {run_id}",
        f"PHASE: {phase}",
        f"WORKER_ID: {worker}",
        f"BASE_REF: {base_ref}",
        "",
        "## Mission Scope",
        f"- {scope}",
        "",
        "## Repo Write Scope",
    ]
    for item in repo_scope:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Artifact Write Root (Required)",
            f"- {artifact_root}",
            "",
            "Only write standard bundle artifacts under this root:",
        ]
    )
    for artifact in WORKER_ARTIFACT_FILES:
        lines.append(f"- {artifact}")

    lines.extend(
        [
            "",
            "## Hard Constraints",
            "- Determinism only: stable ordering, no random IDs, no UUIDs.",
            "- Do not modify protected paths: .git/**, .env*, .github/workflows/**.",
            "- Abort immediately on out-of-scope writes or path collisions.",
            "- Abort immediately if another worker owns a path you plan to change.",
            "",
            "## Worker-Specific Constraints",
        ]
    )
    for item in constraints:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Completion Signal",
            f"- Write STATUS.json to {artifact_root}STATUS.json",
            "",
            "## Abort Conditions",
            "- Collision detected in prompt artifacts or worker outputs.",
            "- Requested change is outside declared scope.",
            "- Required path ownership is ambiguous.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_runboard(
    *,
    run_id: str,
    base_ref: str,
    phase: str,
    workers: Iterable[str],
) -> str:
    sorted_workers = sorted(set(str(item) for item in workers))
    lines = [
        "# HITECH-OS Factory RUNBOARD",
        f"RUN_ID: {run_id}",
        f"PHASE: {phase}",
        f"BASE_REF: {base_ref}",
        "",
        "## Worker Prompt Targets",
    ]
    for worker in sorted_workers:
        lines.append(f"- {worker}: tools/codex/worktrees/{run_id}/{worker}/PROMPT_WORKER.txt")

    lines.extend(
        [
            "",
            "## Completion Gate",
            "Wait for all worker status files:",
        ]
    )
    for worker in sorted_workers:
        lines.append(f"- tools/codex/runs/{run_id}/{worker}/STATUS.json")

    lines.extend(
        [
            "",
            "## Operator Action",
            "In each worker VS Code window: Ctrl+Alt+P -> New Codex Agent -> paste PROMPT_WORKER.txt",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generate_phase_prompts(
    *,
    run_id: str,
    base_ref: str,
    phase: str,
    workers: list[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    _ensure_repo_root()
    spec = get_phase_spec(phase)
    worker_specs = spec.get("workers", {})
    writes: list[dict[str, Any]] = []
    for worker in workers:
        worker_spec = dict(worker_specs.get(worker, {}))
        if not worker_spec:
            raise OperatorError(f"worker missing from phase spec: {worker}")
        content = render_worker_prompt(
            run_id=run_id,
            base_ref=base_ref,
            phase=phase,
            worker=worker,
            worker_spec=worker_spec,
        )
        writes.append(
            _write_if_clean(
                path=prompt_path(run_id, worker),
                content=content,
                run_id=run_id,
                dry_run=dry_run,
                require_parent=False,
            )
        )
        writes.append(
            _write_if_clean(
                path=worktree_prompt_path(run_id, worker),
                content=content,
                run_id=run_id,
                dry_run=dry_run,
                require_parent=True,
            )
        )

    board_content = render_runboard(
        run_id=run_id,
        base_ref=base_ref,
        phase=phase,
        workers=workers,
    )
    writes.append(
        _write_if_clean(
            path=runboard_path(run_id),
            content=board_content,
            run_id=run_id,
            dry_run=dry_run,
            require_parent=False,
        )
    )

    actions = sorted(set(str(item.get("action", "")) for item in writes if str(item.get("action", "")).strip()))
    created = sorted(str(item.get("path", "")) for item in writes if item.get("action") == "created")
    unchanged = sorted(str(item.get("path", "")) for item in writes if item.get("action") == "unchanged")
    planned = sorted(str(item.get("path", "")) for item in writes if item.get("action") == "planned_write")

    return {
        "status": PASS,
        "run_id": run_id,
        "phase": phase,
        "workers": sorted(set(workers)),
        "actions": actions,
        "created": created,
        "unchanged": unchanged,
        "planned": planned,
        "writes": sorted(writes, key=lambda item: str(item.get("path", ""))),
    }


def scan_worker_statuses(
    *,
    run_id: str,
    workers: list[str],
    runs_dir: Path | None = None,
) -> dict[str, Any]:
    present: list[str] = []
    missing: list[str] = []
    for worker in sorted(set(workers)):
        if worker_status_path(run_id, worker, runs_dir=runs_dir).exists():
            present.append(worker)
        else:
            missing.append(worker)
    return {
        "run_id": run_id,
        "present": sorted(present),
        "missing": sorted(missing),
        "ready": len(missing) == 0,
    }


def watch_for_worker_statuses(
    *,
    run_id: str,
    workers: list[str],
    sleep_sec: int = DEFAULT_SLEEP_SEC,
    timeout_min: int = DEFAULT_TIMEOUT_MIN,
    runs_dir: Path | None = None,
    dry_run: bool = False,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    sorted_workers = sorted(set(workers))
    if dry_run:
        state = scan_worker_statuses(run_id=run_id, workers=sorted_workers, runs_dir=runs_dir)
        state["status"] = PASS
        state["iterations"] = 0
        state["timed_out"] = False
        state["dry_run"] = True
        return state

    timeout_seconds = max(1, int(timeout_min) * 60)
    interval = max(1, int(sleep_sec))
    deadline = time.monotonic() + timeout_seconds
    iterations = 0

    while True:
        state = scan_worker_statuses(run_id=run_id, workers=sorted_workers, runs_dir=runs_dir)
        progress = {
            "run_id": run_id,
            "workers": sorted_workers,
            "present": list(state["present"]),
            "missing": list(state["missing"]),
            "ready": bool(state["ready"]),
            "iteration": iterations,
        }
        if on_progress is not None:
            on_progress(progress)
        if state["ready"]:
            state["status"] = PASS
            state["iterations"] = iterations
            state["timed_out"] = False
            state["dry_run"] = False
            return state
        if time.monotonic() >= deadline:
            state["status"] = BLOCKED
            state["iterations"] = iterations
            state["timed_out"] = True
            state["dry_run"] = False
            return state
        iterations += 1
        time.sleep(interval)


def run_external_command(command: list[str], *, dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {
            "cmd": list(command),
            "rc": 0,
            "stdout": "",
            "stderr": "",
            "dry_run": True,
        }
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "cmd": list(command),
        "rc": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "dry_run": False,
    }
