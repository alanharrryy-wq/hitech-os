from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent
FORGEOS_ROOT = REPO_ROOT / "forgeos"
FORGEOS_SCRIPTS = FORGEOS_ROOT / "scripts"
EVIDENCE_DEFAULT = REPO_ROOT / "tools" / "_local" / "evidence"


def _ensure_exists(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")


def _pythonpath_for(*relative_entries: str) -> str:
    entries = [str((FORGEOS_ROOT / rel).resolve()) for rel in relative_entries]
    existing = os.environ.get("PYTHONPATH", "")
    return os.pathsep.join(entries + ([existing] if existing else []))


def _run_subprocess(
    cmd: list[str],
    cwd: Path,
    extra_pythonpath: str | None = None,
) -> int:
    env = os.environ.copy()
    if extra_pythonpath:
        env["PYTHONPATH"] = extra_pythonpath
    process = subprocess.run(cmd, cwd=str(cwd), env=env, check=False)
    return int(process.returncode)


def _emit_json(payload: dict[str, object], output_path: Path | None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=True)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    print(text)


def cmd_validate_boundaries(args: argparse.Namespace) -> int:
    _ensure_exists(FORGEOS_ROOT, "ForgeOS root")
    _ensure_exists(FORGEOS_SCRIPTS / "validate_import_boundaries.py", "Boundary validator")
    report_path = Path(args.report).resolve() if args.report else (Path(args.evidence_dir).resolve() / "forgeos_import_boundaries_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str((FORGEOS_SCRIPTS / "validate_import_boundaries.py").resolve()),
        "--root",
        str(FORGEOS_ROOT.resolve()),
        "--report",
        str(report_path),
    ]
    return _run_subprocess(cmd=cmd, cwd=FORGEOS_ROOT)


def cmd_package_dry_run(args: argparse.Namespace) -> int:
    _ensure_exists(FORGEOS_ROOT, "ForgeOS root")
    _ensure_exists(FORGEOS_SCRIPTS / "package_dry_run.py", "Package dry-run validator")
    report_path = Path(args.report).resolve() if args.report else (Path(args.evidence_dir).resolve() / "forgeos_package_dry_run_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str((FORGEOS_SCRIPTS / "package_dry_run.py").resolve()),
        "--root",
        str(FORGEOS_ROOT.resolve()),
        "--kernel-version",
        str(args.kernel_version),
        "--report",
        str(report_path),
    ]
    return _run_subprocess(cmd=cmd, cwd=FORGEOS_ROOT)


def _append_sys_path(entries: Iterable[Path]) -> None:
    for entry in entries:
        text = str(entry.resolve())
        if text not in sys.path:
            sys.path.insert(0, text)


def cmd_repo_analyzer(args: argparse.Namespace) -> int:
    _ensure_exists(FORGEOS_ROOT, "ForgeOS root")
    _append_sys_path(
        [
            FORGEOS_ROOT / "platform" / "forge_kernel" / "src",
            FORGEOS_ROOT / "platform" / "forge_commons" / "src",
            FORGEOS_ROOT / "products" / "repo_analyzer" / "src",
        ]
    )

    from forge_commons import ForgeCommonsBootstrap  # type: ignore
    from forge_kernel import HostContribution, KernelBootstrap, RuntimeState  # type: ignore
    from repo_analyzer import RepoAnalyzerRuntime  # type: ignore

    target_root = Path(args.target_root).resolve()
    if not target_root.exists():
        raise FileNotFoundError(f"target root does not exist: {target_root}")

    output_path = Path(args.output).resolve() if args.output else None
    actor = args.actor or "root.forgeos.entrypoint"
    correlation_id = args.correlation_id or "forgeos-repo-analyzer"

    session = KernelBootstrap.start(kernel_version=args.kernel_version)
    commons = ForgeCommonsBootstrap.start(contracts=session.contracts)
    runtime = RepoAnalyzerRuntime(history_runs=commons.history_runs)
    runtime_id = "product.repo_analyzer"
    contribution_registered = False

    try:
        session.lifecycle.register_runtime(runtime_id)
        session.lifecycle.transition(runtime_id, RuntimeState.PREPARED, "prepared")
        runtime.prepare(str(target_root))
        runtime.activate()
        session.lifecycle.transition(runtime_id, RuntimeState.ACTIVE, "active")

        contribution = HostContribution(
            contribution_id=runtime.contribution_id,
            slot_id=runtime.slot_id,
            product_id=runtime.product_id,
            surface_kind=runtime.surface_kind,
            metadata={"product": runtime.product_id, "entrypoint": "root"},
            actions=runtime.contribution_actions(),
        )
        session.host_shell.register_contribution(
            contribution=contribution,
            actor=actor,
            correlation_id=correlation_id + "-register",
        )
        contribution_registered = True
        session.host_shell.set_visible(runtime.slot_id, True)

        summary = runtime.analyze_repository(actor=actor, correlation_id=correlation_id)
        payload: dict[str, object] = {
            "status": "PASS",
            "product": runtime.product_id,
            "target_root": str(target_root),
            "kernel_version": session.kernel_version,
            "summary": {
                "root_path": summary.root_path,
                "total_files": summary.total_files,
                "total_lines": summary.total_lines,
                "generated_at_utc": summary.generated_at_utc,
                "extension_counts": summary.extension_counts,
            },
            "host_shell": {
                "contribution_count": session.host_shell.snapshot().contribution_count,
                "slot_bindings": session.host_shell.snapshot().slot_bindings,
            },
            "history_runs": [run.__dict__ for run in commons.history_runs.all_runs()],
        }

        if args.query:
            payload["search_results"] = [match.__dict__ for match in runtime.search(args.query, limit=args.search_limit)]
        if args.preview_path:
            payload["preview"] = {
                "file_path": str(Path(args.preview_path).resolve()),
                "lines": runtime.preview_file(args.preview_path, max_lines=args.preview_lines),
            }

        _emit_json(payload=payload, output_path=output_path)
        return 0
    finally:
        if contribution_registered:
            session.host_shell.dispose(actor=actor, correlation_id=correlation_id + "-dispose-host")
        try:
            if runtime.state.value == "active":
                runtime.suspend()
                session.lifecycle.transition(runtime_id, RuntimeState.SUSPENDED, "suspended")
        except Exception:
            pass
        try:
            session.lifecycle.transition(runtime_id, RuntimeState.DISPOSING, "disposing")
        except Exception:
            pass
        try:
            runtime.dispose()
        except Exception:
            pass
        try:
            session.lifecycle.transition(runtime_id, RuntimeState.DISPOSED, "disposed")
        except Exception:
            pass
        commons.dispose()


QUALITY_GATE_STEPS = (
    {
        "name": "Import boundary validation",
        "cmd": [sys.executable, str((FORGEOS_SCRIPTS / "validate_import_boundaries.py").resolve()), "--root", str(FORGEOS_ROOT.resolve()), "--report", "{evidence}/forgeos_import_boundaries_report.json"],
        "cwd": FORGEOS_ROOT,
        "pythonpath": None,
    },
    {
        "name": "Package dry-run validation",
        "cmd": [sys.executable, str((FORGEOS_SCRIPTS / "package_dry_run.py").resolve()), "--root", str(FORGEOS_ROOT.resolve()), "--kernel-version", "{kernel_version}", "--report", "{evidence}/forgeos_package_dry_run_report.json"],
        "cwd": FORGEOS_ROOT,
        "pythonpath": None,
    },
    {
        "name": "Kernel tests",
        "cmd": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        "cwd": FORGEOS_ROOT / "platform" / "forge_kernel",
        "pythonpath": _pythonpath_for(
            "platform/forge_kernel/src",
            "platform/forge_commons/src",
            "products/dummy_product/src",
            "products/repo_analyzer/src",
            "products/cloudflare_guardian/src",
            "products/orchestrator_bridge/src",
        ),
    },
    {
        "name": "Commons tests",
        "cmd": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        "cwd": FORGEOS_ROOT / "platform" / "forge_commons",
        "pythonpath": _pythonpath_for(
            "platform/forge_commons/src",
            "platform/forge_kernel/src",
        ),
    },
    {
        "name": "Repo Analyzer tests",
        "cmd": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        "cwd": FORGEOS_ROOT / "products" / "repo_analyzer",
        "pythonpath": _pythonpath_for(
            "products/repo_analyzer/src",
            "platform/forge_kernel/src",
            "platform/forge_commons/src",
        ),
    },
    {
        "name": "Cloudflare Guardian tests",
        "cmd": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        "cwd": FORGEOS_ROOT / "products" / "cloudflare_guardian",
        "pythonpath": _pythonpath_for(
            "products/cloudflare_guardian/src",
            "platform/forge_kernel/src",
            "platform/forge_commons/src",
        ),
    },
    {
        "name": "Orchestrator Bridge tests",
        "cmd": [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        "cwd": FORGEOS_ROOT / "products" / "orchestrator_bridge",
        "pythonpath": _pythonpath_for(
            "products/orchestrator_bridge/src",
            "platform/forge_kernel/src",
            "platform/forge_commons/src",
        ),
    },
)


def cmd_quality_gate(args: argparse.Namespace) -> int:
    _ensure_exists(FORGEOS_ROOT, "ForgeOS root")
    evidence_dir = Path(args.evidence_dir).resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    print(f"[ForgeOS] Running root-authority quality gate")
    print(f"[ForgeOS] Repo root: {REPO_ROOT}")
    print(f"[ForgeOS] ForgeOS root: {FORGEOS_ROOT}")
    print(f"[ForgeOS] Evidence dir: {evidence_dir}")

    failed_steps: list[str] = []
    for step in QUALITY_GATE_STEPS:
        rendered_cmd = [
            item.format(evidence=str(evidence_dir), kernel_version=str(args.kernel_version))
            for item in step["cmd"]
        ]
        print(f"[ForgeOS] {step['name']}...")
        code = _run_subprocess(
            cmd=rendered_cmd,
            cwd=step["cwd"],
            extra_pythonpath=step["pythonpath"],
        )
        if code != 0:
            failed_steps.append(step["name"])
            if args.fail_fast:
                break

    if failed_steps:
        print(f"[ForgeOS] Quality gate FAILED. Failed steps: {', '.join(failed_steps)}")
        return 1

    print("[ForgeOS] Quality gate PASSED.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Root authority entrypoint for ForgeOS.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_validate = subparsers.add_parser("validate-boundaries", help="Run ForgeOS import boundary validation.")
    parser_validate.add_argument("--evidence-dir", default=str(EVIDENCE_DEFAULT))
    parser_validate.add_argument("--report", default="")
    parser_validate.set_defaults(func=cmd_validate_boundaries)

    parser_package = subparsers.add_parser("package-dry-run", help="Run ForgeOS package dry-run validation.")
    parser_package.add_argument("--kernel-version", default="0.1.0")
    parser_package.add_argument("--evidence-dir", default=str(EVIDENCE_DEFAULT))
    parser_package.add_argument("--report", default="")
    parser_package.set_defaults(func=cmd_package_dry_run)

    parser_repo = subparsers.add_parser("repo-analyzer", help="Run repo_analyzer through ForgeOS root authority.")
    parser_repo.add_argument("--target-root", default=str(REPO_ROOT))
    parser_repo.add_argument("--kernel-version", default="0.1.0")
    parser_repo.add_argument("--actor", default="root.forgeos.entrypoint")
    parser_repo.add_argument("--correlation-id", default="forgeos-repo-analyzer")
    parser_repo.add_argument("--output", default="")
    parser_repo.add_argument("--query", default="")
    parser_repo.add_argument("--search-limit", type=int, default=50)
    parser_repo.add_argument("--preview-path", default="")
    parser_repo.add_argument("--preview-lines", type=int, default=80)
    parser_repo.set_defaults(func=cmd_repo_analyzer)

    parser_quality = subparsers.add_parser("quality-gate", help="Run the official ForgeOS root quality gate.")
    parser_quality.add_argument("--kernel-version", default="0.1.0")
    parser_quality.add_argument("--evidence-dir", default=str(EVIDENCE_DEFAULT))
    parser_quality.add_argument("--fail-fast", action="store_true")
    parser_quality.set_defaults(func=cmd_quality_gate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if getattr(args, "output", "") == "":
        args.output = None
    if getattr(args, "query", "") == "":
        args.query = None
    if getattr(args, "preview_path", "") == "":
        args.preview_path = None
    if getattr(args, "report", "") == "":
        args.report = None
    try:
        return int(args.func(args))
    except Exception as exc:  # noqa: BLE001
        print(f"[ForgeOS] ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
