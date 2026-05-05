from __future__ import annotations

import sys
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parents[1]
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import argparse
import json

from ark_contract_validator_bundle.runtime.canon import (
    FINAL_STATUS_WORDING,
    INSTALL_REL_DEFAULT,
    REQUIRED_VALIDATOR_ARTIFACTS,
    STATE_FILE,
    STATE_ROOT_REL,
    TOP_LEVEL_DIR,
    bundle_root_role,
    canonical_bundle_mapping,
    is_canonical_bundle_root_name,
)

REQUIRED_PATHS = [
    'contract_validator_installer.py',
    'payload_manifest.py',
    'tools/validate_contract_validator_bundle.py',
    'tools/count_bundle_mix.py',
    'tools/generate_example_outputs.py',
    'runtime/evaluator.py',
    'runtime/gates.py',
    'fixtures/case_index.py',
    'tests/test_gate_semantics.py',
    'FINAL_REPORT.md',
]


def validate(bundle_root: Path) -> dict:
    missing = [rel for rel in REQUIRED_PATHS if not (bundle_root / rel).exists()]
    installer_text = (bundle_root / 'contract_validator_installer.py').read_text(encoding='utf-8')
    final_report = (bundle_root / 'FINAL_REPORT.md').read_text(encoding='utf-8')
    issues = []
    if not is_canonical_bundle_root_name(bundle_root.name):
        issues.append(f'top_level_dir_mismatch:{bundle_root.name}')
    if 'payload' in installer_text and '--payload' in installer_text:
        issues.append('installer_forbidden_payload_argument')
    for token in [INSTALL_REL_DEFAULT, STATE_ROOT_REL, STATE_FILE, FINAL_STATUS_WORDING]:
        if token not in installer_text and token not in final_report:
            issues.append(f'missing_token:{token}')
    for artifact in REQUIRED_VALIDATOR_ARTIFACTS:
        if artifact not in installer_text and artifact not in final_report:
            issues.append(f'missing_artifact_reference:{artifact}')
    if FINAL_STATUS_WORDING not in final_report:
        issues.append('final_report_missing_status')
    if TOP_LEVEL_DIR not in final_report:
        issues.append('archive_identity_not_documented')
    if 'contract_validator_bundle' not in final_report:
        issues.append('installed_subtree_not_documented')
    if 'reports_real/' not in final_report and 'reports_real' not in installer_text:
        issues.append('reports_real_exclusion_missing')
    return {
        'bundle_root': str(bundle_root),
        'bundle_root_name': bundle_root.name,
        'bundle_root_role': bundle_root_role(bundle_root),
        'canon_mapping': canonical_bundle_mapping(),
        'missing_paths': missing,
        'issues': issues,
        'status': 'ok' if not missing and not issues else 'blocked',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle-root', required=True)
    args = parser.parse_args()
    print(json.dumps(validate(Path(args.bundle_root)), indent=2, sort_keys=True))
