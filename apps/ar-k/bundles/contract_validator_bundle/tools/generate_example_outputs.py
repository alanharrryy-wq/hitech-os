from __future__ import annotations

import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import json

from ark_contract_validator_bundle.fixtures.case_index import load_all_cases
from ark_contract_validator_bundle.runtime.canon import FINAL_STATUS_WORDING
from ark_contract_validator_bundle.runtime.evaluator import evaluate_cases


def _select_verify_cases(limit: int = 16) -> list[dict]:
    cases = load_all_cases()
    evaluations = evaluate_cases(cases)
    ready_ids = [evaluation['case_id'] for evaluation in evaluations if evaluation['summary']['overall_status'] == 'READY']
    selected_ids = set(ready_ids[:limit])
    return [case for case in cases if case['case_id'] in selected_ids]


def generate(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = _select_verify_cases()
    evaluations = evaluate_cases(cases)
    all_findings = [finding for evaluation in evaluations for finding in evaluation['findings']]
    counts = {'info': 0, 'warning': 0, 'error': 0, 'critical': 0}
    for finding in all_findings:
        counts[finding['severity']] += 1
    overall = 'BLOCKED' if counts['critical'] or counts['error'] else ('WARNING' if counts['warning'] else 'READY')
    validation_report = {
        'summary': {
            'status': overall,
            'counts_by_severity': counts,
            'case_count': len(evaluations),
            'bundle_status_wording': FINAL_STATUS_WORDING,
            'mode': 'verification_example_outputs',
        },
        'violations': all_findings,
    }
    gate_decisions = {
        'overall_status': overall,
        'decisions': [gate for evaluation in evaluations for gate in evaluation['gates']],
    }
    validator_summary = {
        'status': FINAL_STATUS_WORDING,
        'runtime_claim': 'handoff_package_only',
        'generated_during': 'verify',
        'case_ids': [evaluation['case_id'] for evaluation in evaluations],
        'overall_status': overall,
    }
    (output_dir / 'validation_report.json').write_text(json.dumps(validation_report, indent=2, sort_keys=True), encoding='utf-8')
    (output_dir / 'gate_decisions.json').write_text(json.dumps(gate_decisions, indent=2, sort_keys=True), encoding='utf-8')
    (output_dir / 'validator_summary.json').write_text(json.dumps(validator_summary, indent=2, sort_keys=True), encoding='utf-8')
    return {
        'validation_report': str(output_dir / 'validation_report.json'),
        'gate_decisions': str(output_dir / 'gate_decisions.json'),
        'validator_summary': str(output_dir / 'validator_summary.json'),
        'overall_status': overall,
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    result = generate(Path(args.output_dir))
    print(json.dumps(result, indent=2, sort_keys=True))
