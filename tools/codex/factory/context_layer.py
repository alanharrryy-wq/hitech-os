#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
CODEX_DIR = REPO_ROOT / "tools" / "codex"
RUNS_ROOT = CODEX_DIR / "runs"
PROMPTS_ROOT = CODEX_DIR / "prompts"
DEFAULT_WORKERS = ("A_core", "B_tooling", "C_features", "D_validation", "Z_aggregator")

CONTRACT_SOURCES = (
    "KERNEL_CONTEXT.md",
    "MODULE_BOUNDARIES.md",
    "ARCHITECTURE_DECISIONS.md",
    "docs/factory/CONTRACT.md",
    "docs/factory/FACTORY_RUNTIME_EXPLAINED.md",
    "docs/factory/ANTI_HALLUCINATION_METRICS_GOVERNANCE.md",
    "docs/factory/MEANINGFUL_EXECUTION_GATE.md",
    "tools/codex/dispatch/execution_rules.json",
    "docs/GOVERNANCE_DOCS.md",
)


def _iso_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _run_git(args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return int(proc.returncode), proc.stdout or "", proc.stderr or ""


def _repo_fingerprint() -> dict[str, Any]:
    rc_head, out_head, _ = _run_git(["rev-parse", "HEAD"])
    rc_branch, out_branch, _ = _run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    rc_status, out_status, _ = _run_git(["status", "--porcelain"])
    rc_remote, out_remote, _ = _run_git(["remote", "-v"])
    rc_submodules, out_submodules, _ = _run_git(["submodule", "status"])
    return {
        "generated_at_utc": _iso_utc(),
        "repo_root": REPO_ROOT.as_posix(),
        "head_commit": out_head.strip() if rc_head == 0 else "",
        "branch": out_branch.strip() if rc_branch == 0 else "",
        "dirty": bool(out_status.strip()) if rc_status == 0 else True,
        "status_porcelain": [line for line in out_status.splitlines() if line.strip()] if rc_status == 0 else [],
        "remote": [line.strip() for line in out_remote.splitlines() if line.strip()] if rc_remote == 0 else [],
        "submodules": [line.strip() for line in out_submodules.splitlines() if line.strip()] if rc_submodules == 0 else [],
    }


def _repo_tree() -> str:
    rc, stdout, _ = _run_git(["ls-files"])
    if rc != 0:
        return "# git ls-files unavailable\n"
    lines = sorted(line.strip() for line in stdout.splitlines() if line.strip())
    return "\n".join(lines) + "\n"


def _contract_summary(contract_paths: list[Path]) -> str:
    lines: list[str] = ["# CONTRACT_SUMMARY", "", "Rules-at-a-glance:"]
    for contract in contract_paths:
        rel = contract.relative_to(REPO_ROOT).as_posix()
        lines.append(f"- Source: `{rel}`")
        text = _read_text(contract)
        headings = [line.strip() for line in text.splitlines() if line.strip().startswith("## ")]
        bullets = [line.strip() for line in text.splitlines() if line.strip().startswith("- ")]
        for heading in headings[:3]:
            lines.append(f"  - {heading}")
        for bullet in bullets[:5]:
            lines.append(f"  - {bullet}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _worker_input_text(run_id: str, worker: str) -> str:
    prompt_path = PROMPTS_ROOT / run_id / f"{worker}_{run_id}.txt"
    if prompt_path.exists():
        prompt = _read_text(prompt_path)
        trimmed = "\n".join(prompt.splitlines()[:200]).strip()
        return (
            f"# WORKER_INPUTS/{worker}.md\n\n"
            f"- run_id: `{run_id}`\n"
            f"- worker: `{worker}`\n"
            f"- source_prompt: `{prompt_path.as_posix()}`\n\n"
            f"## Prompt Snippet\n\n"
            f"```text\n{trimmed}\n```\n"
        )
    return (
        f"# WORKER_INPUTS/{worker}.md\n\n"
        f"- run_id: `{run_id}`\n"
        f"- worker: `{worker}`\n"
        "- source_prompt: missing\n\n"
        "## TODO\n\n"
        "Prompt not found. Generate or materialize prompts before dispatch.\n"
    )


def _target_files(manifest: dict[str, Any]) -> str:
    raw = manifest.get("target_files", []) if isinstance(manifest.get("target_files", []), list) else []
    values = sorted({str(item).replace("\\", "/").strip() for item in raw if str(item).strip()})
    if not values:
        values = [
            "tools/codex/dispatch/validator.py",
            "tools/codex/dispatch/run_iter.ps1",
            "tools/codex/factory/integrator.py",
            "tools/docs_governor/docs_governor.py",
            "docs/GOVERNANCE_DOCS.md",
        ]
    return "\n".join(values) + "\n"


def _shared_references(run_id: str) -> str:
    refs = [
        ("KERNEL_CONTEXT.md", "Kernel context and mandatory execution scope"),
        ("MODULE_BOUNDARIES.md", "Module isolation boundaries"),
        ("ARCHITECTURE_DECISIONS.md", "Architecture decision authority"),
        ("docs/factory/CONTRACT.md", "Factory runtime contract"),
        ("docs/factory/FACTORY_RUNTIME_EXPLAINED.md", "Execution model and stage semantics"),
        ("docs/factory/ANTI_HALLUCINATION_METRICS_GOVERNANCE.md", "Anti-padding and anti-hallucination rules"),
        ("docs/factory/MEANINGFUL_EXECUTION_GATE.md", "Meaningful change enforcement"),
        ("tools/codex/dispatch/execution_rules.json", "Anti-hallucination and LOC governance thresholds"),
        ("docs/GOVERNANCE_DOCS.md", "Documentation governance policy"),
        (f"tools/codex/runs/{run_id}/RUN_MANIFEST.json", "Run manifest and dispatch runtime metadata"),
    ]
    lines = ["# SHARED_REFERENCES", ""]
    for path, reason in refs:
        lines.append(f"- `{path}`: {reason}")
    return "\n".join(lines).rstrip() + "\n"


def _open_questions(manifest: dict[str, Any]) -> str:
    items = manifest.get("open_questions", []) if isinstance(manifest.get("open_questions", []), list) else []
    lines = ["# OPEN_QUESTIONS", ""]
    if not items:
        lines.append("- none")
    else:
        for item in items:
            value = str(item).strip()
            if value:
                lines.append(f"- {value}")
    return "\n".join(lines).rstrip() + "\n"


def _context_fingerprint(context_dir: Path) -> dict[str, Any]:
    files = sorted(
        [path for path in context_dir.rglob("*") if path.is_file() and path.name != "CONTEXT_FINGERPRINT.json"],
        key=lambda p: p.as_posix(),
    )
    entries: list[dict[str, str]] = []
    aggregate_lines: list[str] = []
    for file in files:
        data = file.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        rel = file.relative_to(context_dir).as_posix()
        entries.append({"path": rel, "sha256": digest})
        aggregate_lines.append(f"{rel}:{digest}")
    aggregate = hashlib.sha256("\n".join(aggregate_lines).encode("utf-8")).hexdigest()
    return {
        "generated_at_utc": _iso_utc(),
        "context_dir": context_dir.as_posix(),
        "file_count": len(entries),
        "files": entries,
        "context_sha256": aggregate,
    }


def _write_apply_instructions(run_id: str, z_dir: Path, apply_dir: Path) -> None:
    text = (
        "# APPLY_INSTRUCTIONS\n\n"
        f"RUN_ID: {run_id}\n\n"
        "1. Review `DIFF_MERGED.patch` and `FILES_CHANGED_MERGED.json`.\n"
        "2. Dry-run patch application in `_apply/`.\n"
        "3. Apply and run repo validation commands.\n"
        "4. Commit and push only after checks pass.\n"
    )
    _write_text(z_dir / "APPLY_INSTRUCTIONS.md", text)
    apply_dir.mkdir(parents=True, exist_ok=True)


def _ensure_rework_queue(run_root: Path) -> None:
    for rel in ("_queue/rework/inbox", "_queue/rework/outbox", "_queue/rework/deadletter", "_queue/rework/state"):
        (run_root / rel).mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic run context layer")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--workers", default=",".join(DEFAULT_WORKERS))
    parser.add_argument("--prepare-generated-docs", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = str(args.run_id).strip()
    workers = [item.strip() for item in str(args.workers).split(",") if item.strip()]
    if not workers:
        workers = list(DEFAULT_WORKERS)

    run_root = RUNS_ROOT / run_id
    context_dir = run_root / "_context"
    worker_inputs_dir = context_dir / "WORKER_INPUTS"
    run_manifest_path = run_root / "RUN_MANIFEST.json"
    manifest = _read_json(run_manifest_path)

    run_root.mkdir(parents=True, exist_ok=True)
    context_dir.mkdir(parents=True, exist_ok=True)
    worker_inputs_dir.mkdir(parents=True, exist_ok=True)
    _ensure_rework_queue(run_root)

    contract_paths = [REPO_ROOT / rel for rel in CONTRACT_SOURCES if (REPO_ROOT / rel).exists()]

    manifest_copy = dict(manifest)
    manifest_copy.setdefault("run_id", run_id)
    manifest_copy.setdefault("generated_context_at_utc", _iso_utc())
    manifest_copy.setdefault("workers", workers)

    _write_json(context_dir / "RUN_MANIFEST.json", manifest_copy)
    _write_json(context_dir / "REPO_FINGERPRINT.json", _repo_fingerprint())
    _write_text(context_dir / "REPO_TREE.txt", _repo_tree())
    _write_text(context_dir / "TARGET_FILES.txt", _target_files(manifest_copy))
    _write_text(context_dir / "CONTRACT_SOURCES.txt", "\n".join(CONTRACT_SOURCES) + "\n")
    _write_text(context_dir / "CONTRACT_SUMMARY.md", _contract_summary(contract_paths))

    kernel_src = REPO_ROOT / "KERNEL_CONTEXT.md"
    if kernel_src.exists():
        _write_text(context_dir / "KERNEL_CONTEXT.md", _read_text(kernel_src))
    else:
        _write_text(context_dir / "KERNEL_CONTEXT.md", "# KERNEL_CONTEXT\n\nmissing in repository root.\n")

    runtime_src = REPO_ROOT / "docs" / "factory" / "FACTORY_RUNTIME_EXPLAINED.md"
    if runtime_src.exists():
        _write_text(context_dir / "FACTORY_RUNTIME_EXPLAINED.md", _read_text(runtime_src))
    else:
        _write_text(context_dir / "FACTORY_RUNTIME_EXPLAINED.md", "# FACTORY_RUNTIME_EXPLAINED\n\nmissing source document.\n")

    boundaries_src = REPO_ROOT / "MODULE_BOUNDARIES.md"
    if boundaries_src.exists():
        _write_text(context_dir / "MODULE_BOUNDARIES.md", _read_text(boundaries_src))
    else:
        _write_text(context_dir / "MODULE_BOUNDARIES.md", "# MODULE_BOUNDARIES\n\nmissing source document.\n")

    decisions_src = REPO_ROOT / "ARCHITECTURE_DECISIONS.md"
    if decisions_src.exists():
        _write_text(context_dir / "ARCHITECTURE_DECISIONS.md", _read_text(decisions_src))
    else:
        _write_text(context_dir / "ARCHITECTURE_DECISIONS.md", "# ARCHITECTURE_DECISIONS\n\nmissing source document.\n")

    for worker in workers:
        _write_text(worker_inputs_dir / f"{worker}.md", _worker_input_text(run_id, worker))

    _write_text(context_dir / "SHARED_REFERENCES.md", _shared_references(run_id))
    _write_text(context_dir / "OPEN_QUESTIONS.md", _open_questions(manifest_copy))
    context_fingerprint = _context_fingerprint(context_dir)
    _write_json(context_dir / "CONTEXT_FINGERPRINT.json", context_fingerprint)

    z_dir = run_root / "Z_integrator"
    _write_apply_instructions(run_id, z_dir, run_root / "_apply")

    if args.prepare_generated_docs:
        generated_dir = REPO_ROOT / "docs" / "_generated" / run_id
        generated_dir.mkdir(parents=True, exist_ok=True)
        _write_text(
            generated_dir / "index.md",
            "# Generated Docs Index\n\n- run_id: `{}`\n- status: staging\n".format(run_id),
        )
        _write_json(
            generated_dir / "promotion_manifest.json",
            {
                "schema_version": 1,
                "run_id": run_id,
                "generated_at_utc": _iso_utc(),
                "items": [],
                "rules": {
                    "require_index": True,
                    "max_docs_depth": 5,
                },
            },
        )

    root_manifest = dict(manifest) if isinstance(manifest, dict) else {}
    root_manifest.setdefault("run_id", run_id)
    root_manifest["context_layer"] = {
        "generated_at_utc": _iso_utc(),
        "dir": context_dir.as_posix(),
        "fingerprint_file": (context_dir / "CONTEXT_FINGERPRINT.json").as_posix(),
        "fingerprint_sha256": str(context_fingerprint.get("context_sha256", "")),
    }
    root_manifest["rework_transport"] = "file_queue"
    root_manifest["rework_queue"] = {
        "inbox": (run_root / "_queue" / "rework" / "inbox").as_posix(),
        "outbox": (run_root / "_queue" / "rework" / "outbox").as_posix(),
    }
    _write_json(run_manifest_path, root_manifest)

    payload = {
        "status": "PASS",
        "run_id": run_id,
        "run_root": run_root.as_posix(),
        "context_dir": context_dir.as_posix(),
        "workers": workers,
        "files": {
            "run_manifest": (context_dir / "RUN_MANIFEST.json").as_posix(),
            "repo_fingerprint": (context_dir / "REPO_FINGERPRINT.json").as_posix(),
            "context_fingerprint": (context_dir / "CONTEXT_FINGERPRINT.json").as_posix(),
            "repo_tree": (context_dir / "REPO_TREE.txt").as_posix(),
            "target_files": (context_dir / "TARGET_FILES.txt").as_posix(),
            "contract_sources": (context_dir / "CONTRACT_SOURCES.txt").as_posix(),
            "contract_summary": (context_dir / "CONTRACT_SUMMARY.md").as_posix(),
            "kernel_context": (context_dir / "KERNEL_CONTEXT.md").as_posix(),
            "factory_runtime": (context_dir / "FACTORY_RUNTIME_EXPLAINED.md").as_posix(),
            "module_boundaries": (context_dir / "MODULE_BOUNDARIES.md").as_posix(),
            "architecture_decisions": (context_dir / "ARCHITECTURE_DECISIONS.md").as_posix(),
            "worker_inputs_dir": worker_inputs_dir.as_posix(),
            "shared_references": (context_dir / "SHARED_REFERENCES.md").as_posix(),
            "open_questions": (context_dir / "OPEN_QUESTIONS.md").as_posix(),
            "apply_dir": (run_root / "_apply").as_posix(),
            "apply_instructions": (z_dir / "APPLY_INSTRUCTIONS.md").as_posix(),
        },
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
