from __future__ import annotations

import argparse
import json
from pathlib import Path

from pya.kernel.context import RuntimeContext
from pya.kernel.engine_loader import discover_and_load_engines
from pya.kernel.pipeline import PipelineCoordinator
from pya.system.execution import CANONICAL_STAGE_ORDER
from pya.system.root_manifest import get_root_manifest

PLACEHOLDER_TOKENS = {"<real_frontend_target>", "<target>", "<path>"}


def _section_exists(readme_path: Path, heading: str) -> bool:
    if not readme_path.exists():
        return False
    return heading in readme_path.read_text(encoding="utf-8")


def _validate_cli_path_argument(name: str, value: Path) -> Path:
    raw = str(value).strip()
    lowered = raw.lower()
    if any(token in lowered for token in PLACEHOLDER_TOKENS) or ("<" in raw and ">" in raw):
        raise ValueError(
            f"Invalid --{name} value: placeholder token detected. Replace it with a real absolute path. Got: {raw}"
        )
    return Path(raw).expanduser().resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ar-k governed platform CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Validate constitution, manifests, and ownership")
    doctor.add_argument("--root", required=True, help="Absolute project root")

    run = subparsers.add_parser("run", help="Run governed pipeline")
    run.add_argument("--root", required=True, help="Absolute project root")
    run.add_argument("--target", required=True, help="Target app to scan")
    run.add_argument("--out", required=True, help="Output directory")
    run.add_argument(
        "--switch-override",
        action="append",
        default=[],
        help="Override switch or target id with KEY=bool",
    )
    return parser


def _parse_overrides(items: list[str]) -> dict[str, bool]:
    overrides: dict[str, bool] = {}
    for item in items:
        key, raw_value = item.split("=", 1)
        value = raw_value.strip().lower()
        if value not in {"true", "false"}:
            overrides[key.strip()] = raw_value
        else:
            overrides[key.strip()] = value == "true"
    return overrides


def cmd_doctor(root: Path) -> int:
    root = _validate_cli_path_argument("root", root)
    manifest = get_root_manifest()
    engines = discover_and_load_engines(root, manifest)
    ownership = manifest["ownership_policy"]
    writer_counts = {}
    for registry_name, policy in ownership.items():
        writer_counts[registry_name] = policy["writer"]
    summary = {
        "root": str(root),
        "system_id": manifest["system_id"],
        "kernel_version": manifest["version"],
        "stage_order": manifest["canonical_stage_order"],
        "engine_count": len(engines),
        "engines": [engine.engine_id for engine in engines],
        "readme_parallel_section": _section_exists(root / "README.md", "## Developing the 5 engines in parallel"),
        "ownership_writers": writer_counts,
        "doctor_status": "ok",
    }
    if summary["stage_order"] != CANONICAL_STAGE_ORDER or not summary["readme_parallel_section"]:
        summary["doctor_status"] = "fail"
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def cmd_run(root: Path, target: Path, out: Path, overrides: dict[str, bool]) -> int:
    root = _validate_cli_path_argument("root", root)
    target = _validate_cli_path_argument("target", target)
    out = _validate_cli_path_argument("out", out)
    context = RuntimeContext.build(root=root, target=target, out=out, switch_overrides=overrides)
    coordinator = PipelineCoordinator(context)
    report = coordinator.run()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "doctor":
        return cmd_doctor(Path(args.root))
    if args.command == "run":
        return cmd_run(Path(args.root), Path(args.target), Path(args.out), _parse_overrides(args.switch_override))
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
