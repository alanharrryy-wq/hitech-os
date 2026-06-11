# VALIDATION_MATRIX

Static validators are repo-native and run without server.

| validator | command | status |
| --- | --- | --- |
| node-check-all | node --check tools/prisma-visual/**/*.mjs | PASS |
| legacy-python-visual-catalog | python tools/prisma-visual/run_visual_catalog_validators.py . | PASS |
| validate-component-variants | node tools/prisma-visual/validate-component-variants/index.mjs | PASS |
| validate-domain-contracts | node tools/prisma-visual/validate-domain-contracts/index.mjs | PASS |
| validate-migration-tiers | node tools/prisma-visual/validate-migration-tiers/index.mjs | PASS |
| validate-adoption-scorecard | node tools/prisma-visual/validate-adoption-scorecard/index.mjs | PASS |
| validate-visual-debt | node tools/prisma-visual/validate-visual-debt/index.mjs | PASS |
| validate-screen-blueprints | node tools/prisma-visual/validate-screen-blueprints/index.mjs | PASS |
| validate-generator-contracts | node tools/prisma-visual/validate-generator-contracts/index.mjs | PASS |
| validate-atlas-map | node tools/prisma-visual/validate-atlas-map/index.mjs | PASS |
| validate-context-motors | node tools/prisma-visual/validate-context-motors/index.mjs | PASS |
| validate-governed-system | node tools/prisma-visual/validate-governed-system/index.mjs | PASS |
| generate tablet | node tools/prisma-visual/generate-surface-screen/index.mjs --surface tablet | PASS |
| generate pc | node tools/prisma-visual/generate-surface-screen/index.mjs --surface pc | PASS |
| generate mobile | node tools/prisma-visual/generate-surface-screen/index.mjs --surface mobile | PASS |
| generate chart-lab | node tools/prisma-visual/generate-surface-screen/index.mjs --surface chart-lab | PASS |
| generate kiosk | node tools/prisma-visual/generate-surface-screen/index.mjs --surface kiosk | PASS |
| plan-migration | node tools/prisma-visual/plan-migration/index.mjs | PASS |
| measure-adoption | node tools/prisma-visual/measure-adoption/index.mjs | PASS |
