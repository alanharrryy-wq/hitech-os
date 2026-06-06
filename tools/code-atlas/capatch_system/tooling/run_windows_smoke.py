#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_audit.telemetry import enrich_payload, write_telemetry_report

ESSENTIAL_PLUGIN_ENV = "CAPATCH_WINDOWS_SMOKE_REQUIRED_PLUGINS"
DEFAULT_REQUIRED_PLUGINS = [
    "fixer.safe-runtime-actions",
    "recommender.safe-fix-plan",
    "verifier.post-fix-verifier",
]


def build_windows_steps(base_dir: Path, workspace_root: Path, ops_file: Path) -> list[dict[str, Any]]:
    python_exe = sys.executable
    capatch = str((base_dir / "capatch.py").resolve())
    workspace = str(workspace_root)
    ops = str(ops_file)
    return [
        {"name": "smoke-test", "argv": [python_exe, capatch, "--smoke-test"]},
        {"name": "plugin-health", "argv": [python_exe, capatch, "--plugin-health"]},
        {"name": "apply", "argv": [python_exe, capatch, "--root-dir", workspace, "--ops-file", ops]},
        {"name": "list-checkpoints", "argv": [python_exe, capatch, "--root-dir", workspace, "--list-checkpoints"]},
        {"name": "rollback-last", "argv": [python_exe, capatch, "--root-dir", workspace, "--rollback-last"]},
    ]


def parse_required_plugins(value: str | None) -> list[str]:
    if not value:
        return list(DEFAULT_REQUIRED_PLUGINS)
    rows = [item.strip() for item in str(value).replace(";", ",").split(",")]
    parsed = [item for item in rows if item]
    return parsed or list(DEFAULT_REQUIRED_PLUGINS)


def _step_text(step: dict[str, Any]) -> str:
    return "\n".join([str(step.get("stdout") or ""), str(step.get("stderr") or "")]).lower()


def _plugin_health_state(step: dict[str, Any], required_plugins: Iterable[str]) -> tuple[list[str], list[str], list[str]]:
    text = _step_text(step)
    missing: list[str] = []
    rejected: list[str] = []
    disabled: list[str] = []
    for plugin_name in required_plugins:
        token = str(plugin_name).strip()
        if not token:
            continue
        lowered = token.lower()
        line_hits = [line.strip() for line in text.splitlines() if lowered in line]
        if not line_hits:
            missing.append(token)
            continue
        if any("reject" in line or "incompatible" in line for line in line_hits):
            rejected.append(token)
        if any("inactive" in line or "disabled" in line for line in line_hits):
            disabled.append(token)
    return missing, rejected, disabled


def determine_smoke_status(steps: list[dict[str, Any]], *, required_plugins: Iterable[str]) -> tuple[str, str, dict[str, list[str]]]:
    step_map = {str(step.get("name")): step for step in steps}
    hard_fail = [name for name in ("smoke-test", "apply", "rollback-last") if int(step_map.get(name, {}).get("returncode", 1)) != 0]
    plugin_step = step_map.get("plugin-health")
    missing: list[str] = []
    rejected: list[str] = []
    disabled: list[str] = []
    reasons: list[str] = []
    if hard_fail:
        reasons.append(f"required Windows flow steps failed: {', '.join(hard_fail)}")
    if plugin_step is not None:
        if int(plugin_step.get("returncode", 0)) != 0:
            reasons.append("plugin-health failed")
        missing, rejected, disabled = _plugin_health_state(plugin_step, required_plugins)
        if missing:
            reasons.append(f"missing required plugins: {', '.join(missing)}")
        if rejected:
            reasons.append(f"rejected required plugins: {', '.join(rejected)}")
        if disabled:
            reasons.append(f"disabled required plugins: {', '.join(disabled)}")
    if hard_fail or missing or rejected:
        return "failed", "; ".join(reasons), {"missing": missing, "rejected": rejected, "disabled": disabled}
    if disabled or reasons:
        return "degraded", "; ".join(reasons), {"missing": missing, "rejected": rejected, "disabled": disabled}
    return "passed", "", {"missing": missing, "rejected": rejected, "disabled": disabled}


def _write_report(output_dir: Path, stem: str, payload: dict[str, Any]) -> dict[str, str]:
    lines = ["## steps", ""]
    for step in payload["steps"]:
        lines.append(f"- `{step['name']}` => rc={step['returncode']}")
    return write_telemetry_report(output_dir, stem, payload, lines)


def run_windows_smoke(base_dir: Path, output_dir: Path | None = None, *, required_plugins: list[str] | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    required_plugins = list(required_plugins or parse_required_plugins(os.environ.get(ESSENTIAL_PLUGIN_ENV)))
    if platform.system() != "Windows":
        payload = enrich_payload(
            {
                "name": "windows_smoke",
                "status": "skipped",
                "reason": "Windows-only smoke. This environment is not Windows.",
                "platform": platform.system(),
                "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
                "required_plugins": required_plugins,
                "missing_required_plugins": [],
                "rejected_required_plugins": [],
                "disabled_required_plugins": [],
                "smoke_status_reason": "not-windows",
                "steps": [],
            },
            root_dir=base_dir,
            artifact_kind="telemetry-report",
            artifact_scope="reports/telemetry/windows_smoke",
        )
        if output_dir is not None:
            payload["report_paths"] = _write_report(output_dir, "windows_smoke", payload)
        return payload

    with tempfile.TemporaryDirectory(prefix="capatch_windows_smoke_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        workspace_root = tmp_root / "workspace with spaces" / "área"
        workspace_root.mkdir(parents=True, exist_ok=True)
        target = workspace_root / "service_util.py"
        target.write_text("def compute() -> int:\n    return 41\n", encoding="utf-8", newline="")
        ops_file = tmp_root / "ops smoke.json"
        ops_file.write_text(
            json.dumps([
                {
                    "type": "EnsureReplaceExactOnce",
                    "label": "meaning-42",
                    "file": "service_util.py",
                    "old_text": "    return 41\n",
                    "new_text": "    return 42\n",
                }
            ], indent=2, ensure_ascii=False),
            encoding="utf-8",
            newline="",
        )
        steps = []
        for step in build_windows_steps(base_dir, workspace_root, ops_file):
            completed = subprocess.run(step["argv"], capture_output=True, text=True, timeout=180, check=False)
            steps.append({
                "name": step["name"],
                "argv": step["argv"],
                "returncode": completed.returncode,
                "stdout": (completed.stdout or "")[:4000],
                "stderr": (completed.stderr or "")[:4000],
            })
    status, reason, detail = determine_smoke_status(steps, required_plugins=required_plugins)
    payload = enrich_payload(
        {
            "name": "windows_smoke",
            "status": status,
            "reason": reason,
            "platform": platform.system(),
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "required_plugins": required_plugins,
            "missing_required_plugins": detail["missing"],
            "rejected_required_plugins": detail["rejected"],
            "disabled_required_plugins": detail["disabled"],
            "smoke_status_reason": reason or status,
            "steps": steps,
        },
        root_dir=base_dir,
        artifact_kind="telemetry-report",
        artifact_scope="reports/telemetry/windows_smoke",
    )
    if output_dir is not None:
        payload["report_paths"] = _write_report(output_dir, "windows_smoke", payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    payload = run_windows_smoke(ROOT, ROOT / "reports" / "telemetry")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] in {"passed", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
