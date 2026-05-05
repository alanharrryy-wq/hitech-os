# Switch Engine Bundle Closeout

1. STATUS

READY FOR HANDOFF

2. ROOT CANON

- Archive top-level directory: `ark_switch_engine_bundle/`
- Installed subtree: `<root>/bundles/switch_engine_bundle`
- State root: `<root>/.ark_install/switch_engine_bundle`
- Rollback state file: `<root>/.ark_install/switch_engine_bundle/last_apply.json`

3. NOTES

- `reports_real/` remains excluded from canonical switch inputs.
- Verify emits only the required switch artifacts under `.ark_install/switch_engine_bundle/verify_outputs/`.
- The moved bundle root `switch_engine_bundle` is an accepted canonical installed subtree name alongside the archive root name.
