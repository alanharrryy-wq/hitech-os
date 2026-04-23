from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

from ark_contract_validator_bundle.runtime.canon import (
    BACKUP_ROOT_REL,
    FINAL_STATUS_WORDING,
    INSTALL_REL_DEFAULT,
    REQUIRED_VALIDATOR_ARTIFACTS,
    STATE_FILE,
    STATE_ROOT_REL,
    TOP_LEVEL_DIR,
    canonical_bundle_mapping,
)
from ark_contract_validator_bundle.tools.generate_example_outputs import generate
from ark_contract_validator_bundle.tools.validate_contract_validator_bundle import validate


@dataclass
class Paths:
    root: Path
    install_root: Path
    state_root: Path
    state_file: Path
    backup_root: Path
    log_file: Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Self-contained installer for the governed contract validator handoff bundle.'
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply', action='store_true')
    mode.add_argument('--verify', action='store_true')
    mode.add_argument('--rollback', action='store_true')
    parser.add_argument('--root', required=True)
    parser.add_argument('--log-dir', default=r'F:\descargasf')
    parser.add_argument('--install-rel', default=INSTALL_REL_DEFAULT)
    return parser


def bundle_source_root() -> Path:
    return Path(__file__).resolve().parent


def build_paths(args: argparse.Namespace) -> Paths:
    root = Path(args.root)
    stamp = datetime.now().strftime('%y%m%d_%H%M')
    log_file = Path(args.log_dir) / f'Ar-k_contract_validator_int_{stamp}.log'
    state_root = root / STATE_ROOT_REL
    return Paths(
        root=root,
        install_root=root / args.install_rel,
        state_root=state_root,
        state_file=root / STATE_FILE,
        backup_root=root / BACKUP_ROOT_REL / stamp,
        log_file=log_file,
    )


def iter_payload_files() -> list[Path]:
    source = bundle_source_root()
    return sorted(
        path
        for path in source.rglob('*')
        if path.is_file() and '__pycache__' not in path.parts and not path.name.endswith(('.pyc', '.pyo'))
    )


def log(paths: Paths, message: str) -> None:
    paths.log_file.parent.mkdir(parents=True, exist_ok=True)
    with paths.log_file.open('a', encoding='utf-8') as handle:
        handle.write(message + '\n')


def dry_run(paths: Paths) -> dict:
    files = [str(path.relative_to(bundle_source_root())) for path in iter_payload_files()]
    result = {
        'mode': 'dry-run',
        'source_root': str(bundle_source_root()),
        'install_root': str(paths.install_root),
        'state_root': str(paths.state_root),
        'state_file': str(paths.state_file),
        'artifact_names': REQUIRED_VALIDATOR_ARTIFACTS,
        'file_count': len(files),
        'files': files,
        'canon_mapping': canonical_bundle_mapping(),
        'status': FINAL_STATUS_WORDING,
    }
    log(paths, json.dumps(result, sort_keys=True))
    return result


def apply(paths: Paths) -> dict:
    source = bundle_source_root()
    if paths.install_root.exists():
        paths.backup_root.mkdir(parents=True, exist_ok=True)
        backup_target = paths.backup_root / TOP_LEVEL_DIR
        if backup_target.exists():
            shutil.rmtree(backup_target)
        shutil.copytree(paths.install_root, backup_target)
    if paths.install_root.exists():
        shutil.rmtree(paths.install_root)
    paths.install_root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, paths.install_root)
    paths.state_root.mkdir(parents=True, exist_ok=True)
    state = {
        'installed_from': str(source),
        'install_root': str(paths.install_root),
        'backup_root': str(paths.backup_root / TOP_LEVEL_DIR),
        'state_root': str(paths.state_root),
        'canon_mapping': canonical_bundle_mapping(),
        'status': FINAL_STATUS_WORDING,
    }
    paths.state_file.write_text(json.dumps(state, indent=2, sort_keys=True), encoding='utf-8')
    log(paths, json.dumps({'mode': 'apply', **state}, sort_keys=True))
    return state


def verify(paths: Paths) -> dict:
    target = paths.install_root if paths.install_root.exists() else bundle_source_root()
    validation = validate(target)
    output_dir = target / 'example_runtime' / 'validator_outputs'
    generated = generate(output_dir)
    result = {
        'mode': 'verify',
        'bundle_root': str(target),
        'validation': validation,
        'generated_outputs': generated,
        'canon_mapping': canonical_bundle_mapping(),
        'status': FINAL_STATUS_WORDING,
        'runtime_claim': 'handoff_package_only',
    }
    log(paths, json.dumps(result, sort_keys=True))
    return result


def rollback(paths: Paths) -> dict:
    if not paths.state_file.exists():
        result = {'mode': 'rollback', 'status': 'no_state', 'canon_mapping': canonical_bundle_mapping()}
        log(paths, json.dumps(result, sort_keys=True))
        return result
    state = json.loads(paths.state_file.read_text(encoding='utf-8'))
    backup_root = Path(state.get('backup_root', ''))
    if backup_root.exists():
        if paths.install_root.exists():
            shutil.rmtree(paths.install_root)
        shutil.copytree(backup_root, paths.install_root)
        outcome = 'restored_backup'
    else:
        if paths.install_root.exists():
            shutil.rmtree(paths.install_root)
        outcome = 'removed_install_root'
    result = {
        'mode': 'rollback',
        'status': outcome,
        'install_root': str(paths.install_root),
        'canon_mapping': canonical_bundle_mapping(),
    }
    log(paths, json.dumps(result, sort_keys=True))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = build_paths(args)
    if args.dry_run:
        payload = dry_run(paths)
    elif args.apply:
        payload = apply(paths)
    elif args.verify:
        payload = verify(paths)
    else:
        payload = rollback(paths)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
