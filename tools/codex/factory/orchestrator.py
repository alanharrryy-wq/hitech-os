from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from .common import CODEX_DIR, REPO_ROOT, RUNS_DIR, WORKERS, ensure_dir, read_text, stable_sha256_text, write_text
from .path_guard import is_protected_path, normalize_rel_path
from .shared_bridge import (
    SharedBridgeFlags,
    consume_from_shared,
    discover_repo_root,
    parse_shared_flags,
    publish_to_shared,
    resolve_shared_current_run_root,
    resolve_shared_root,
    write_factory_pointer,
    write_shared_pointer,
)
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

WORKER_ENRICHMENT_HINTS: dict[str, dict[str, tuple[str, ...]]] = {
    "A_worker": {
        "objective_fit": (
            "Focus on interface-first scaffolding for render, registry, and desktop bridge modules.",
            "Keep extension seams explicit so later runtime implementation can plug in without contract churn.",
        ),
        "no_go": (
            "Do not add runtime execution paths, adapters, or environment-bound integrations.",
            "Do not introduce broad refactors outside scaffold boundaries.",
        ),
    },
    "B_worker": {
        "objective_fit": (
            "Focus on deterministic tooling primitives and reusable helper APIs.",
            "Prefer composable utilities that can be imported without hidden side effects.",
        ),
        "no_go": (
            "Do not add product/business behavior to tooling packages.",
            "Do not add heavyweight dependencies when native or existing tooling is sufficient.",
        ),
    },
    "C_worker": {
        "objective_fit": (
            "Focus on schema and placeholder contracts only, with stable serialization semantics.",
            "Keep compatibility intent explicit so integration can validate contract evolution safely.",
        ),
        "no_go": (
            "Do not add runtime implementations, loaders, or service behavior.",
            "Do not couple schema placeholders to non-contract runtime code.",
        ),
    },
    "D_worker": {
        "objective_fit": (
            "Focus on deterministic smoke/docs scaffolding that supports integrator consumption.",
            "Keep acceptance criteria explicit and reproducible for follow-up automation.",
        ),
        "no_go": (
            "Do not edit core runtime modules while preparing smoke/docs scaffolding.",
            "Do not write final integration conclusions before worker artifacts are complete.",
        ),
    },
}


class OperatorError(RuntimeError):
    pass


class OperatorCollisionError(OperatorError):
    pass


PHASE_SPECS: dict[str, dict[str, Any]] = {
    "phase1-extract": {
        "description": "Deterministic phase-1 extraction scaffolding.",
        "run_id_prefix": "RUN_PHASE1_EXTRACT",
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


def run_id_prefix_for_phase(phase: str) -> str:
    spec = get_phase_spec(phase)
    explicit = str(spec.get("run_id_prefix", "")).strip()
    if explicit:
        return explicit

    normalized = "".join(char if char.isalnum() else "_" for char in str(phase).upper())
    normalized = "_".join(item for item in normalized.split("_") if item)
    if not normalized:
        raise OperatorError(f"unable to derive run-id prefix for phase: {phase}")
    return f"RUN_{normalized}"


def parse_run_suffix(run_id: str, prefix: str) -> int | None:
    token = f"{prefix}_"
    if not str(run_id).startswith(token):
        return None
    suffix = str(run_id)[len(token) :]
    if not suffix.isdigit():
        return None
    try:
        return int(suffix)
    except ValueError:
        return None


def list_existing_run_ids(
    *,
    runs_dir: Path,
    prompts_dir: Path,
    worktrees_dir: Path,
    prefix: str,
) -> list[str]:
    candidates: set[str] = set()
    for root in (runs_dir, prompts_dir, worktrees_dir):
        if not root.exists():
            continue
        try:
            children = sorted(item for item in root.iterdir() if item.is_dir())
        except OSError:
            continue
        for child in children:
            run_id = child.name
            if parse_run_suffix(run_id, prefix) is not None:
                candidates.add(run_id)
    return sorted(candidates, key=lambda item: (parse_run_suffix(item, prefix) or 0, item))


def is_run_id_occupied(
    run_id: str,
    *,
    runs_dir: Path,
    prompts_dir: Path,
    worktrees_dir: Path,
) -> bool:
    return any((root / run_id).exists() for root in (runs_dir, prompts_dir, worktrees_dir))


def next_available_run_id(
    prefix: str,
    start: int = 1,
    max_tries: int = 200,
    *,
    runs_dir: Path,
    prompts_dir: Path,
    worktrees_dir: Path,
) -> str:
    origin = max(1, int(start))
    tries = max(1, int(max_tries))
    for offset in range(tries):
        suffix = origin + offset
        candidate = f"{prefix}_{suffix:03d}"
        if not is_run_id_occupied(
            candidate,
            runs_dir=runs_dir,
            prompts_dir=prompts_dir,
            worktrees_dir=worktrees_dir,
        ):
            return candidate
    raise OperatorCollisionError(f"unable to select free run-id for prefix={prefix} after {tries} attempts")


def select_run_id_for_phase(
    phase: str,
    explicit_run_id: str | None,
    strict: bool,
    *,
    runs_dir: Path,
    prompts_dir: Path,
    worktrees_dir: Path,
    start: int = 1,
    max_tries: int = 200,
) -> tuple[str, str]:
    prefix = run_id_prefix_for_phase(phase)
    run_id_raw = str(explicit_run_id or "").strip()
    auto_requested = not run_id_raw or run_id_raw.lower() == "auto"
    if auto_requested:
        chosen = next_available_run_id(
            prefix,
            start=start,
            max_tries=max_tries,
            runs_dir=runs_dir,
            prompts_dir=prompts_dir,
            worktrees_dir=worktrees_dir,
        )
        return chosen, "auto"

    if strict and is_run_id_occupied(
        run_id_raw,
        runs_dir=runs_dir,
        prompts_dir=prompts_dir,
        worktrees_dir=worktrees_dir,
    ):
        raise OperatorCollisionError(f"explicit run-id is occupied: {run_id_raw}")
    return run_id_raw, "explicit"


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
    header = _render_worker_prompt_header(
        run_id=run_id,
        base_ref=base_ref,
        phase=phase,
        worker=worker,
        worker_spec=worker_spec,
    )
    enriched = render_enriched_playbook(
        run_id=run_id,
        phase=phase,
        worker=worker,
        worker_spec=worker_spec,
    )
    return f"{header}\n{enriched}"


def _render_worker_prompt_header(
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


def render_enriched_playbook(
    *,
    run_id: str,
    phase: str,
    worker: str,
    worker_spec: Mapping[str, Any],
) -> str:
    hints = WORKER_ENRICHMENT_HINTS.get(worker, {})
    objective_fit = sorted(str(item) for item in hints.get("objective_fit", ()) if str(item).strip())
    no_go_examples = sorted(str(item) for item in hints.get("no_go", ()) if str(item).strip())

    lines = [
        "## === ENRICHED PLAYBOOK ===",
        "",
        "### Context Guardrails",
        "- This playbook enriches worker behavior and never overrides Factory constraints defined above.",
        "- Confirm the active worktree maps to this RUN_ID and WORKER_ID before making edits.",
        "- If detected context disagrees with this prompt metadata, set STATUS.json to BLOCKED and stop.",
        "",
        "### Preflight Checklist",
        "- Verify git status is clean before writing repo files.",
        "- Reconfirm every planned change remains inside the declared Repo Write Scope.",
        "- Validate Artifact Write Root exists and is writable before code edits begin.",
        "",
        "### Collision Protocol",
        "- If non-scaffold content would be overwritten, set STATUS.json to BLOCKED and stop.",
        "- If another worker appears to own a target path, set STATUS.json to BLOCKED and document the conflict.",
        "- Never continue after collision detection; include deterministic resume guidance in HANDOFF_NOTE.json.",
        "",
        "### Determinism Audit",
        "- Keep ordering stable for JSON keys, lists, and bullet output in every artifact.",
        "- Avoid randomness, UUIDs, and environment-specific values in generated outputs.",
        "- Re-run local checks after edits and confirm repeated runs produce identical outputs.",
        "",
        "### Diff Scope Validation",
        "- Validate git diff output is limited to the declared Repo Write Scope.",
        "- If any out-of-scope path appears, set STATUS.json to BLOCKED and report it.",
        "",
        "### Development Discipline",
        "- Keep public API surfaces explicit and typed for future extension.",
        "- Avoid side effects on import; module loading must remain inert.",
        "- Prefer minimal dependency changes and reuse existing repository tooling patterns.",
        "",
        "### Artifact Quality Gate",
        "- Verify all required artifacts exist before signaling completion.",
        "- Write FILES_CHANGED.json with stable ordering and deterministic action labels.",
        "- Keep SCOPE_LOCK.json ownership entries aligned with the declared scope and overlap policy.",
        "- Keep HANDOFF_NOTE.json concise with decisions, risks, and deterministic next actions.",
        "",
        "### Objective Fit Check",
        "- Confirm each changed file directly advances this worker mission without scope drift.",
    ]

    for item in objective_fit:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "### No-Go This Chat",
        ]
    )
    for item in no_go_examples:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "### Structured Summary Format",
            "- In SUMMARY.md include: Completed Work, Validation Commands, Risks, and Next Actions.",
            "- Keep file and command lists sorted for deterministic review.",
            "",
            "### Time Box and Troubleshooting",
            "- Work in focused passes; if blocked, stop early and record the blocker instead of improvising.",
            "- When a command is unavailable or environment-limited, record exact command and outcome in LOGS/INDEX.json.",
            "- If preflight or validation remains unresolved, mark BLOCKED with concrete resume guidance.",
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
    if command:
        resolved = shutil.which(command[0])
        if resolved:
            command = [resolved, *command[1:]]
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


def _shared_flags_payload(flags: SharedBridgeFlags) -> dict[str, Any]:
    return {
        "mode": flags.mode,
        "require_current": bool(flags.require_current),
        "strict_schema": bool(flags.strict_schema),
        "hash_strategy": flags.hash_strategy,
        "dry_run": bool(flags.dry_run),
        "shared_root_override": str(flags.shared_root_override or ""),
    }


def resolve_shared_bridge_context(*, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    """
    Resolve shared bridge runtime context from env flags.
    Flags are OFF by default and no side effects occur in this resolver.
    """
    source_env = dict(os.environ)
    if env is not None:
        source_env.update({str(key): str(value) for key, value in dict(env).items()})

    flags = parse_shared_flags(source_env)
    payload: dict[str, Any] = {
        "status": PASS,
        "enabled": bool(flags.mode != "off"),
        "flags": _shared_flags_payload(flags),
        "repo_root": "",
        "shared_root": "",
        "shared_current_run_root": "",
        "reason": "",
    }

    if flags.mode == "off":
        payload["reason"] = "shared bridge mode is off"
        return payload

    try:
        repo_root = discover_repo_root(REPO_ROOT)
    except FileNotFoundError as exc:
        payload["status"] = BLOCKED
        payload["reason"] = str(exc)
        return payload

    shared_root = resolve_shared_root(
        repo_root,
        shared_root_override=flags.shared_root_override,
        env=source_env,
    )

    try:
        shared_current = resolve_shared_current_run_root(
            shared_root,
            require_current=bool(flags.require_current),
        )
    except FileNotFoundError as exc:
        payload["status"] = BLOCKED
        payload["repo_root"] = repo_root.as_posix()
        payload["shared_root"] = shared_root.as_posix() if shared_root is not None else ""
        payload["reason"] = str(exc)
        return payload

    payload["repo_root"] = repo_root.as_posix()
    payload["shared_root"] = shared_root.as_posix() if shared_root is not None else ""
    payload["shared_current_run_root"] = shared_current.as_posix() if shared_current is not None else ""
    if shared_root is None:
        payload["reason"] = "shared root not resolved"
    elif shared_current is None:
        payload["reason"] = "shared current run root not resolved"
    else:
        payload["reason"] = "shared bridge context resolved"
    return payload


def run_shared_consume_hook(
    *,
    run_id: str,
    dry_run: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """
    Pre-run shared consume hook.
    Writes only to canonical `tools/codex/runs/<RUN_ID>/incoming_shared/` when enabled.
    """
    context = resolve_shared_bridge_context(env=env)
    flags = SharedBridgeFlags(**dict(context.get("flags", {})))
    effective_dry_run = bool(dry_run or flags.dry_run)

    if not bool(context.get("enabled", False)):
        return {
            "status": PASS,
            "enabled": False,
            "mode": flags.mode,
            "dry_run": effective_dry_run,
            "reason": str(context.get("reason", "shared bridge disabled")),
            "context": context,
        }

    if str(context.get("status", PASS)) != PASS:
        return {
            "status": BLOCKED,
            "enabled": True,
            "mode": flags.mode,
            "dry_run": effective_dry_run,
            "reason": str(context.get("reason", "shared bridge context blocked")),
            "context": context,
            "consume": {},
            "pointers": {},
        }

    run_root = RUNS_DIR / run_id
    shared_current_root_raw = str(context.get("shared_current_run_root", "")).strip()
    shared_current_root = Path(shared_current_root_raw) if shared_current_root_raw else None
    shared_root_raw = str(context.get("shared_root", "")).strip()
    shared_root = Path(shared_root_raw) if shared_root_raw else None

    consume_payload = consume_from_shared(
        run_id=run_id,
        run_root=run_root,
        shared_current_run_root=shared_current_root,
        mode=flags.mode,
        hash_strategy=flags.hash_strategy,
        dry_run=effective_dry_run,
        strict_on_lock=bool(flags.strict_schema),
    )

    pointers: dict[str, Any] = {}
    if shared_current_root is not None and shared_root is not None and not consume_payload.get("lock_files"):
        pointers["factory_pointer"] = write_factory_pointer(
            run_id=run_id,
            factory_run_root=run_root,
            factory_worktrees_root=CODEX_DIR / "worktrees" / run_id,
            shared_current_run_root=shared_current_root,
            mode=flags.mode,
            dry_run=effective_dry_run,
        )
        pointers["shared_pointer"] = write_shared_pointer(
            run_id=run_id,
            factory_run_root=run_root,
            shared_root=shared_root,
            shared_current_run_root=shared_current_root,
            mode=flags.mode,
            dry_run=effective_dry_run,
        )

    return {
        "status": str(consume_payload.get("status", PASS)),
        "enabled": True,
        "mode": flags.mode,
        "dry_run": effective_dry_run,
        "reason": str(consume_payload.get("reason", "")),
        "context": context,
        "consume": consume_payload,
        "pointers": pointers,
    }


def run_shared_publish_hook(
    *,
    run_id: str,
    dry_run: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """
    Post-run shared publish hook.
    Copies canonical run outputs into shared when enabled.
    """
    context = resolve_shared_bridge_context(env=env)
    flags = SharedBridgeFlags(**dict(context.get("flags", {})))
    effective_dry_run = bool(dry_run or flags.dry_run)

    if not bool(context.get("enabled", False)):
        return {
            "status": PASS,
            "enabled": False,
            "mode": flags.mode,
            "dry_run": effective_dry_run,
            "reason": str(context.get("reason", "shared bridge disabled")),
            "context": context,
        }

    if str(context.get("status", PASS)) != PASS:
        return {
            "status": BLOCKED,
            "enabled": True,
            "mode": flags.mode,
            "dry_run": effective_dry_run,
            "reason": str(context.get("reason", "shared bridge context blocked")),
            "context": context,
            "publish": {},
            "pointers": {},
        }

    run_root = RUNS_DIR / run_id
    shared_current_root_raw = str(context.get("shared_current_run_root", "")).strip()
    shared_current_root = Path(shared_current_root_raw) if shared_current_root_raw else None
    shared_root_raw = str(context.get("shared_root", "")).strip()
    shared_root = Path(shared_root_raw) if shared_root_raw else None

    publish_payload = publish_to_shared(
        run_id=run_id,
        run_root=run_root,
        shared_current_run_root=shared_current_root,
        mode=flags.mode,
        hash_strategy=flags.hash_strategy,
        dry_run=effective_dry_run,
        strict_on_lock=bool(flags.strict_schema),
    )

    pointers: dict[str, Any] = {}
    if shared_current_root is not None and shared_root is not None and not publish_payload.get("lock_files"):
        pointers["factory_pointer"] = write_factory_pointer(
            run_id=run_id,
            factory_run_root=run_root,
            factory_worktrees_root=CODEX_DIR / "worktrees" / run_id,
            shared_current_run_root=shared_current_root,
            mode=flags.mode,
            dry_run=effective_dry_run,
        )
        pointers["shared_pointer"] = write_shared_pointer(
            run_id=run_id,
            factory_run_root=run_root,
            shared_root=shared_root,
            shared_current_run_root=shared_current_root,
            mode=flags.mode,
            dry_run=effective_dry_run,
        )

    return {
        "status": str(publish_payload.get("status", PASS)),
        "enabled": True,
        "mode": flags.mode,
        "dry_run": effective_dry_run,
        "reason": str(publish_payload.get("reason", "")),
        "context": context,
        "publish": publish_payload,
        "pointers": pointers,
    }
