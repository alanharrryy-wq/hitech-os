#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_contracts import build_operation_spec
from capatch_engine import preflight

from tooling.run_qa_benchmark_suite import run_suite
from tooling.run_rollback_drill import run_rollback_drill
from tooling.run_windows_smoke import run_windows_smoke


def _write_report(output_dir: Path, stem: str, payload: dict[str, Any]) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8", newline="")
    lines = [
        f"# {payload['name']}",
        "",
        f"- status: {payload['status']}",
        f"- reason: {payload.get('reason', '')}",
        "",
        "## checks",
        "",
    ]
    for row in payload["checks"]:
        lines.append(f"- `{row['name']}` => status={row['status']}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
    return {"json": str(json_path), "md": str(md_path)}


class _Ctx:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.backup_dir = root_dir / "_chatgpt_patch_backups"
        self.checkpoint_dir = self.backup_dir / "hardening_preflight"
        self.dry_run = False
        self.auto_support = True
        self.invocation_mode = "patch-run"
        self.run_id = None


def _preflight_conflict_check() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="capatch_hardening_conflict_") as tmp_dir:
        root = Path(tmp_dir)
        (root / "pkg").mkdir(parents=True, exist_ok=True)
        (root / "pkg" / "service.py").write_text(
            "def compute() -> int:\n    return 41\n    return 41\n",
            encoding="utf-8",
            newline="",
        )
        operations = [
            build_operation_spec(
                {
                    "type": "EnsureReplaceExactOnce",
                    "label": "first",
                    "file": "pkg/service.py",
                    "old_text": "    return 41\n",
                    "new_text": "    return 42\n",
                }
            ),
            build_operation_spec(
                {
                    "type": "EnsureReplaceExactOnce",
                    "label": "second",
                    "file": "pkg/service.py",
                    "old_text": "    return 41\n",
                    "new_text": "    return 43\n",
                }
            ),
        ]
        report = preflight(_Ctx(root), operations)
        reasons = [row.get("reason") for row in report.conflicts]
        return {
            "name": "preflight_conflict_guard",
            "status": "passed" if "duplicate_exact_text_match" in reasons else "failed",
            "reasons": reasons,
        }


def run_hardening_suite(base_dir: Path, output_dir: Path | None = None, *, quick: bool = False) -> dict[str, Any]:
    started = time.perf_counter()
    benchmark = run_suite(base_dir, output_dir=None, quick=quick)
    rollback = run_rollback_drill(base_dir, output_dir=None)
    windows = run_windows_smoke(base_dir, output_dir=None)
    preflight_check = _preflight_conflict_check()
    checks = [
        {"name": "qa_benchmark_suite", "status": "passed" if benchmark["metrics"]["fix_success_rate"] >= 0.5 else "failed"},
        {"name": "rollback_drill", "status": rollback["status"]},
        {"name": "windows_smoke", "status": windows["status"]},
        preflight_check,
    ]
    status = "passed"
    reason = ""
    if any(row["status"] == "failed" for row in checks):
        status = "failed"
        reason = "One or more hardening checks failed."
    elif any(row["status"] == "degraded" for row in checks):
        status = "degraded"
        reason = "At least one hardening check is degraded."
    payload = {
        "name": "hardening_suite",
        "status": status,
        "reason": reason,
        "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
        "checks": checks,
        "benchmark_metrics": benchmark["metrics"],
        "rollback_summary": {
            "status": rollback["status"],
            "conflict_preview_detected": rollback.get("conflict_preview_detected"),
            "multi_run_restore_ok": rollback.get("multi_run_restore_ok"),
        },
        "windows_summary": {
            "status": windows["status"],
            "reason": windows.get("reason", ""),
        },
    }
    if output_dir is not None:
        payload["report_paths"] = _write_report(output_dir, "hardening_suite", payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or [])
    payload = run_hardening_suite(ROOT, ROOT / "reports" / "telemetry", quick="--quick" in argv)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] in {"passed", "degraded"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
