"""Generate example switch outputs during verification only."""

from __future__ import annotations

import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import argparse
import json

from switch_engine.models import SwitchEntry
from switch_engine.resolver import resolve_switch_entries
from switch_engine.tracing import build_summary


def sample_entries() -> list[SwitchEntry]:
    return [
        SwitchEntry('switch.alpha', 'module', 'module.alpha', True),
        SwitchEntry('switch.beta', 'module', 'module.beta', False),
        SwitchEntry('switch.gamma', 'route', 'route.gamma', True),
        SwitchEntry('switch.delta', 'boundary', 'boundary.delta', False),
    ]


def generate(output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = '2026-04-11T23:59:59Z'
    resolutions, trace, warnings, deterministic_hash = resolve_switch_entries(
        sample_entries(),
        {'switch.beta': True, 'route.gamma': False, 'switch.delta': 'bad-value'},
        timestamp,
    )
    summary = build_summary('verify_example', len(resolutions), len(warnings), deterministic_hash)
    files = {
        'switch_decision_registry.json': resolutions,
        'switch_decision_trace.json': trace,
        'switch_resolution_summary.json': summary,
    }
    for name, payload in files.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')
    return {name: str(output_dir / name) for name in files}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Generate example switch outputs')
    parser.add_argument('--output-dir', required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    manifest = generate(Path(args.output_dir).resolve())
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
