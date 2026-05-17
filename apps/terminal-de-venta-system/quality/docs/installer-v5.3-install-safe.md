# PRISMA Quality OS v5.3 install-safe calibration

This bundle separates quality package installation from full repository release readiness.

- `--apply` and `--verify` require static payload checks, self-test, and automation.
- Phase 5 still runs during installer verification, but external repo launcher/docs drift is advisory by default.
- Use `--strict-phase5` when the installation should rollback on full repo Phase 5 blockers.
- Q26 still blocks missing official launchers/wrappers when Control Center is active. Content drift such as stale wrapper references is a warning unless `PRISMA_QUALITY_STRICT_PHASE5=1`.

This prevents a quality-only replacement from rolling back because of files outside the `quality/` folder.
