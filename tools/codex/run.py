#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = REPO_ROOT / "tools" / "codex"
RUNS_DIR = CODEX_DIR / "runs"
INTEGRATOR_DIR = "Z_integrator"
LOGS_DIR = "LOGS"


def now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_cmd(cmd: str, cwd: Path) -> Tuple[int, str]:
    process = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output: List[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        output.append(line.decode("utf-8", errors="replace"))
    rc = process.wait()
    return rc, "".join(output)


def detect_any(repo: Path, any_files: Sequence[str]) -> bool:
    return any((repo / candidate).exists() for candidate in any_files)


def load_adapter() -> Tuple[Path, Dict[str, Any]]:
    validation_json = CODEX_DIR / "validation.json"
    validation_yaml = CODEX_DIR / "validation.yaml"

    if validation_json.exists():
        return validation_json, json.loads(validation_json.read_text(encoding="utf-8"))

    if validation_yaml.exists():
        raise RuntimeError("validation.yaml found but YAML parsing is disabled by design. Use validation.json.")

    raise RuntimeError("No validation adapter found. Expected tools/codex/validation.json.")


def is_required(step_cfg: Dict[str, Any]) -> bool:
    allow_fail = bool(step_cfg.get("allow_fail", False))
    return bool(step_cfg.get("required", not allow_fail))


def append_steps(
    target: List[Dict[str, Any]],
    group: str,
    steps: Sequence[Dict[str, Any]],
) -> None:
    for entry in steps:
        target.append({"group": group, **entry})


def collect_steps(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []
    preflight = (cfg.get("defaults") or {}).get("preflight", []) or []
    append_steps(steps, "preflight", preflight)

    guardrails = (cfg.get("guardrails") or {}).get("commands", []) or []
    append_steps(steps, "guardrails", guardrails)

    node_cfg = cfg.get("node") or {}
    node_detect = (node_cfg.get("detect") or {}).get("any_files", []) or []
    if detect_any(REPO_ROOT, node_detect):
        append_steps(steps, "node", node_cfg.get("commands", []) or [])

    playwright_cfg = cfg.get("playwright") or {}
    playwright_detect = (playwright_cfg.get("detect") or {}).get("any_files", []) or []
    if detect_any(REPO_ROOT, playwright_detect):
        append_steps(steps, "playwright", playwright_cfg.get("commands", []) or [])

    return steps


def result_record(
    *,
    name: str,
    group: str,
    rc: int,
    required: bool,
    allow_fail: bool,
    cmd: str,
    log_path: Path,
) -> Dict[str, Any]:
    return {
        "name": name,
        "group": group,
        "cmd": cmd,
        "rc": rc,
        "required": required,
        "optional": not required,
        "allow_fail": allow_fail,
        "status": "PASS" if rc == 0 else "FAIL",
        "log": str(log_path),
    }


def summarize(results: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    required = [item for item in results if item.get("required")]
    optional = [item for item in results if not item.get("required")]
    return {
        "required": {
            "total": len(required),
            "passed": len([item for item in required if item.get("rc") == 0]),
            "failed": len([item for item in required if item.get("rc") != 0]),
        },
        "optional": {
            "total": len(optional),
            "passed": len([item for item in optional if item.get("rc") == 0]),
            "failed": len([item for item in optional if item.get("rc") != 0]),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=f"preflight_{now_ts()}")
    args = parser.parse_args()

    run_id = args.run_id
    run_dir = RUNS_DIR / run_id / INTEGRATOR_DIR
    logs_dir = run_dir / LOGS_DIR
    run_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    run_log_path = run_dir / "RUN_LOG.txt"
    error_path = run_dir / "ERROR.txt"

    def log(message: str) -> None:
        print(message)
        with run_log_path.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")

    status: Dict[str, Any] = {
        "run_id": run_id,
        "repo": str(REPO_ROOT),
        "adapter": None,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": [],
        "summary": {},
        "final": "UNKNOWN",
        "blocked_reason": None,
        "error": None,
    }

    exit_code = 0

    try:
        adapter_path, cfg = load_adapter()
        status["adapter"] = str(adapter_path)
        steps = collect_steps(cfg)

        log(f"[HITECH-OS] Repo: {REPO_ROOT}")
        log(f"[HITECH-OS] Run : {run_id}")
        log(f"[HITECH-OS] Adapter: {adapter_path}")
        log(f"[HITECH-OS] Output: {run_dir}")

        for step in steps:
            name = str(step.get("name", "unnamed"))
            cmd = str(step.get("cmd", "")).strip()
            group = str(step.get("group", "unknown"))
            allow_fail = bool(step.get("allow_fail", False))
            required = is_required(step)

            if not cmd:
                continue

            log(f"==> [{group}] {name}: {cmd}")
            started_at = time.strftime("%Y-%m-%d %H:%M:%S")
            rc, output = run_cmd(cmd, REPO_ROOT)
            ended_at = time.strftime("%Y-%m-%d %H:%M:%S")

            log_file = logs_dir / f"{name}.log.txt"
            rendered_log = (
                f"# command: {cmd}\n"
                f"# group: {group}\n"
                f"# cwd: {REPO_ROOT}\n"
                f"# required: {required}\n"
                f"# allow_fail: {allow_fail}\n"
                f"# started_at: {started_at}\n"
                f"# ended_at: {ended_at}\n"
                f"# rc: {rc}\n\n"
                f"{output}"
            )
            write_text(log_file, rendered_log)

            status["results"].append(
                result_record(
                    name=name,
                    group=group,
                    rc=rc,
                    required=required,
                    allow_fail=allow_fail,
                    cmd=cmd,
                    log_path=log_file,
                )
            )

            if rc != 0 and required and status["blocked_reason"] is None:
                status["blocked_reason"] = f"required step failed: {name} (rc={rc})"

        status["summary"] = summarize(status["results"])
        required_failures = [item for item in status["results"] if item["required"] and item["rc"] != 0]

        if required_failures:
            status["final"] = "BLOCKED"
            if status["blocked_reason"] is None:
                names = ", ".join(item["name"] for item in required_failures)
                status["blocked_reason"] = f"required steps failed: {names}"
            status["error"] = {
                "message": status["blocked_reason"],
                "required_failures": required_failures,
            }
            write_text(error_path, json.dumps(status["error"], indent=2) + "\n")
            exit_code = 2
            log(f"[BLOCKED] {status['blocked_reason']}")
        else:
            status["final"] = "PASS"
            write_text(error_path, "")
            exit_code = 0
            log("[PASS] all required validation steps succeeded")

    except Exception as exc:  # pragma: no cover - defensive path
        trace = traceback.format_exc()
        status["final"] = "BLOCKED"
        status["blocked_reason"] = f"runner exception: {exc}"
        status["error"] = {"message": str(exc), "traceback": trace}
        write_text(error_path, trace)
        exit_code = 2
        log(f"[FATAL] {exc}")

    finally:
        status["ended_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if not status.get("summary"):
            status["summary"] = summarize(status.get("results", []))
        status_path = run_dir / "STATUS.json"
        write_text(status_path, json.dumps(status, indent=2))
        log(f"[DONE] Wrote: {status_path}")
        log(f"[DONE] Wrote: {run_log_path}")
        log(f"[DONE] Wrote: {error_path}")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
