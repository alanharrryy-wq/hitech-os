from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from contracts.shared_canon import (
    BACKUP_REL,
    DEFAULT_INSTALL_REL,
    DEFAULT_LOG_DIR,
    LAST_APPLY_REL,
    LOG_BASENAME_PREFIX,
    STATE_REL,
    TOP_LEVEL_DIR,
)
from payload_manifest import PAYLOAD_ENTRIES
from tools.generate_example_outputs import generate
from tools.validate_switch_engine_bundle import validate_tree


@dataclass
class PlannedChange:
    relative_path: str
    source: str
    target: str
    action: str


@dataclass
class InstallPlan:
    root: str
    install_root: str
    state_root: str
    state_file: str
    backup_root: str
    log_file: str
    changes: list[PlannedChange]


BUNDLE_DIR = Path(__file__).resolve().parent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Homologated Switch Engine bundle installer', add_help=False)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--verify', action='store_true')
    mode.add_argument('--rollback', action='store_true')
    parser.add_argument('--root', required=True, help='Root path used to derive install and state locations')
    parser.add_argument('--log-dir', default=DEFAULT_LOG_DIR, help='Directory for the single installer log')
    parser.add_argument('--install-rel', default=str(DEFAULT_INSTALL_REL), help='Install path relative to --root')
    return parser


def resolve_root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def timestamp_slug() -> str:
    return datetime.now().strftime('%y%m%d_%H%M')


def configure_logging(log_dir: Path) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{LOG_BASENAME_PREFIX}{timestamp_slug()}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[logging.FileHandler(log_file, encoding='utf-8'), logging.StreamHandler(sys.stdout)],
        force=True,
    )
    return log_file


def build_plan(root: Path, install_rel: str, log_dir: Path) -> InstallPlan:
    install_root = (root / Path(install_rel)).resolve()
    state_root = (root / STATE_REL).resolve()
    state_file = (root / LAST_APPLY_REL).resolve()
    backup_root = (root / BACKUP_REL / datetime.now().strftime('%Y%m%d_%H%M%S')).resolve()
    changes: list[PlannedChange] = []
    for entry in PAYLOAD_ENTRIES:
        rel = entry['relative_path']
        if rel == 'FINAL_REPORT.md':
            # report is part of the bundle but not required in install target payload
            continue
        source = BUNDLE_DIR / rel
        target = install_root / rel
        if target.exists():
            action = 'skip' if source.read_bytes() == target.read_bytes() else 'replace'
        else:
            action = 'create'
        changes.append(PlannedChange(rel, str(source), str(target), action))
    return InstallPlan(
        root=str(root),
        install_root=str(install_root),
        state_root=str(state_root),
        state_file=str(state_file),
        backup_root=str(backup_root),
        log_file=str(log_dir / f"{LOG_BASENAME_PREFIX}{timestamp_slug()}.log"),
        changes=changes,
    )


def backup_target(target: Path, backup_root: Path, install_root: Path) -> Path:
    relative = target.relative_to(install_root)
    backup_path = backup_root / relative
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup_path)
    return backup_path


def save_state(state_file: Path, payload: dict[str, object]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')


def run_dry(plan: InstallPlan) -> int:
    logging.info('Planned %s changes into %s', len(plan.changes), plan.install_root)
    print(json.dumps({
        'root': plan.root,
        'install_root': plan.install_root,
        'state_root': plan.state_root,
        'state_file': plan.state_file,
        'backup_root': plan.backup_root,
        'changes': [change.__dict__ for change in plan.changes],
    }, indent=2, sort_keys=True))
    return 0


def run_apply(plan: InstallPlan) -> int:
    install_root = Path(plan.install_root)
    backup_root = Path(plan.backup_root)
    install_root.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    replaced: list[str] = []
    skipped: list[str] = []
    backed_up: list[str] = []
    for change in plan.changes:
        source = Path(change.source)
        target = Path(change.target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if change.action == 'skip':
            skipped.append(change.relative_path)
            continue
        if change.action == 'replace' and target.exists():
            backed_up.append(str(backup_target(target, backup_root, install_root)))
            replaced.append(change.relative_path)
        else:
            created.append(change.relative_path)
        shutil.copy2(source, target)
    state_payload = {
        'bundle_dir': str(BUNDLE_DIR),
        'root': plan.root,
        'install_root': plan.install_root,
        'state_root': plan.state_root,
        'state_file': plan.state_file,
        'backup_root': plan.backup_root,
        'created': created,
        'replaced': replaced,
        'skipped': skipped,
        'backups': backed_up,
    }
    save_state(Path(plan.state_file), state_payload)
    logging.info('Apply completed with %s created, %s replaced, %s skipped', len(created), len(replaced), len(skipped))
    print(json.dumps(state_payload, indent=2, sort_keys=True))
    return 0


def run_verify(plan: InstallPlan) -> int:
    tree_report = validate_tree(BUNDLE_DIR)
    state_root = Path(plan.state_root)
    example_dir = state_root / 'verify_outputs'
    manifest = generate(example_dir)
    verify_payload = {
        'tree_report': tree_report,
        'example_outputs': manifest,
        'install_root': plan.install_root,
        'state_root': plan.state_root,
        'required_install_root': str((Path(plan.root) / Path(plan.install_root).relative_to(Path(plan.root))).resolve()) if Path(plan.install_root).is_absolute() else plan.install_root,
    }
    logging.info('Verify completed and emitted example outputs to %s', example_dir)
    print(json.dumps(verify_payload, indent=2, sort_keys=True))
    return 0 if tree_report['ok'] else 1


def run_rollback(plan: InstallPlan) -> int:
    state_file = Path(plan.state_file)
    if not state_file.exists():
        logging.info('No rollback state found at %s', state_file)
        print(json.dumps({'rolled_back': False, 'reason': 'missing_state_file', 'state_file': str(state_file)}, indent=2, sort_keys=True))
        return 0
    state = json.loads(state_file.read_text(encoding='utf-8'))
    install_root = Path(state['install_root'])
    backup_root = Path(state['backup_root'])
    for rel in state.get('created', []):
        target = install_root / rel
        if target.exists():
            target.unlink()
    for rel in state.get('replaced', []):
        target = install_root / rel
        backup = backup_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if backup.exists():
            shutil.copy2(backup, target)
    logging.info('Rollback completed using %s', backup_root)
    print(json.dumps({'rolled_back': True, 'state_file': str(state_file), 'restored_backup_root': str(backup_root)}, indent=2, sort_keys=True))
    return 0


def main() -> int:
    args = build_parser().parse_args()
    root = resolve_root(args.root)
    log_file = configure_logging(Path(args.log_dir))
    plan = build_plan(root, args.install_rel, Path(args.log_dir))
    logging.info('Bundle root=%s top_level_dir=%s', BUNDLE_DIR, TOP_LEVEL_DIR)
    logging.info('Log file=%s', log_file)
    if args.dry_run:
        return run_dry(plan)
    if args.apply:
        return run_apply(plan)
    if args.verify:
        return run_verify(plan)
    if args.rollback:
        return run_rollback(plan)
    raise AssertionError('unreachable')


if __name__ == '__main__':
    raise SystemExit(main())
