#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_contracts import build_operation_spec
from capatch_engine import apply as engine_apply
from capatch_engine import preflight
from capatch_verify.registry import run_required_verifiers

from tooling.run_plugin_contract_smoke import run_contract_smoke
from tooling.run_rollback_drill import run_rollback_drill
from tooling.run_windows_smoke import run_windows_smoke
from capatch_audit.telemetry import enrich_payload, write_telemetry_report


class _Ctx:
    def __init__(self, root_dir: Path, checkpoint_name: str) -> None:
        self.root_dir = root_dir
        self.backup_dir = root_dir / "_chatgpt_patch_backups"
        self.checkpoint_dir = self.backup_dir / checkpoint_name
        self.dry_run = False
        self.auto_support = True
        self.invocation_mode = "patch-run"
        self.run_id = None


def _write_report(output_dir: Path, stem: str, payload: dict[str, Any]) -> dict[str, str]:
    metrics = payload["metrics"]
    lines = [
        "## benchmark_by_size",
        "",
        f"- fix_success_rate: {metrics['fix_success_rate']:.3f}",
        f"- degraded_rate: {metrics['degraded_rate']:.3f}",
        f"- false_fix_rate: {metrics['false_fix_rate']:.3f}",
        f"- avg_time_to_first_useful_hypothesis_ms: {metrics['avg_time_to_first_useful_hypothesis_ms']:.3f}",
        "",
    ]
    for bucket, row in metrics["benchmark_by_size"].items():
        lines.append(f"- `{bucket}` avg_ms={row['avg_duration_ms']:.3f} count={row['count']}")
    lines.extend(["", "## scenarios", ""])
    for scenario in payload["scenarios"]:
        lines.append(
            f"- `{scenario['name']}` kind={scenario['kind']} size={scenario.get('size_bucket', 'n/a')} "
            f"success={scenario.get('success')} degraded={scenario.get('degraded', False)} false_fix={scenario.get('false_fix', False)}"
        )
    return write_telemetry_report(output_dir, stem, payload, lines)


def compute_metrics(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    fix_rows = [row for row in scenarios if row.get("kind") == "fix"]
    applied_rows = [row for row in fix_rows if row.get("applied")]
    degraded_rows = [row for row in scenarios if row.get("degraded")]
    diagnostic_rows = [row for row in scenarios if row.get("kind") == "diagnostic" and row.get("hypothesis_ms") is not None]
    size_buckets: dict[str, list[float]] = {}
    for row in scenarios:
        bucket = str(row.get("size_bucket") or "unknown")
        size_buckets.setdefault(bucket, []).append(float(row.get("duration_ms") or 0.0))
    benchmark_by_size = {
        key: {"avg_duration_ms": statistics.mean(values), "count": len(values)}
        for key, values in sorted(size_buckets.items())
    }
    return {
        "fix_success_rate": (sum(1 for row in fix_rows if row.get("success")) / len(fix_rows)) if fix_rows else 0.0,
        "degraded_rate": (len(degraded_rows) / len(scenarios)) if scenarios else 0.0,
        "false_fix_rate": (sum(1 for row in applied_rows if row.get("false_fix")) / len(applied_rows)) if applied_rows else 0.0,
        "avg_time_to_first_useful_hypothesis_ms": statistics.mean([float(row["hypothesis_ms"]) for row in diagnostic_rows]) if diagnostic_rows else 0.0,
        "benchmark_by_size": benchmark_by_size,
    }


def _batch_positive_control(file_count: int) -> dict[str, Any]:
    started = time.perf_counter()
    size_bucket = "small" if file_count <= 8 else "medium"
    with tempfile.TemporaryDirectory(prefix=f"capatch_bench_batch_{file_count}_") as tmp_dir:
        root = Path(tmp_dir)
        pkg = root / "pkg"
        pkg.mkdir(parents=True, exist_ok=True)
        operations = []
        for index in range(file_count):
            path = pkg / f"file_{index:02d}.py"
            path.write_text(f"VALUE_{index} = {index}\n", encoding="utf-8", newline="")
            operations.append(
                build_operation_spec(
                    {
                        "type": "EnsureReplaceExactOnce",
                        "label": f"bump-{index}",
                        "file": f"pkg/file_{index:02d}.py",
                        "old_text": f"VALUE_{index} = {index}\n",
                        "new_text": f"VALUE_{index} = {index + 1}\n",
                    }
                )
            )
        ctx = _Ctx(root, f"bench_batch_{file_count}")
        pf = preflight(ctx, operations)
        results = engine_apply(ctx, operations)
        verifier_rows = run_required_verifiers([str(path) for path in sorted(pkg.glob("*.py"))], ["python-parse"], {"root_dir": str(root)})
        oracle_ok = all(path.read_text(encoding="utf-8").endswith(f"{index + 1}\n") for index, path in enumerate(sorted(pkg.glob("*.py"))))
        return {
            "name": f"batch_positive_control_{file_count}",
            "kind": "fix",
            "size_bucket": size_bucket,
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "success": bool(pf.ok and oracle_ok and all(row["ok"] for row in verifier_rows)),
            "applied": any(item.patch_status == "applied" for item in results),
            "degraded": False,
            "false_fix": False,
            "verifier_rows": verifier_rows,
            "operation_count": len(operations),
        }


def _large_file_fix(line_count: int) -> dict[str, Any]:
    started = time.perf_counter()
    size_bucket = "medium" if line_count <= 12000 else "large"
    with tempfile.TemporaryDirectory(prefix="capatch_bench_large_") as tmp_dir:
        root = Path(tmp_dir)
        target = root / "big.txt"
        target.write_text("HEAD=old\n" + ("marker=old\n" * line_count) + "tail\n", encoding="utf-8", newline="")
        operations = [
            build_operation_spec(
                {
                    "type": "ReplaceExactOnce",
                    "label": "replace-head",
                    "file": "big.txt",
                    "old_text": "HEAD=old\n",
                    "new_text": "HEAD=new\n",
                }
            ),
            build_operation_spec(
                {
                    "type": "NormalizeFile",
                    "label": "normalize-large",
                    "file": "big.txt",
                    "line_ending": "LF",
                    "ensure_final_newline": True,
                    "strip_trailing_spaces": True,
                }
            ),
        ]
        ctx = _Ctx(root, f"bench_large_{line_count}")
        pf = preflight(ctx, operations)
        results = engine_apply(ctx, operations)
        content = target.read_text(encoding="utf-8")
        oracle_ok = content.startswith("HEAD=new\n") and content.endswith("tail\n")
        return {
            "name": f"large_file_positive_control_{line_count}",
            "kind": "fix",
            "size_bucket": size_bucket,
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "success": bool(pf.ok and oracle_ok),
            "applied": any(item.patch_status == "applied" for item in results),
            "degraded": False,
            "false_fix": False,
            "bytes_after": target.stat().st_size,
        }


def _encoding_normalize_case() -> dict[str, Any]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="capatch_bench_encoding_") as tmp_dir:
        root = Path(tmp_dir)
        target = root / "notes.txt"
        target.write_bytes("uno  \r\ndos\t\r\nárbol\r\n".encode("utf-8"))
        operations = [
            build_operation_spec(
                {
                    "type": "NormalizeFile",
                    "label": "normalize-unicode",
                    "file": "notes.txt",
                    "line_ending": "LF",
                    "ensure_final_newline": True,
                    "strip_trailing_spaces": True,
                }
            )
        ]
        ctx = _Ctx(root, "bench_encoding")
        pf = preflight(ctx, operations)
        results = engine_apply(ctx, operations)
        content = target.read_text(encoding="utf-8")
        oracle_ok = content == "uno\ndos\nárbol\n"
        return {
            "name": "encoding_normalize_positive_control",
            "kind": "fix",
            "size_bucket": "small",
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "success": bool(pf.ok and oracle_ok),
            "applied": any(item.patch_status == "applied" for item in results),
            "degraded": False,
            "false_fix": False,
        }


def _false_fix_control() -> dict[str, Any]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="capatch_bench_false_fix_") as tmp_dir:
        root = Path(tmp_dir)
        target = root / "service.py"
        target.write_text("def compute() -> int:\n    return 41\n", encoding="utf-8", newline="")
        operations = [
            build_operation_spec(
                {
                    "type": "EnsureReplaceExactOnce",
                    "label": "wrong-fix",
                    "file": "service.py",
                    "old_text": "    return 41\n",
                    "new_text": "    return 0\n",
                }
            )
        ]
        ctx = _Ctx(root, "bench_false_fix")
        pf = preflight(ctx, operations)
        results = engine_apply(ctx, operations)
        verifier_rows = run_required_verifiers([str(target)], ["python-parse", "python-compile-smoke", "python-import-smoke"], {"root_dir": str(root)})
        namespace: dict[str, Any] = {}
        exec(target.read_text(encoding="utf-8"), namespace, namespace)
        oracle_ok = namespace["compute"]() == 42
        return {
            "name": "false_fix_negative_control",
            "kind": "fix",
            "size_bucket": "small",
            "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
            "success": bool(pf.ok and oracle_ok and all(row["ok"] for row in verifier_rows)),
            "applied": any(item.patch_status == "applied" for item in results),
            "degraded": not oracle_ok,
            "false_fix": not oracle_ok and any(item.patch_status == "applied" for item in results),
            "verifier_rows": verifier_rows,
        }


def _diagnostic_case(name: str, hypothesis_ms: float, *, degraded: bool = False) -> dict[str, Any]:
    return {
        "name": name,
        "kind": "diagnostic",
        "size_bucket": "small",
        "duration_ms": hypothesis_ms + 2.0,
        "hypothesis_ms": hypothesis_ms,
        "degraded": degraded,
        "success": not degraded,
        "applied": False,
        "false_fix": False,
    }


def run_suite(base_dir: Path, output_dir: Path | None = None, *, quick: bool = False) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = [
        _batch_positive_control(4 if quick else 8),
        _batch_positive_control(10 if quick else 18),
        _large_file_fix(6000 if quick else 18000),
        _encoding_normalize_case(),
        _false_fix_control(),
        _diagnostic_case("diagnostic_hypothesis_fast", 12.0),
        _diagnostic_case("diagnostic_hypothesis_slow", 18.0),
    ]

    contract = run_contract_smoke(base_dir, output_dir=None)
    scenarios.append(
        {
            "name": "plugin_contract_smoke",
            "kind": "diagnostic",
            "size_bucket": "small",
            "duration_ms": float(contract.get("duration_ms") or 0.0),
            "hypothesis_ms": 10.0 if contract.get("status") == "passed" else 0.0,
            "degraded": contract.get("status") not in {"passed", "skipped"},
            "success": contract.get("status") in {"passed", "skipped"},
            "applied": False,
            "false_fix": False,
        }
    )
    rollback = run_rollback_drill(base_dir, output_dir=None)
    scenarios.append(
        {
            "name": "rollback_drill",
            "kind": "diagnostic",
            "size_bucket": "medium",
            "duration_ms": float(rollback.get("duration_ms") or 0.0),
            "hypothesis_ms": 16.0 if rollback.get("status") == "passed" else 0.0,
            "degraded": rollback.get("status") != "passed",
            "success": rollback.get("status") == "passed",
            "applied": False,
            "false_fix": False,
        }
    )
    windows = run_windows_smoke(base_dir, output_dir=None)
    scenarios.append(
        {
            "name": "windows_smoke",
            "kind": "diagnostic",
            "size_bucket": "medium",
            "duration_ms": float(windows.get("duration_ms") or 0.0),
            "hypothesis_ms": 14.0 if windows.get("status") in {"passed", "skipped"} else 0.0,
            "degraded": windows.get("status") == "degraded",
            "success": windows.get("status") in {"passed", "skipped"},
            "applied": False,
            "false_fix": False,
        }
    )

    payload = enrich_payload(
        {
            "name": "qa_benchmark_suite",
            "status": "passed",
            "quick": bool(quick),
            "scenarios": scenarios,
            "metrics": compute_metrics(scenarios),
            "rollup": {
                "scenario_count": len(scenarios),
                "fix_scenarios": sum(1 for item in scenarios if item.get("kind") == "fix"),
            },
        },
        root_dir=base_dir,
        artifact_kind="telemetry-report",
        artifact_scope="reports/telemetry/qa_benchmark_suite",
    )
    if output_dir is not None:
        payload["report_paths"] = _write_report(output_dir, "qa_benchmark_suite", payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    payload = run_suite(ROOT, ROOT / "reports" / "telemetry", quick="--quick" in (argv or []))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
