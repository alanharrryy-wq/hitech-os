from __future__ import annotations

import argparse
import json
import sys
sys.dont_write_bytecode = True
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
BUNDLE_ROOT = THIS_DIR.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

from compat.query_index_alias import adapt_registry_index_for_legacy
from fixtures.catalog import load_all_cases
from policy.promotion_policy import build_canonical_outputs


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate example JSON outputs during verification only.')
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--limit', type=int, default=3)
    args = parser.parse_args()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for case in load_all_cases()[: max(1, args.limit)]:
        case_dir = out_dir / case['scenario_id']
        case_dir.mkdir(parents=True, exist_ok=True)
        outputs = build_canonical_outputs(case['observed_signals'], execution_id=case['scenario_id'])
        (case_dir / 'module_registry.json').write_text(json.dumps(outputs['module_registry'], indent=2, sort_keys=True), encoding='utf-8')
        (case_dir / 'boundary_registry.json').write_text(json.dumps(outputs['boundary_registry'], indent=2, sort_keys=True), encoding='utf-8')
        (case_dir / 'registry_index.json').write_text(json.dumps(outputs['registry_index'], indent=2, sort_keys=True), encoding='utf-8')
        (case_dir / 'query_index_legacy_view.json').write_text(json.dumps(adapt_registry_index_for_legacy(outputs['registry_index']), indent=2, sort_keys=True), encoding='utf-8')
        index.append({
            'scenario_id': case['scenario_id'],
            'path': str(case_dir),
            'module_count': len(outputs['module_registry']),
            'boundary_count': len(outputs['boundary_registry']),
            'index_count': len(outputs['registry_index']),
        })
    (out_dir / 'generated_examples_index.json').write_text(json.dumps(index, indent=2, sort_keys=True), encoding='utf-8')
    print(json.dumps({'output_dir': str(out_dir), 'generated_cases': len(index)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
