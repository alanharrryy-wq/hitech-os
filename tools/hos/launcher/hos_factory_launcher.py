from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

WORKERS: tuple[str, ...] = ("A_core", "B_tooling", "C_features", "D_validation", "Z_aggregator")
DEFAULT_FALLBACK_REPO = Path(r"F:\repos\hitech-os")
DEFAULT_BASE_BRANCH = "main"
WORKTREE_BRANCH_PREFIX = "hos/factory-launcher"
WORKTREE_ROOT_REL = Path("tools") / "codex" / "worktrees"
RUNS_ROOT_REL = Path("tools") / "codex" / "runs"
WORKSPACES_REL = Path("tools") / "hos" / "launcher" / "workspaces"

ENV_RUN_ID = "RUN_ID"
ENV_UPDATE = "HOS_LAUNCHER_UPDATE"
ENV_BASE_BRANCH = "HOS_LAUNCHER_BASE_BRANCH"
ENV_CODE_CMD = "HOS_LAUNCHER_CODE_CMD"


class LauncherError(RuntimeError):
    pass


@dataclass
class Summary:
    ok: bool
    run_id: str
    repo_root: str
    worktrees: dict[str, str]
    opened: list[str]
    warnings: list[str]
    errors: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": bool(self.ok),
            "run_id": self.run_id,
            "repo_root": self.repo_root,
            "worktrees": dict(self.worktrees),
            "opened": list(self.opened),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


class LauncherLogger:
    def __init__(self, log_path: Path) -> None:
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str) -> None:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{stamp} [{level}] {message.rstrip()}\n"
        with self.log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)

    def log_process(self, label: str, text: str) -> None:
        stripped = text.strip()
        if not stripped:
            return
        for line in stripped.splitlines():
            self.log(label, line)


def _env_truthy(name: str) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return False
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _normalize_path(value: Path | str) -> str:
    return str(Path(value).resolve(strict=False)).rstrip("\\/").lower()


def _run_command(
    args: list[str],
    *,
    cwd: Path,
    logger: LauncherLogger,
    check: bool,
    timeout_seconds: float = 120.0,
) -> subprocess.CompletedProcess[str]:
    logger.log("CMD", f"cwd={cwd} :: {' '.join(args)}")
    try:
        completed = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=max(1.0, timeout_seconds),
        )
    except FileNotFoundError as exc:
        raise LauncherError(f"Command not found: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise LauncherError(f"Command timed out: {' '.join(args)}") from exc

    logger.log("CMD", f"rc={completed.returncode}")
    logger.log_process("STDOUT", completed.stdout)
    logger.log_process("STDERR", completed.stderr)

    if check and completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip() or "no output"
        raise LauncherError(f"Command failed ({completed.returncode}): {' '.join(args)} :: {stderr}")
    return completed


def _git_toplevel(start_dir: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(start_dir), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    text = completed.stdout.strip()
    if not text:
        return None
    return Path(text).resolve()


def _resolve_repo_root() -> Path:
    if shutil.which("git") is None:
        raise LauncherError("git is not available in PATH.")

    script_repo = Path(__file__).resolve().parents[3]
    probes = [script_repo, Path.cwd()]
    for probe in probes:
        detected = _git_toplevel(probe)
        if detected:
            return detected

    if DEFAULT_FALLBACK_REPO.exists():
        return DEFAULT_FALLBACK_REPO.resolve()

    raise LauncherError(
        f"Unable to resolve repository root via git; fallback path does not exist: {DEFAULT_FALLBACK_REPO}"
    )


def _resolve_run_id(explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    from_env = os.environ.get(ENV_RUN_ID, "").strip()
    if from_env:
        return from_env
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _current_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _resolve_code_program(explicit: str | None, *, logger: LauncherLogger) -> str:
    if explicit and explicit.strip():
        candidate = explicit.strip()
        explicit_path = Path(candidate.strip('"'))
        if explicit_path.exists():
            return str(explicit_path)
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
        raise LauncherError(f"Provided code command is not callable: {explicit}")

    for command in ("code", "code.cmd"):
        resolved = shutil.which(command)
        if resolved:
            return resolved

    local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
    program_files = os.environ.get("ProgramFiles", "").strip()
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "").strip()

    search_paths = [
        Path(local_appdata) / "Programs" / "Microsoft VS Code" / "Code.exe" if local_appdata else None,
        Path(program_files) / "Microsoft VS Code" / "Code.exe" if program_files else None,
        Path(program_files_x86) / "Microsoft VS Code" / "Code.exe" if program_files_x86 else None,
        Path(r"C:\Users\alanh\AppData\Local\Programs\Microsoft VS Code\Code.exe"),
    ]
    for item in search_paths:
        if item and item.exists():
            return str(item)

    logger.log("WARN", "Could not resolve 'code' command or Code.exe from common install locations.")
    raise LauncherError("VS Code CLI is unavailable. Install 'code' command or provide --code-cmd.")


def _verify_code_program(code_program: str, *, repo_root: Path, logger: LauncherLogger) -> None:
    _run_command([code_program, "--version"], cwd=repo_root, logger=logger, check=True, timeout_seconds=20.0)


def _parse_worktree_porcelain(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            if current:
                rows.append(current)
                current = {}
            continue
        if " " in line:
            key, value = line.split(" ", 1)
        else:
            key, value = line, ""
        current[key] = value
    if current:
        rows.append(current)
    return rows


def _worktree_map(repo_root: Path, *, logger: LauncherLogger) -> dict[str, dict[str, str]]:
    completed = _run_command(
        ["git", "-C", str(repo_root), "worktree", "list", "--porcelain"],
        cwd=repo_root,
        logger=logger,
        check=True,
    )
    mapping: dict[str, dict[str, str]] = {}
    for row in _parse_worktree_porcelain(completed.stdout):
        raw_path = row.get("worktree", "").strip()
        if not raw_path:
            continue
        mapping[_normalize_path(raw_path)] = row
    return mapping


def _short_branch_name(raw_ref: str | None) -> str:
    if raw_ref is None:
        return ""
    text = raw_ref.strip()
    if text.startswith("refs/heads/"):
        return text[len("refs/heads/") :]
    return text


def _git_ref_exists(repo_root: Path, ref_name: str, *, logger: LauncherLogger) -> bool:
    completed = _run_command(
        ["git", "-C", str(repo_root), "show-ref", "--verify", "--quiet", ref_name],
        cwd=repo_root,
        logger=logger,
        check=False,
    )
    return completed.returncode == 0


def _resolve_base_ref(repo_root: Path, base_branch: str, *, logger: LauncherLogger) -> str:
    local_ref = f"refs/heads/{base_branch}"
    remote_ref = f"refs/remotes/origin/{base_branch}"
    if _git_ref_exists(repo_root, local_ref, logger=logger):
        return base_branch
    if _git_ref_exists(repo_root, remote_ref, logger=logger):
        return f"origin/{base_branch}"
    raise LauncherError(f"Base branch '{base_branch}' was not found locally or at origin/{base_branch}.")


def _ensure_worktrees(
    repo_root: Path,
    *,
    base_branch: str,
    create_missing: bool,
    logger: LauncherLogger,
    warnings: list[str],
) -> dict[str, Path]:
    root = repo_root / WORKTREE_ROOT_REL
    root.mkdir(parents=True, exist_ok=True)
    mapping = _worktree_map(repo_root, logger=logger)
    base_ref = _resolve_base_ref(repo_root, base_branch, logger=logger)

    ensured: dict[str, Path] = {}
    for worker in WORKERS:
        expected_path = root / worker
        expected_norm = _normalize_path(expected_path)
        expected_branch = f"{WORKTREE_BRANCH_PREFIX}/{worker}"

        if expected_path.exists():
            if not expected_path.is_dir():
                raise LauncherError(f"Worktree path exists but is not a directory: {expected_path}")
            info = mapping.get(expected_norm)
            if info is None:
                raise LauncherError(
                    "Worktree path exists but is not registered in this repository worktree list: "
                    f"{expected_path}"
                )
            branch = _short_branch_name(info.get("branch", ""))
            if branch and branch != expected_branch:
                warnings.append(
                    f"{worker}: existing worktree branch is '{branch}' (expected '{expected_branch}'); left unchanged."
                )
            logger.log("INFO", f"Reusing worktree for {worker}: {expected_path}")
            ensured[worker] = expected_path.resolve()
            continue

        if not create_missing:
            raise LauncherError(f"Missing required worktree: {expected_path}")

        expected_path.parent.mkdir(parents=True, exist_ok=True)
        ref_name = f"refs/heads/{expected_branch}"
        if _git_ref_exists(repo_root, ref_name, logger=logger):
            args = ["git", "-C", str(repo_root), "worktree", "add", str(expected_path), expected_branch]
        else:
            args = ["git", "-C", str(repo_root), "worktree", "add", "-b", expected_branch, str(expected_path), base_ref]

        _run_command(args, cwd=repo_root, logger=logger, check=True)
        mapping = _worktree_map(repo_root, logger=logger)
        if expected_norm not in mapping:
            raise LauncherError(f"Worktree creation did not register expected path: {expected_path}")
        logger.log("INFO", f"Created worktree for {worker}: {expected_path} (base={base_ref})")
        ensured[worker] = expected_path.resolve()

    return ensured


def _workspace_payload(worker: str, worktree_path: Path, repo_name: str) -> dict[str, Any]:
    return {
        "folders": [{"path": str(worktree_path)}],
        "settings": {
            "terminal.integrated.defaultProfile.windows": "PowerShell",
            "files.eol": "\r\n",
            "files.encoding": "utf8",
            "window.title": f"HITECH-OS {worker} | {repo_name}",
        },
    }


def _write_workspace_files(
    repo_root: Path,
    *,
    worktrees: dict[str, Path],
    logger: LauncherLogger,
) -> dict[str, Path]:
    workspace_root = repo_root / WORKSPACES_REL
    workspace_root.mkdir(parents=True, exist_ok=True)
    repo_name = repo_root.name
    files: dict[str, Path] = {}

    for worker in WORKERS:
        worktree_path = worktrees[worker]
        target = workspace_root / f"{worker}.code-workspace"
        payload = _workspace_payload(worker, worktree_path, repo_name)
        text = json.dumps(payload, indent=2, ensure_ascii=True) + "\n"
        prior = target.read_text(encoding="utf-8") if target.exists() else None
        if prior != text:
            target.write_text(text, encoding="utf-8", newline="\n")
            logger.log("INFO", f"Wrote workspace file: {target}")
        else:
            logger.log("INFO", f"Workspace file unchanged: {target}")
        files[worker] = target.resolve()
    return files


def _validate_workspace_files(
    repo_root: Path,
    *,
    worktrees: dict[str, Path],
    logger: LauncherLogger,
) -> None:
    workspace_root = repo_root / WORKSPACES_REL
    for worker in WORKERS:
        expected_workspace = workspace_root / f"{worker}.code-workspace"
        if not expected_workspace.exists():
            raise LauncherError(f"Missing workspace file: {expected_workspace}")
        try:
            payload = json.loads(expected_workspace.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise LauncherError(f"Workspace JSON is invalid: {expected_workspace}") from exc

        folders = payload.get("folders", [])
        if not isinstance(folders, list) or not folders:
            raise LauncherError(f"Workspace has no folders entry: {expected_workspace}")
        folder0 = folders[0]
        if not isinstance(folder0, dict) or "path" not in folder0:
            raise LauncherError(f"Workspace folder entry is invalid: {expected_workspace}")

        expected = _normalize_path(worktrees[worker])
        actual = _normalize_path(str(folder0["path"]))
        if actual != expected:
            raise LauncherError(
                f"Workspace path mismatch for {worker}: expected {worktrees[worker]}, got {folder0['path']}"
            )
        logger.log("INFO", f"Validated workspace file: {expected_workspace}")


def _open_vscode_windows(
    *,
    code_program: str,
    repo_root: Path,
    workspace_files: dict[str, Path],
    logger: LauncherLogger,
) -> list[str]:
    opened: list[str] = []
    for worker in WORKERS:
        workspace_path = workspace_files[worker]
        completed = _run_command(
            [code_program, "--new-window", "--reuse-window=false", str(workspace_path)],
            cwd=repo_root,
            logger=logger,
            check=False,
            timeout_seconds=45.0,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
            raise LauncherError(f"Failed opening VS Code for {worker}: {stderr}")
        opened.append(worker)
        time.sleep(0.2)
    return opened


def _maybe_self_update(repo_root: Path, *, logger: LauncherLogger, requested: bool) -> None:
    if not requested:
        logger.log("INFO", "Self-update is OFF.")
        return
    logger.log("INFO", "Self-update requested: running git pull --ff-only.")
    _run_command(
        ["git", "-C", str(repo_root), "pull", "--ff-only"],
        cwd=repo_root,
        logger=logger,
        check=True,
        timeout_seconds=180.0,
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="HITECH-OS minimal factory launcher.")
    parser.add_argument("--run-id", default=None, help="Run ID used for debug logs.")
    parser.add_argument(
        "--base-branch",
        default=os.environ.get(ENV_BASE_BRANCH, DEFAULT_BASE_BRANCH),
        help="Base branch used when creating missing worktrees.",
    )
    parser.add_argument(
        "--code-cmd",
        default=os.environ.get(ENV_CODE_CMD),
        help="Optional VS Code command/path override.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help=f"Enable self-update before launch (same effect as {ENV_UPDATE}=1).",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validation-only mode: check worktrees/workspaces/VS Code command without opening windows.",
    )
    return parser


def _run(args: argparse.Namespace) -> Summary:
    run_id = _resolve_run_id(args.run_id)
    warnings: list[str] = []
    errors: list[str] = []
    worktree_summary: dict[str, str] = {}
    opened: list[str] = []

    try:
        repo_root = _resolve_repo_root()
    except Exception as exc:
        errors.append(str(exc))
        return Summary(
            ok=False,
            run_id=run_id,
            repo_root=str(DEFAULT_FALLBACK_REPO),
            worktrees=worktree_summary,
            opened=opened,
            warnings=warnings,
            errors=errors,
        )

    debug_dir = repo_root / RUNS_ROOT_REL / run_id / "_debug"
    try:
        debug_dir.mkdir(parents=True, exist_ok=True)
        log_path = debug_dir / f"LAUNCHER_{_current_stamp()}.log"
        logger = LauncherLogger(log_path)
    except Exception as exc:
        errors.append(f"Unable to initialize launcher log path at {debug_dir}: {exc}")
        return Summary(
            ok=False,
            run_id=run_id,
            repo_root=str(repo_root),
            worktrees=worktree_summary,
            opened=opened,
            warnings=warnings,
            errors=errors,
        )

    logger.log("INFO", f"run_id={run_id}")
    logger.log("INFO", f"repo_root={repo_root}")
    logger.log("INFO", f"mode={'validate' if args.validate else 'launch'}")
    logger.log("INFO", f"base_branch={args.base_branch}")

    try:
        if shutil.which("git") is None:
            raise LauncherError("git is not available in PATH.")

        update_requested = bool(args.update or _env_truthy(ENV_UPDATE))
        _maybe_self_update(repo_root, logger=logger, requested=update_requested)

        code_program = _resolve_code_program(args.code_cmd, logger=logger)
        logger.log("INFO", f"Resolved VS Code command: {code_program}")
        _verify_code_program(code_program, repo_root=repo_root, logger=logger)

        worktrees = _ensure_worktrees(
            repo_root,
            base_branch=args.base_branch,
            create_missing=not args.validate,
            logger=logger,
            warnings=warnings,
        )
        worktree_summary = {worker: str(worktrees[worker]) for worker in WORKERS}

        if args.validate:
            _validate_workspace_files(repo_root, worktrees=worktrees, logger=logger)
            logger.log("INFO", "Validation checks completed successfully.")
        else:
            workspace_files = _write_workspace_files(repo_root, worktrees=worktrees, logger=logger)
            opened = _open_vscode_windows(
                code_program=code_program,
                repo_root=repo_root,
                workspace_files=workspace_files,
                logger=logger,
            )
            logger.log("INFO", "VS Code windows opened for all workers in A/B/C/D/Z order.")

    except LauncherError as exc:
        message = str(exc)
        errors.append(message)
        logger.log("ERROR", message)
    except Exception as exc:  # pragma: no cover - defensive fallback
        message = f"Unhandled launcher error: {exc!r}"
        errors.append(message)
        logger.log("ERROR", message)

    ok = len(errors) == 0
    summary = Summary(
        ok=ok,
        run_id=run_id,
        repo_root=str(repo_root),
        worktrees=worktree_summary,
        opened=opened,
        warnings=warnings,
        errors=errors,
    )

    summary_path = debug_dir / "LAUNCHER_SUMMARY.json"
    try:
        summary_path.write_text(json.dumps(summary.as_dict(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        logger.log("INFO", f"Wrote launcher summary: {summary_path}")
    except Exception as exc:
        warning = f"Unable to write launcher summary file: {exc}"
        summary.warnings.append(warning)
        logger.log("WARN", warning)
    logger.log("INFO", f"Launcher completed with ok={ok}")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    summary = _run(args)
    sys.stdout.write(json.dumps(summary.as_dict(), ensure_ascii=True) + "\n")
    return 0 if summary.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
