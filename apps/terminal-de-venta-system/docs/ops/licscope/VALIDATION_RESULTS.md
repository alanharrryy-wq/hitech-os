# Validation Results

| Command | Status | Exit Code | Source |
| --- | --- | --- | --- |
| pnpm -C apps/terminal-de-venta-system run verify:tenant-scope-readiness | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:license-device-crosscheck | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:customer-setup-full | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:tablet-claim | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:pc-claim | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:mobile-claim | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:sales-provenance-lineage | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:sales-outbox-linking | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:outbox-sync-canonical | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:revoke-renewal-replacement | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:surface-scope-permissions | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:customer-visible-safety | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:pii-secret-safety | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:orphan-detector | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:duplicate-detector | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:staleness-monitor | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:audit-completeness | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:golden-path-operations | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:device-without-license-blocked | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:license-without-client-blocked | PASS | 0 | verifier_outputs/command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:customer-setup:multidevice | PASS | 0 | verifier_outputs/extra-command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:customer-setup:plan-provisioning | PASS | 0 | verifier_outputs/extra-command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run e2e:012:plan-based-client-onboarding | PASS | 0 | verifier_outputs/extra-command-run-results.json |
| pnpm -C apps/terminal-de-venta-system run verify:data-surfaces | PASS | 0 | verifier_outputs/extra-command-run-results.json |
| pnpm -C apps/terminal-de-venta-system/products/tablet/app exec tsc --noEmit | PASS | 0 | verifier_outputs/typecheck-results.json |
| pnpm -C apps/terminal-de-venta-system/products/pc/app exec tsc --noEmit | PASS | 0 | verifier_outputs/typecheck-results.json |
| pnpm -C apps/terminal-de-venta-system/products/mobile/app exec tsc --noEmit | PASS | 0 | verifier_outputs/typecheck-results.json |
| Cloudflare worker deploy preflight/dry-run | BLOCKED | 0 | deploy/DEPLOY_PREFLIGHT.json |
