# TABREST_NON_POS Surface Plan

Date: 2026-07-02

## Scope

Polish all remaining PRISMA Tablet product surfaces except the primary POS sale/cobro surface. Keep Tablet as a local selling surface with clear cashier/supervisor workflows.

## Non-Negotiables

- Keep colors light and tactile unless a specific exterior backdrop needs a soft dimmed gradient.
- Do not expose lab, QA, runtime, route, outbox, issuer, signed payload, Visual OS, ADLANT4, LICFLOW2, or other technical vocabulary in operator-facing UI.
- Keep bottom dock as primary navigation; topbar is context only.
- Export and diagnostic actions must be secondary, collapsed, or support-scoped.
- Do not touch PC, Web, Mobile, Control Center, licensing engines, or sync contracts.
- Do not start dev servers, kill processes, create ZIP handoffs, or push automatically.

## Work Slices

1. Shell and navigation
   - Confirm final nav only exposes product routes.
   - Remove technical helper copy from topbar flow labels.
   - Keep `/events/outbox` and `/prisma-pulse` out of final nav/home.

2. Home
   - Reduce to a one-glance start surface.
   - Keep at most six obvious actions.
   - Remove runtime/admin/support panel from primary home view.

3. Shift
   - Make the primary action depend on shift state.
   - Replace informal copy.
   - Keep open/close/count review clear and calm.

4. Inventory and catalog
   - Keep stock search and product state strong.
   - Move export to a secondary details/dropdown affordance.
   - Collapse heavy filters where appropriate.

5. Sales and returns
   - Keep sales list/detail readable.
   - Make export secondary.
   - Strengthen return reason/confirm clarity without changing business semantics.

6. Sync/offline/export
   - Make pending work the main story.
   - Move diagnostics/export to support details.
   - Rename technical status labels to human operator labels.

7. License/settings
   - Keep readonly license truth.
   - Keep support details collapsed.
   - Avoid activation/import/admin actions inside Tablet.

8. Verifiers and final reports
   - Add TABREST verifiers requested by the package.
   - Produce final changed files, verifier summary, backout, and improvement matrix.

## Required TABREST Verifiers

- `verify_tabrest_non_pos_copy_0207.mjs`
- `verify_tabrest_non_pos_navigation_0207.mjs`
- `verify_tabrest_inventory_export_secondary_0207.mjs`
- `verify_tabrest_sync_human_pending_0207.mjs`
- `verify_tabrest_license_human_0207.mjs`
- `verify_tabrest_interactions_0207.mjs`
- `verify_zero_important_0207.mjs` or the existing zero-priority gate.

## Final Reports To Produce

- `TABREST_NON_POS_FINAL_REPORT.md`
- `TABREST_NON_POS_CHANGED_FILES.md`
- `TABREST_NON_POS_VERIFIER_SUMMARY.json`
- `TABREST_NON_POS_BACKOUT.md`
- `TABREST_NON_POS_100_IMPROVEMENTS_MATRIX.md`
