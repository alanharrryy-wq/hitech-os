1. STATUS
READY FOR HANDOFF

2. ROOT CAUSE
Verification drift existed because `payload_manifest.PAYLOAD_FILES` was a stale 10-file runtime subset while the bundle actually shipped a much larger homologated surface. The installer copied only that narrow payload, `run_verify()` checked only those same 10 paths, and verification-time example JSON artifacts were written into `<root>/bundles/scanner_bundle/generated_examples` instead of a scanner-owned state path under `.ark_install/scanner_bundle/`. That left the manifest, installer behavior, verify scope, and report wording slightly out of tune.

3. FILES CREATED / MODIFIED / DELETED
Modified:
- `README.md`
- `FINAL_REPORT.md`
- `scanner_installer.py`
- `payload_manifest.py`
- `contracts_py/report_sections.py`
- `contracts_py/scanner_contract.py`
- `contracts_py/shared_canon.py`
- `tools/generate_example_outputs.py`
- `tools/validate_scanner_bundle.py`
- `tests/test_bundle_tools.py`

Created:
- `tests/test_verification_regressions.py`

Deleted:
- None

4. COMMANDS RUN
- `python3 -m unittest discover -s tests -v`
- `python3 scanner_installer.py --dry-run --root /tmp/scanner_gold_root --log-dir /tmp/scanner_gold_logs`
- `python3 scanner_installer.py --apply --root /tmp/scanner_gold_root --log-dir /tmp/scanner_gold_logs`
- `python3 scanner_installer.py --verify --root /tmp/scanner_gold_root --log-dir /tmp/scanner_gold_logs`
- `python3 scanner_installer.py --rollback --root /tmp/scanner_gold_root --log-dir /tmp/scanner_gold_logs`
- `python3 tools/validate_scanner_bundle.py .`
- `python3 tools/count_bundle_mix.py .`
- `zip -qr /tmp/ark_scanner_bundle.zip ark_scanner_bundle`
- `python3 tools/count_bundle_mix.py /tmp/ark_scanner_bundle.zip`
- `python3 tools/validate_scanner_bundle.py /tmp/ark_scanner_bundle.zip`

5. HOMOLOGATION FIX
- Replaced the stale partial payload list with one canonical Python verification model derived from the full installable bundle surface.
- Kept the installer self-contained and preserved the exact CLI surface: `--dry-run`, `--apply`, `--verify`, `--rollback`, `--root`, `--log-dir`, `--install-rel`.
- Preserved default install root: `<root>/bundles/scanner_bundle`.
- Preserved state root: `<root>/.ark_install/scanner_bundle/`.
- Preserved rollback state file: `<root>/.ark_install/scanner_bundle/last_apply.json`.
- Moved verification-generated example outputs from the installed bundle tree into `<root>/.ark_install/scanner_bundle/verification_outputs/<timestamp>/`.
- Added regression coverage proving verify now fails when an installed bundle file outside the old 10-file subset is missing.
- Kept Scanner observed-only and left canonical registries, switch outputs, validator outputs, and annotations outside Scanner write authority.

6. VALIDATION RESULTS
- dry-run result: PASS (`dry_run_install_root=/tmp/scanner_gold_root/bundles/scanner_bundle`).
- apply result: PASS (`applied_install_root=/tmp/scanner_gold_root/bundles/scanner_bundle`).
- verify result: PASS (`verify_generated=24`).
- rollback result: PASS (`rollback_restored=/tmp/scanner_gold_root/bundles/scanner_bundle`).
- regression test result: PASS (`python3 -m unittest discover -s tests -v`, 14 tests passing).
- Verification surface file count: 164
- Verify outputs path: <root>/.ark_install/scanner_bundle/verification_outputs/<timestamp>/
- Explicit proof of intended surface coverage: verify now compares the installed tree against the full canonical install surface returned by `payload_manifest.install_surface(...)`, rather than a 10-file subset.
- Explicit proof of write-scope alignment: verify-time example JSON artifacts are generated only under `.ark_install/scanner_bundle/verification_outputs/...` and no longer under the installed bundle tree.
- ZIP size proof: PASS (`compressed_size=337415`, threshold `>= 307200`).
- Python mix proof: PASS (`py_count=162`, `file_count=164`, `py_ratio=0.9878048780487805`).

7. RISKS
- The bundle now verifies the full intended installed surface, so accidental local scratch files placed inside the source bundle root before packaging would become part of the computed install surface unless removed first.
- Verification examples remain synthetic corpora by design; they prove contract and path policy behavior, not production telemetry.

8. NEXT STEPS
None
