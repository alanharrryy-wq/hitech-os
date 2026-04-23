from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

if __package__ in {None, ""}:
    bundle_root = Path(__file__).resolve().parent
    if str(bundle_root) not in sys.path:
        sys.path.insert(0, str(bundle_root))

import payload_manifest
from tools.generate_example_outputs import generate_example_outputs

DEFAULT_INSTALL_REL = "bundles/scanner_bundle"
STATE_REL = ".ark_install/scanner_bundle"
LAST_APPLY_REL = ".ark_install/scanner_bundle/last_apply.json"
LOG_DIR_DEFAULT = Path(r"F:\descargasf")


@dataclass
class InstallPlan:
    root: str
    install_root: str
    state_root: str
    backup_root: str
    last_apply: str
    source_root: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Homologated scanner bundle installer")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--apply", action="store_true")
    modes.add_argument("--verify", action="store_true")
    modes.add_argument("--rollback", action="store_true")
    parser.add_argument("--root", required=True)
    parser.add_argument("--log-dir", default=str(LOG_DIR_DEFAULT))
    parser.add_argument("--install-rel", default=DEFAULT_INSTALL_REL)
    return parser


def now_stamp() -> str:
    return datetime.now().strftime("%y%m%d_%H%M")


def resolve_paths(args: argparse.Namespace) -> InstallPlan:
    root = Path(args.root).resolve()
    install_root = root / args.install_rel
    state_root = root / STATE_REL
    backup_root = state_root / "backups" / now_stamp()
    last_apply = root / LAST_APPLY_REL
    source_root = Path(__file__).resolve().parent
    return InstallPlan(
        root=str(root),
        install_root=str(install_root),
        state_root=str(state_root),
        backup_root=str(backup_root),
        last_apply=str(last_apply),
        source_root=str(source_root),
    )


def log_path(log_dir: Path) -> Path:
    return log_dir / f"Ar-k_scanner_int_{now_stamp()}.log"


def write_log(log_file: Path, lines: list[str]) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_surface(root: Path) -> list[str]:
    return payload_manifest.install_surface(root)


def materialize_install_surface(source_root: Path, install_root: Path, rel_paths: list[str]) -> None:
    if install_root.exists():
        shutil.rmtree(install_root)
    for rel in rel_paths:
        src = source_root / rel
        dst = install_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def collect_installed_surface(install_root: Path) -> list[str]:
    if not install_root.exists():
        return []
    return payload_manifest.install_surface(install_root)


def run_dry(plan: InstallPlan, log_file: Path) -> int:
    source_root = Path(plan.source_root)
    surface = install_surface(source_root)
    lines = ["mode=dry-run", json.dumps(asdict(plan), indent=2, sort_keys=True)]
    lines.append(f"verification_surface_files={len(surface)}")
    write_log(log_file, lines)
    print(f"dry_run_install_root={plan.install_root}")
    return 0


def run_apply(plan: InstallPlan, log_file: Path) -> int:
    install_root = Path(plan.install_root)
    state_root = Path(plan.state_root)
    backup_root = Path(plan.backup_root)
    source_root = Path(plan.source_root)
    surface = install_surface(source_root)
    state_root.mkdir(parents=True, exist_ok=True)
    backup_used = False
    if install_root.exists():
        backup_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(install_root, backup_root / "install_root")
        backup_used = True
    install_root.parent.mkdir(parents=True, exist_ok=True)
    materialize_install_surface(source_root, install_root, surface)
    state = {
        "install_root": str(install_root),
        "state_root": str(state_root),
        "backup_root": str(backup_root),
        "backup_used": backup_used,
        "installed_files": surface,
        "installed_file_count": len(surface),
    }
    Path(plan.last_apply).parent.mkdir(parents=True, exist_ok=True)
    Path(plan.last_apply).write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    write_log(log_file, ["mode=apply", json.dumps(state, indent=2, sort_keys=True)])
    print(f"applied_install_root={install_root}")
    return 0


def run_verify(plan: InstallPlan, log_file: Path) -> int:
    source_root = Path(plan.source_root)
    install_root = Path(plan.install_root)
    state_root = Path(plan.state_root)
    expected = install_surface(source_root)
    installed = collect_installed_surface(install_root)
    expected_set = set(expected)
    installed_set = set(installed)
    missing = sorted(expected_set - installed_set)
    unexpected = sorted(installed_set - expected_set)
    output_root = state_root / "verification_outputs" / now_stamp()
    written = generate_example_outputs(output_root)
    summary = {
        "install_root": str(install_root),
        "state_root": str(state_root),
        "expected_file_count": len(expected),
        "installed_file_count": len(installed),
        "missing_files": missing,
        "unexpected_files": unexpected,
        "verification_output_root": str(output_root),
        "generated_examples": len(written),
        "required_json_names": sorted({p.name for p in written}),
    }
    write_log(log_file, ["mode=verify", json.dumps(summary, indent=2, sort_keys=True)])
    if missing or unexpected:
        print("verify=failed")
        return 1
    print(f"verify_generated={len(written)}")
    return 0


def run_rollback(plan: InstallPlan, log_file: Path) -> int:
    state_path = Path(plan.last_apply)
    if not state_path.exists():
        write_log(log_file, ["mode=rollback", "result=no_state"])
        print("rollback=no_state")
        return 1
    state = json.loads(state_path.read_text(encoding="utf-8"))
    install_root = Path(state["install_root"])
    backup_root = Path(state["backup_root"])
    if install_root.exists():
        shutil.rmtree(install_root)
    if state.get("backup_used") and (backup_root / "install_root").exists():
        install_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(backup_root / "install_root", install_root)
    state_path.unlink()
    write_log(log_file, ["mode=rollback", json.dumps(state, indent=2, sort_keys=True)])
    print(f"rollback_restored={install_root}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    plan = resolve_paths(args)
    log_file = log_path(Path(args.log_dir))
    if args.dry_run:
        return run_dry(plan, log_file)
    if args.apply:
        return run_apply(plan, log_file)
    if args.verify:
        return run_verify(plan, log_file)
    return run_rollback(plan, log_file)


if __name__ == "__main__":
    raise SystemExit(main())
