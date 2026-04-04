# UX Release Proof Workflow

This document defines the authoritative UX proof workflow for `pyside6_glass`.

## Ownership

- Sacred release-blocker contract (40): `forgeos/shared/pyside6_glass/SACRED_CAPABILITIES_CONTRACT.md`
- Premium capability contract (100): `forgeos/shared/pyside6_glass/contracts/premium_capabilities_100.md`
- Operational matrix (before-status + required evidence tags):
  - `forgeos/shared/pyside6_glass/contracts/premium_capability_matrix_v1.json`
- Golden sessions specification:
  - `forgeos/shared/pyside6_glass/golden_sessions/golden_sessions_v1.json`
- Semantic baseline (authoritative comparator source):
  - `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/semantic_baseline.json`
- Visual baseline manifest (secondary screenshot reference):
  - `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/visual_baseline_manifest.json`

## Local Commands

Full release gate:

```bash
python forgeos/shared/pyside6_glass/release_gate.py
```

Quick contract+compile gate:

```bash
python forgeos/shared/pyside6_glass/release_gate.py --skip-tests --skip-proof
```

Run UX proof only:

```bash
python -m forgeos.shared.pyside6_glass.ux_flight_recorder.runner --no-screenshots
```

## CI / Headless Command

```bash
python forgeos/shared/pyside6_glass/release_gate.py --ci
```

Nightly visual evidence pass (non-blocking, screenshots enabled):

```bash
python forgeos/shared/pyside6_glass/release_gate.py --ci --nightly-visual-proof
```

## Baseline Refresh Policy

Baselines are refreshed only by explicit operator action:

```bash
python -m forgeos.shared.pyside6_glass.ux_flight_recorder.runner --refresh-baseline --no-screenshots
```

Never refresh baselines as part of default release checks.
Nightly visual proof is non-blocking and does not refresh baseline files.

## Artifacts

Release proof artifacts are generated under:

- `forgeos/shared/pyside6_glass/artifacts/ux_release_proof/<timestamp>/`

Each run contains at minimum:

- `UX_RELEASE_PROOF.md`
- `golden_sessions_summary.json`
- `comparison_report.json`
- `semantic_run_payload.json`
- `capability_matrix_delta.json`
- `sessions/<session_id>/manifest.json`
- `sessions/<session_id>/events.json`
- `sessions/<session_id>/checkpoints/*.json`
- `sessions/<session_id>/screenshots/*.png` (if screenshots enabled)

Release gate evidence JSON is written to:

- `tools/_local/evidence/pyside6_glass_release_gate_<timestamp>.json`
