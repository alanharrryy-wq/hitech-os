#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from capatch_diagnostics.phase_runner import normalize_artifact
from capatch_policy.verification_requirements import compute_verification_policy
from capatch_verify.registry import run_required_verifiers


def test_artifact_contract_accepts_fix_link_fields() -> None:
    artifact = normalize_artifact(
        'fixture.plugin',
        {'proposal_id': 'autofix.fixture', 'category': 'diagnostics', 'summary': 'linked', 'unexpected_plugin_field': {'kept': True}},
        1,
    )
    assert artifact is not None
    payload = artifact.to_dict()
    assert payload['proposal_id'] == 'autofix.fixture'
    assert payload['metadata']['plugin_payload_extra']['unexpected_plugin_field'] == {'kept': True}


def test_css_policy_requires_css_sanity_for_module_css() -> None:
    policy = compute_verification_policy({'risk_level': 'medium'}, ['products/tablet/app/components/pos/pos.module.css'])
    assert 'css-sanity' in policy['required_verifiers']
    assert policy['verification_floor'] == 'syntax'
    assert policy['surface_flags']['touches_css'] is True


def test_css_sanity_verifier_passes_balanced_css(tmp_path) -> None:
    css_path = tmp_path / 'pos.module.css'
    css_path.write_text('.button { color: red; }\n/* CAPATCH START */\n.card { padding: 1rem; }\n/* CAPATCH END */\n', encoding='utf-8')
    rows = run_required_verifiers([css_path.name], ['css-sanity'], {'root_dir': str(tmp_path)})
    assert rows
    assert all(row['ok'] for row in rows)


def test_css_sanity_verifier_fails_broken_css(tmp_path) -> None:
    css_path = tmp_path / 'bad.module.css'
    css_path.write_text('.button { color: red; \n/* CAPATCH START */\n', encoding='utf-8')
    rows = run_required_verifiers([css_path.name], ['css-sanity'], {'root_dir': str(tmp_path)})
    assert rows
    assert not rows[0]['ok']
