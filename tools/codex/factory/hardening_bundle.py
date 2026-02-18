from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from factory.common import INTEGRATOR, REPO_ROOT, iso_utc, read_json, write_json, write_text
    from factory.diffing import unified_patch_for_paths
else:
    from .common import INTEGRATOR, REPO_ROOT, iso_utc, read_json, write_json, write_text
    from .diffing import unified_patch_for_paths


def _run(name: str, command: list[str], cwd: Path, log_path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    body = (
        f"# cmd: {' '.join(command)}\n"
        f"# rc: {proc.returncode}\n\n"
        f"{proc.stdout}"
        f"{proc.stderr}"
    )
    write_text(log_path, body)
    return {
        "name": name,
        "cmd": command,
        "rc": proc.returncode,
        "log": log_path.as_posix(),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _head_exists(path: str) -> bool:
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{path}"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.returncode == 0


def _collect_changed_paths() -> list[str]:
    static_paths = [
        "docs/codex-kernel/INDEX.md",
        "docs/codex-kernel/docs/INDEX.md",
        "tools/codex/validation.json",
        "tools/codex/factory_cli.py",
        "tools/codex/factory.ps1",
        ".vscode/codex-factory.tasks.json",
    ]
    globs = [
        "docs/factory/*.md",
        "tools/codex/contracts/factory/*.json",
        "tools/codex/examples/factory/*",
        "tools/codex/factory/*.py",
        "tools/codex/factory/tests/*.py",
        "tools/codex/schemas/*.schema.json",
        "tools/codex/templates/factory/*",
    ]
    paths: set[str] = set()
    for item in static_paths:
        candidate = REPO_ROOT / item
        if candidate.exists():
            paths.add(item)
    for pattern in globs:
        for candidate in REPO_ROOT.glob(pattern):
            if candidate.is_file():
                paths.add(candidate.relative_to(REPO_ROOT).as_posix())
    return sorted(paths)


def _render_report(
    run_id: str,
    command_results: list[dict[str, Any]],
    improvements: list[dict[str, Any]],
    files_changed_count: int,
    self_test_summary: dict[str, Any],
) -> str:
    lines = [
        f"# FINAL_REPORT — {run_id}",
        "",
        "1) Summary",
        "- Implemented additive Multi-Codex factory hardening under `tools/codex` and `docs/factory`.",
        "- Added Python-first orchestration, deterministic contracts validation, worktree helpers, Z integrator pipeline, and smoke tests.",
        f"- Recorded {len(improvements)} concrete improvements with IDs `IMP-001..IMP-{len(improvements):03d}`.",
        "",
        "2) Factory Architecture (A/B/C/D/Z roles)",
        "- `A_worker`: primary scoped implementation output bundle owner.",
        "- `B_worker`: secondary scoped implementation output bundle owner.",
        "- `C_worker`: tooling/infrastructure scoped output bundle owner.",
        "- `D_worker`: validation/hardening scoped output bundle owner.",
        "- `Z_integrator`: consumes worker bundles, enforces overlap/scope checks, merges reports/diffs, emits final run artifacts.",
        "",
        "3) Run/Bundle Schema (paths, JSON schema, validation)",
        "- Schemas live under `tools/codex/schemas/*.schema.json`.",
        "- Contract registry lives at `tools/codex/contracts/factory/contracts_registry.json`.",
        "- Bundle validators run via `python tools/codex/factory_cli.py contracts-check` and `bundle-validate`.",
        "",
        "4) Communication Protocol (worker output, Z consumption)",
        "- Workers must output `STATUS.json`, `SUMMARY.md`, `FILES_CHANGED.json`, `DIFF.patch`, `SUGGESTIONS.md`, `SCOPE_LOCK.json`, `HANDOFF_NOTE.json`, `LOGS/INDEX.json`.",
        "- Z consumes A/B/C/D bundles, performs schema + overlap + scope validation, writes `FINAL_REPORT.txt`, `STATUS.json`, `FILES_CHANGED.json`, `DIFF.patch`, `MERGE_PLAN.md`, and logs.",
        "",
        "5) 200+ Improvements",
    ]
    for item in improvements:
        lines.append(
            f"- {item['id']} | {item['category']} | {item['what']} | {item['where']} | {item['why']}"
        )
    lines.extend(
        [
            "",
            "6) How To Use (exact operator commands)",
            "- `python tools/codex/factory_cli.py contracts-check`",
            "- `python tools/codex/factory_cli.py init-run`",
            "- `python tools/codex/factory_cli.py preflight --run-id <RUN_ID>`",
            "- `python tools/codex/factory_cli.py worktrees create --run-id <RUN_ID>`",
            "- `python tools/codex/factory_cli.py bundle-init --run-id <RUN_ID>`",
            "- `python tools/codex/factory_cli.py bundle-validate --run-id <RUN_ID>`",
            "- `python tools/codex/factory_cli.py integrate --run-id <RUN_ID>`",
            "- `python tools/codex/factory_cli.py self-test`",
            "",
            "7) Self-Test Results (factory smoke)",
            f"- Status: {self_test_summary.get('status', 'UNKNOWN')}",
            f"- Deterministic output hash match: {self_test_summary.get('deterministic', False)}",
            f"- Smoke run id: {self_test_summary.get('run_id', '')}",
            "",
            "8) Risks / Remaining Tech Debt",
            "- Git worktree creation is available but still operator-driven; no automatic teardown by default.",
            "- Integration currently blocks overlaps rather than attempting semantic merge repair.",
            "- Optional CI hook and git-hook entries are documented but intentionally disabled by default.",
            "",
            "9) DELETION_REQUESTS",
            "- None.",
            "",
            "10) NEXT ACTION",
            "- Run one full multi-worker factory execution on a real scoped task and keep this hardening config as the baseline contract.",
            "",
            "Validation Command Results",
        ]
    )
    for entry in command_results:
        lines.append(f"- {entry['name']}: rc={entry['rc']} log={entry['log']}")
    lines.append(f"- Files changed tracked in this report: {files_changed_count}")
    return "\n".join(lines).rstrip() + "\n"


def create_bundle(run_id: str) -> dict[str, Any]:
    run_dir = REPO_ROOT / "tools" / "codex" / "runs" / run_id
    z_dir = run_dir / INTEGRATOR
    logs_dir = z_dir / "LOGS"
    logs_dir.mkdir(parents=True, exist_ok=True)

    command_specs = [
        ("contracts_check", ["python", "tools/codex/factory_cli.py", "contracts-check"]),
        ("preflight", ["python", "tools/codex/factory_cli.py", "preflight", "--run-id", run_id]),
        ("bundle_init", ["python", "tools/codex/factory_cli.py", "bundle-init", "--run-id", run_id]),
        ("bundle_validate", ["python", "tools/codex/factory_cli.py", "bundle-validate", "--run-id", run_id]),
        ("integrate", ["python", "tools/codex/factory_cli.py", "integrate", "--run-id", run_id]),
        ("self_test", ["python", "tools/codex/factory_cli.py", "self-test"]),
        ("unit_tests", ["python", "-m", "unittest", "discover", "-s", "tools/codex/factory/tests", "-p", "test_*.py"]),
        ("launch_dry_run", ["python", "tools/codex/factory_cli.py", "launch", "--run-id", f"{run_id}_dry", "--dry-run"]),
        ("ledger", ["python", "tools/codex/factory_cli.py", "ledger", "--limit", "10"]),
    ]
    command_results: list[dict[str, Any]] = []
    for name, command in command_specs:
        log_path = logs_dir / f"{name}.log.txt"
        command_results.append(_run(name, command, REPO_ROOT, log_path))

    log_index_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "owner": INTEGRATOR,
        "logs": [
            {
                "name": entry["name"],
                "path": Path(entry["log"]).relative_to(z_dir).as_posix(),
                "rc": entry["rc"],
            }
            for entry in command_results
        ],
    }
    write_json(logs_dir / "INDEX.json", log_index_payload)

    improvements_payload = read_json(REPO_ROOT / "tools/codex/contracts/factory/improvements_registry.json")
    improvements = list(improvements_payload.get("improvements", []))

    changed_paths = _collect_changed_paths()
    files_changed_entries = []
    for rel in changed_paths:
        path = REPO_ROOT / rel
        files_changed_entries.append(
            {
                "path": rel,
                "change_type": "modified" if _head_exists(rel) else "added",
                "reason": "factory_hardening",
                "sha256": _sha256(path),
            }
        )

    files_changed_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "owner": INTEGRATOR,
        "changes": files_changed_entries,
    }
    write_json(z_dir / "FILES_CHANGED.json", files_changed_payload)

    patch = unified_patch_for_paths(changed_paths)
    write_text(z_dir / "DIFF.patch", patch)

    self_test_output = (logs_dir / "self_test.log.txt").read_text(encoding="utf-8")
    self_test_payload = {}
    try:
        self_test_payload = json.loads(self_test_output[self_test_output.index("{") :])
    except Exception:
        self_test_payload = {"status": "BLOCKED", "deterministic": False, "run_id": ""}

    required_names = {"contracts_check", "bundle_validate", "integrate", "self_test", "unit_tests"}
    required = [entry for entry in command_results if entry["name"] in required_names]
    required_failed = [entry for entry in required if entry["rc"] != 0]
    final_status = "PASS" if not required_failed else "BLOCKED"

    status_payload = {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": INTEGRATOR,
        "status": final_status,
        "started_at": iso_utc(),
        "ended_at": iso_utc(),
        "required_checks": [
            {"name": entry["name"], "status": "PASS" if entry["rc"] == 0 else "BLOCKED", "rc": entry["rc"], "log": entry["log"]}
            for entry in required
        ],
        "optional_checks": [
            {"name": entry["name"], "status": "PASS" if entry["rc"] == 0 else "WARN", "rc": entry["rc"], "log": entry["log"]}
            for entry in command_results
            if entry["name"] not in required_names
        ],
        "errors": [
            {"kind": "required_check", "name": entry["name"], "rc": entry["rc"], "log": entry["log"]}
            for entry in required_failed
        ],
        "warnings": [],
        "artifacts": [
            "FINAL_REPORT.txt",
            "STATUS.json",
            "FILES_CHANGED.json",
            "DIFF.patch",
            "LOGS/",
        ],
    }
    write_json(z_dir / "STATUS.json", status_payload)

    report = _render_report(
        run_id=run_id,
        command_results=command_results,
        improvements=improvements,
        files_changed_count=len(files_changed_entries),
        self_test_summary=self_test_payload,
    )
    write_text(z_dir / "FINAL_REPORT.txt", report)
    return {
        "run_id": run_id,
        "status": final_status,
        "changed_files": len(files_changed_entries),
        "improvements": len(improvements),
        "z_dir": z_dir.as_posix(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate hardening run bundle artifacts.")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    payload = create_bundle(args.run_id)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
