
"""Generate example JSON outputs from the Python-first corpora."""

from __future__ import annotations

import json
from pathlib import Path

from checks.annotation_contract_checks import assert_annotation_record
from checks.path_exclusion_checks import assert_safe_ignore
from core.case_loader import load_cases
from core.index_compat import canonical_index_name


def build_annotation_record(case: dict[str, object], ordinal: int) -> dict[str, object]:
    upstream = dict(case['upstream_state'])
    expectation = dict(case['advisory_expectation'])
    legacy_name = str(upstream['legacy_index_reference'])
    return {
        'annotation_id': f"{case['case_id']}-rec-{ordinal:03d}",
        'target_type': 'module',
        'target_id': upstream['module_name'],
        'summary': expectation['summary_seed'],
        'rationale': ' '.join(str(item) for item in case['notes'][:4]),
        'confidence': 0.44 if case['family'] in {'ambiguity_cases', 'forbidden_override_cases'} else 0.72,
        'status': expectation['status'],
        'advisory_only': True,
        'evidence_sources': [
            'module_registry.json',
            'validation_report.json',
            'switch_decision_trace.json',
            canonical_index_name(legacy_name),
        ],
        'ignored_paths': [path for path in case['path_examples'] if path.startswith('reports_real/')],
        'forbidden_actions': list(case['forbidden_actions']),
    }


def generate_outputs(output_dir: Path, limit: int = 18) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = load_cases()[:limit]
    annotations = []
    index_rows = []
    ignored_count = 0
    for ordinal, case in enumerate(cases, start=1):
        record = build_annotation_record(case, ordinal)
        assert_annotation_record(record)
        for ignored in record['ignored_paths']:
            assert_safe_ignore(str(ignored))
            ignored_count += 1
        annotations.append(record)
        index_rows.append({
            'target_id': record['target_id'],
            'annotation_id': record['annotation_id'],
            'artifact': 'annotations.json',
            'canonical_index_name': 'registry_index.json',
            'advisory_only': True,
        })
    summary = {
        'annotation_count': len(annotations),
        'ambiguity_cases': sum(1 for case in cases if case['family'] == 'ambiguity_cases'),
        'forbidden_override_cases': sum(1 for case in cases if case['family'] == 'forbidden_override_cases'),
        'safe_ignore_hits': ignored_count,
        'advisory_only': True,
        'status': 'verification_example',
    }
    (output_dir / 'annotations.json').write_text(json.dumps(annotations, indent=2), encoding='utf-8')
    (output_dir / 'annotation_index.json').write_text(json.dumps(index_rows, indent=2), encoding='utf-8')
    (output_dir / 'annotation_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    return summary
