# Tree

```txt
prisma-surface-visual-governor
├─ contracts
│  ├─ runtime-adapters
│  │  ├─ chart-lab
│  │  │  ├─ chart-lab-recipe-export.schema.json
│  │  │  └─ chart-lab-recipe-export.ts
│  │  ├─ mobile
│  │  │  └─ surface-runtime-adapter.ts
│  │  ├─ pc
│  │  │  └─ surface-runtime-adapter.ts
│  │  └─ tablet
│  │     └─ surface-runtime-adapter.ts
│  └─ README.md
├─ docs
│  ├─ app-docs
│  │  ├─ chart-lab
│  │  │  ├─ pilot-02-chart-lab-recipe-export.md
│  │  │  └─ pilot-16-chart-lab-recipe-studio-v2.md
│  │  ├─ mobile
│  │  │  └─ pilot-09-mobile-supervisor-thin-mist-shell.md
│  │  ├─ pc
│  │  │  ├─ pilot-03-pc-referencia-visual.md
│  │  │  └─ pilot-04-pc-dashboard-governed-hoy.md
│  │  ├─ tablet
│  │  │  ├─ pilot-05-tablet-light-shell.md
│  │  │  ├─ pilot-06-pos-final-gate-audit.md
│  │  │  ├─ pilot-07-pos-light-safe-shell.md
│  │  │  └─ pilot-08-checkout-light-safe-shell.md
│  │  └─ web
│  │     └─ pilot-11-eit-web-public-sober-shell.md
│  └─ repo-docs
│     ├─ _hub
│     │  ├─ pilot_status_matrix.csv
│     │  ├─ pilot_status_matrix.json
│     │  ├─ README.md
│     │  ├─ result_zip_inventory.json
│     │  └─ surface_governor_inventory.json
│     ├─ 00_PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_INDEX.md
│     ├─ 01_WHERE_EVERYTHING_LIVES.md
│     ├─ 02_PILOT_STATUS_MATRIX.md
│     ├─ 03_NEXT_STEPS.md
│     ├─ pilot-15-route-budget-enforcer-runtime.md
│     └─ pilot-17-surface-runtime-adapter-v1.md
├─ engines
│  ├─ node
│  │  └─ README.md
│  ├─ powershell
│  │  └─ README.md
│  └─ python
│     ├─ __init__.py
│     ├─ engine_contract.md
│     └─ README.md
├─ evidence
│  ├─ receipts
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_02_RESULT_20260526_185618__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_03_RESULT_20260526_191908__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_04_RESULT_20260526_192341__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_05_RESULT_20260526_194231__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_05_RESULT_20260526_195528__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_06_RESULT_20260526_195929__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_07_RESULT_20260526_200433__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_08_RESULT_20260526_201830__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_09_RESULT_20260526_222559__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_11_RESULT_20260526_235603__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_11_RESULT_20260526_235842__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_12_RESULT_20260527_000748__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_13_MASTER_CLOSEOUT_RESULT_20260527_001125_1___receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_13_MASTER_CLOSEOUT_RESULT_20260527_001125__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_02_RESULT_20260527_014923_1___receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_02_RESULT_20260527_014923__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_03_RESULT_20260527_020110__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_03_RESULT_20260527_020333__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_RESULT_20260527_012405__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_RESULT_20260527_015824__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_RESULT_20260527_020620__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_RESULT_20260527_024247__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_RESULT_20260527_024513__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_RESULT_20260527_024818__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_16_RESULT_20260527_025347__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_16_RESULT_20260527_025714__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040057__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040636__receipt.json
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_18_RESULT_20260527_042137__receipt.json
│  │  └─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_19_DOCS_HUB_RESULT_20260527_111712__receipt.json
│  ├─ reports
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_01_RESULT_20260526_154622__00_EXECUTIVE_SUMMARY.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_02_RESULT_20260526_185618__pilot-02-chart-lab-recipe-export.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_02_RESULT_20260526_185618__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_03_RESULT_20260526_191908__pilot-03-pc-referencia-visual.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_03_RESULT_20260526_191908__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_04_RESULT_20260526_192341__next-pilot-05-note.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_04_RESULT_20260526_192341__pilot-04-pc-dashboard-governed-hoy.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_04_RESULT_20260526_192341__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_05_RESULT_20260526_195528__pilot-05-tablet-light-shell.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_05_RESULT_20260526_195528__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_07_RESULT_20260526_200433__pilot-07-pos-light-safe-shell.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_07_RESULT_20260526_200433__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_08_RESULT_20260526_201830__pilot-08-checkout-light-safe-shell.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_08_RESULT_20260526_201830__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_09_RESULT_20260526_222559__pilot-09-mobile-supervisor-thin-mist-shell.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_09_RESULT_20260526_222559__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_10_RESULT_20260526_235305__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_11_RESULT_20260526_235842__pilot-11-eit-web-public-sober-shell.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_11_RESULT_20260526_235842__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_13_MASTER_CLOSEOUT_REPORT_20260527_002900__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_13_MASTER_CLOSEOUT_RESULT_20260527_001125_1___PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_CLOSEOUT_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_13_MASTER_CLOSEOUT_RESULT_20260527_001125__PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_CLOSEOUT_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_02_RESULT_20260527_014923_1___PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_02_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_02_RESULT_20260527_014923__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_02_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_03_RESULT_20260527_020110__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_03_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_03_RESULT_20260527_020333__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_REMEDIATION_03_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_RESULT_20260527_012405__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_VISUAL_QA_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_RESULT_20260527_015824__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_VISUAL_QA_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_RESULT_20260527_020620__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_14_VISUAL_QA_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_RESULT_20260527_024247__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_ROUTE_BUDGET_ENFORCER_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_RESULT_20260527_024513__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_ROUTE_BUDGET_ENFORCER_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_RESULT_20260527_024818__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_15_ROUTE_BUDGET_ENFORCER_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_16_RESULT_20260527_025347__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_16_RECIPE_STUDIO_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_16_RESULT_20260527_025714__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_16_RECIPE_STUDIO_REPORT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040057__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040636__pilot-17-surface-runtime-adapter-v1.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040636__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040636__README.md
│  │  ├─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_18_RESULT_20260527_042137__PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_18_VISUAL_REGRESSION_REPORT.md
│  │  └─ PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_19_DOCS_HUB_RESULT_20260527_111712__02_PILOT_STATUS_MATRIX.md
│  ├─ README.md
│  ├─ result_zip_inventory.json
│  └─ result_zip_inventory.md
├─ inventory
│  ├─ copied-files.csv
│  ├─ copied-files.json
│  ├─ README.md
│  └─ source-map.json
├─ public-mirrors
│  ├─ chart-lab
│  │  ├─ atmosphere-assets
│  │  │  └─ backgrounds
│  │  │     ├─ aurora-slate-veil.svg
│  │  │     ├─ liquid-operations-smoke.svg
│  │  │     ├─ liquid-operations-ui-reference.png
│  │  │     ├─ obsidian-cloud-motion.svg
│  │  │     ├─ storm-cloud-operations-real.jpg
│  │  │     ├─ storm-glass-horizon.svg
│  │  │     └─ tablet-soft-gray-clouds.svg
│  │  ├─ recipe-export
│  │  │  ├─ latest
│  │  │  │  ├─ background.recipe.json
│  │  │  │  ├─ chart.recipe.json
│  │  │  │  ├─ index.json
│  │  │  │  ├─ motion.recipe.json
│  │  │  │  ├─ README.md
│  │  │  │  ├─ surface.compatibility.json
│  │  │  │  ├─ ultra-codex.index.json
│  │  │  │  └─ visual.recipe.json
│  │  │  └─ pilot-02
│  │  │     ├─ background.recipe.json
│  │  │     ├─ chart.recipe.json
│  │  │     ├─ index.json
│  │  │     ├─ motion.recipe.json
│  │  │     ├─ README.md
│  │  │     ├─ surface.compatibility.json
│  │  │     ├─ ultra-codex.index.json
│  │  │     └─ visual.recipe.json
│  │  ├─ recipe-studio-v2
│  │  │  ├─ latest
│  │  │  │  ├─ index.json
│  │  │  │  └─ README.md
│  │  │  └─ pilot-16
│  │  │     ├─ index.json
│  │  │     └─ README.md
│  │  └─ runtime-adapter
│  │     ├─ latest
│  │     │  └─ index.json
│  │     └─ pilot-17
│  │        └─ index.json
│  ├─ mobile
│  │  ├─ mobile-thin-mist-shell
│  │  │  ├─ latest
│  │  │  │  ├─ atmosphere-assets
│  │  │  │  │  └─ backgrounds
│  │  │  │  │     ├─ aurora-slate-veil.svg
│  │  │  │  │     ├─ liquid-operations-smoke.svg
│  │  │  │  │     ├─ liquid-operations-ui-reference.png
│  │  │  │  │     ├─ obsidian-cloud-motion.svg
│  │  │  │  │     ├─ storm-cloud-operations-real.jpg
│  │  │  │  │     ├─ storm-glass-horizon.svg
│  │  │  │  │     └─ tablet-soft-gray-clouds.svg
│  │  │  │  ├─ index.json
│  │  │  │  ├─ README.md
│  │  │  │  ├─ receipt.expected.json
│  │  │  │  ├─ route.visual-budget.mobile-thin-mist.json
│  │  │  │  └─ surface.compatibility.mobile-thin-mist.json
│  │  │  └─ pilot-09
│  │  │     ├─ atmosphere-assets
│  │  │     │  └─ backgrounds
│  │  │     │     ├─ aurora-slate-veil.svg
│  │  │     │     ├─ liquid-operations-smoke.svg
│  │  │     │     ├─ liquid-operations-ui-reference.png
│  │  │     │     ├─ obsidian-cloud-motion.svg
│  │  │     │     ├─ storm-cloud-operations-real.jpg
│  │  │     │     ├─ storm-glass-horizon.svg
│  │  │     │     └─ tablet-soft-gray-clouds.svg
│  │  │     ├─ index.json
│  │  │     ├─ README.md
│  │  │     ├─ receipt.expected.json
│  │  │     ├─ route.visual-budget.mobile-thin-mist.json
│  │  │     └─ surface.compatibility.mobile-thin-mist.json
│  │  └─ runtime-adapter
│  │     ├─ latest
│  │     │  └─ index.json
│  │     └─ pilot-17
│  │        └─ index.json
│  ├─ pc
│  │  ├─ dashboard
│  │  │  ├─ latest
│  │  │  │  ├─ atmosphere-assets
│  │  │  │  │  └─ backgrounds
│  │  │  │  │     ├─ aurora-slate-veil.svg
│  │  │  │  │     ├─ liquid-operations-smoke.svg
│  │  │  │  │     ├─ liquid-operations-ui-reference.png
│  │  │  │  │     ├─ obsidian-cloud-motion.svg
│  │  │  │  │     ├─ storm-cloud-operations-real.jpg
│  │  │  │  │     ├─ storm-glass-horizon.svg
│  │  │  │  │     └─ tablet-soft-gray-clouds.svg
│  │  │  │  ├─ recipe-export
│  │  │  │  │  ├─ background.recipe.json
│  │  │  │  │  ├─ chart.recipe.json
│  │  │  │  │  ├─ index.json
│  │  │  │  │  ├─ motion.recipe.json
│  │  │  │  │  ├─ surface.compatibility.json
│  │  │  │  │  ├─ ultra-codex.index.json
│  │  │  │  │  └─ visual.recipe.json
│  │  │  │  ├─ index.json
│  │  │  │  ├─ materiality-catalog.pointer.json
│  │  │  │  ├─ README.md
│  │  │  │  ├─ route-budget.pc-dashboard.pilot-04.json
│  │  │  │  ├─ surface-twin.pc-dashboard.json
│  │  │  │  └─ surface.compatibility.dashboard.json
│  │  │  └─ pilot-04
│  │  │     ├─ atmosphere-assets
│  │  │     │  └─ backgrounds
│  │  │     │     ├─ aurora-slate-veil.svg
│  │  │     │     ├─ liquid-operations-smoke.svg
│  │  │     │     ├─ liquid-operations-ui-reference.png
│  │  │     │     ├─ obsidian-cloud-motion.svg
│  │  │     │     ├─ storm-cloud-operations-real.jpg
│  │  │     │     ├─ storm-glass-horizon.svg
│  │  │     │     └─ tablet-soft-gray-clouds.svg
│  │  │     ├─ recipe-export
│  │  │     │  ├─ background.recipe.json
│  │  │     │  ├─ chart.recipe.json
│  │  │     │  ├─ index.json
│  │  │     │  ├─ motion.recipe.json
│  │  │     │  ├─ surface.compatibility.json
│  │  │     │  ├─ ultra-codex.index.json
│  │  │     │  └─ visual.recipe.json
│  │  │     ├─ index.json
│  │  │     ├─ materiality-catalog.pointer.json
│  │  │     ├─ README.md
│  │  │     ├─ route-budget.pc-dashboard.pilot-04.json
│  │  │     ├─ surface-twin.pc-dashboard.json
│  │  │     └─ surface.compatibility.dashboard.json
│  │  ├─ reference-visual
│  │  │  ├─ latest
│  │  │  │  ├─ atmosphere-assets
│  │  │  │  │  └─ backgrounds
│  │  │  │  │     ├─ aurora-slate-veil.svg
│  │  │  │  │     ├─ liquid-operations-smoke.svg
│  │  │  │  │     ├─ liquid-operations-ui-reference.png
│  │  │  │  │     ├─ obsidian-cloud-motion.svg
│  │  │  │  │     ├─ storm-cloud-operations-real.jpg
│  │  │  │  │     ├─ storm-glass-horizon.svg
│  │  │  │  │     └─ tablet-soft-gray-clouds.svg
│  │  │  │  ├─ recipe-export
│  │  │  │  │  ├─ background.recipe.json
│  │  │  │  │  ├─ chart.recipe.json
│  │  │  │  │  ├─ index.json
│  │  │  │  │  ├─ motion.recipe.json
│  │  │  │  │  ├─ surface.compatibility.json
│  │  │  │  │  ├─ ultra-codex.index.json
│  │  │  │  │  └─ visual.recipe.json
│  │  │  │  ├─ index.json
│  │  │  │  ├─ materiality-catalog.registry.json
│  │  │  │  ├─ prisma-pc-reference-visual.css
│  │  │  │  ├─ README.md
│  │  │  │  ├─ route.visual-reference.pilot-03.json
│  │  │  │  └─ surface-twin.pc-reference.json
│  │  │  └─ pilot-03
│  │  │     ├─ atmosphere-assets
│  │  │     │  └─ backgrounds
│  │  │     │     ├─ aurora-slate-veil.svg
│  │  │     │     ├─ liquid-operations-smoke.svg
│  │  │     │     ├─ liquid-operations-ui-reference.png
│  │  │     │     ├─ obsidian-cloud-motion.svg
│  │  │     │     ├─ storm-cloud-operations-real.jpg
│  │  │     │     ├─ storm-glass-horizon.svg
│  │  │     │     └─ tablet-soft-gray-clouds.svg
│  │  │     ├─ recipe-export
│  │  │     │  ├─ background.recipe.json
│  │  │     │  ├─ chart.recipe.json
│  │  │     │  ├─ index.json
│  │  │     │  ├─ motion.recipe.json
│  │  │     │  ├─ surface.compatibility.json
│  │  │     │  ├─ ultra-codex.index.json
│  │  │     │  └─ visual.recipe.json
│  │  │     ├─ index.json
│  │  │     ├─ materiality-catalog.registry.json
│  │  │     ├─ prisma-pc-reference-visual.css
│  │  │     ├─ README.md
│  │  │     ├─ route.visual-reference.pilot-03.json
│  │  │     └─ surface-twin.pc-reference.json
│  │  └─ runtime-adapter
│  │     ├─ latest
│  │     │  └─ index.json
│  │     └─ pilot-17
│  │        └─ index.json
│  ├─ tablet
│  │  ├─ checkout-light-safe-shell
│  │  │  ├─ latest
│  │  │  │  ├─ atmosphere-assets
│  │  │  │  │  └─ backgrounds
│  │  │  │  │     ├─ aurora-slate-veil.svg
│  │  │  │  │     ├─ liquid-operations-smoke.svg
│  │  │  │  │     ├─ liquid-operations-ui-reference.png
│  │  │  │  │     ├─ obsidian-cloud-motion.svg
│  │  │  │  │     ├─ storm-cloud-operations-real.jpg
│  │  │  │  │     ├─ storm-glass-horizon.svg
│  │  │  │  │     └─ tablet-soft-gray-clouds.svg
│  │  │  │  ├─ index.json
│  │  │  │  ├─ README.md
│  │  │  │  ├─ receipt.expected.json
│  │  │  │  ├─ route.visual-budget.checkout-light-safe.json
│  │  │  │  └─ surface.compatibility.checkout-light-safe.json
│  │  │  └─ pilot-08
│  │  │     ├─ atmosphere-assets
│  │  │     │  └─ backgrounds
│  │  │     │     ├─ aurora-slate-veil.svg
│  │  │     │     ├─ liquid-operations-smoke.svg
│  │  │     │     ├─ liquid-operations-ui-reference.png
│  │  │     │     ├─ obsidian-cloud-motion.svg
│  │  │     │     ├─ storm-cloud-operations-real.jpg
│  │  │     │     ├─ storm-glass-horizon.svg
│  │  │     │     └─ tablet-soft-gray-clouds.svg
│  │  │     ├─ index.json
│  │  │     ├─ README.md
│  │  │     ├─ receipt.expected.json
│  │  │     ├─ route.visual-budget.checkout-light-safe.json
│  │  │     └─ surface.compatibility.checkout-light-safe.json
│  │  ├─ pos-final-gate
│  │  │  ├─ latest
│  │  │  │  ├─ index.json
│  │  │  │  ├─ pos.compatibility.gate.json
│  │  │  │  ├─ pos.visual-budget.json
│  │  │  │  ├─ README.md
│  │  │  │  └─ surface-visual-governor.pilot-06.json
│  │  │  └─ pilot-06
│  │  │     ├─ index.json
│  │  │     ├─ pos.compatibility.gate.json
│  │  │     ├─ pos.visual-budget.json
│  │  │     ├─ README.md
│  │  │     └─ surface-visual-governor.pilot-06.json
│  │  ├─ pos-light-safe-shell
│  │  │  ├─ latest
│  │  │  │  ├─ atmosphere-assets
│  │  │  │  │  └─ backgrounds
│  │  │  │  │     ├─ aurora-slate-veil.svg
│  │  │  │  │     ├─ liquid-operations-smoke.svg
│  │  │  │  │     ├─ liquid-operations-ui-reference.png
│  │  │  │  │     ├─ obsidian-cloud-motion.svg
│  │  │  │  │     ├─ storm-cloud-operations-real.jpg
│  │  │  │  │     ├─ storm-glass-horizon.svg
│  │  │  │  │     └─ tablet-soft-gray-clouds.svg
│  │  │  │  ├─ index.json
│  │  │  │  ├─ README.md
│  │  │  │  ├─ route.pos-light-safe-shell.pilot-07.json
│  │  │  │  └─ surface.compatibility.pos-light-safe.json
│  │  │  └─ pilot-07
│  │  │     ├─ atmosphere-assets
│  │  │     │  └─ backgrounds
│  │  │     │     ├─ aurora-slate-veil.svg
│  │  │     │     ├─ liquid-operations-smoke.svg
│  │  │     │     ├─ liquid-operations-ui-reference.png
│  │  │     │     ├─ obsidian-cloud-motion.svg
│  │  │     │     ├─ storm-cloud-operations-real.jpg
│  │  │     │     ├─ storm-glass-horizon.svg
│  │  │     │     └─ tablet-soft-gray-clouds.svg
│  │  │     ├─ index.json
│  │  │     ├─ README.md
│  │  │     ├─ route.pos-light-safe-shell.pilot-07.json
│  │  │     └─ surface.compatibility.pos-light-safe.json
│  │  ├─ runtime-adapter
│  │  │  ├─ latest
│  │  │  │  └─ index.json
│  │  │  └─ pilot-17
│  │  │     └─ index.json
│  │  └─ tablet-light-shell
│  │     ├─ latest
│  │     │  ├─ atmosphere-assets
│  │     │  │  └─ backgrounds
│  │     │  │     ├─ aurora-slate-veil.svg
│  │     │  │     ├─ liquid-operations-smoke.svg
│  │     │  │     ├─ liquid-operations-ui-reference.png
│  │     │  │     ├─ obsidian-cloud-motion.svg
│  │     │  │     ├─ storm-cloud-operations-real.jpg
│  │     │  │     ├─ storm-glass-horizon.svg
│  │     │  │     └─ tablet-soft-gray-clouds.svg
│  │     │  ├─ recipe-export
│  │     │  │  ├─ background.recipe.json
│  │     │  │  ├─ chart.recipe.json
│  │     │  │  ├─ index.json
│  │     │  │  ├─ motion.recipe.json
│  │     │  │  ├─ surface.compatibility.json
│  │     │  │  ├─ ultra-codex.index.json
│  │     │  │  └─ visual.recipe.json
│  │     │  ├─ index.json
│  │     │  ├─ materiality-catalog.pointer.json
│  │     │  ├─ README.md
│  │     │  ├─ route-budget.tablet-light-shell.pilot-05.json
│  │     │  ├─ surface-twin.tablet-light-shell.json
│  │     │  ├─ surface.compatibility.tablet-light-shell.json
│  │     │  └─ tablet-light-shell.tokens.json
│  │     └─ pilot-05
│  │        ├─ atmosphere-assets
│  │        │  └─ backgrounds
│  │        │     ├─ aurora-slate-veil.svg
│  │        │     ├─ liquid-operations-smoke.svg
│  │        │     ├─ liquid-operations-ui-reference.png
│  │        │     ├─ obsidian-cloud-motion.svg
│  │        │     ├─ storm-cloud-operations-real.jpg
│  │        │     ├─ storm-glass-horizon.svg
│  │        │     └─ tablet-soft-gray-clouds.svg
│  │        ├─ recipe-export
│  │        │  ├─ background.recipe.json
│  │        │  ├─ chart.recipe.json
│  │        │  ├─ index.json
│  │        │  ├─ motion.recipe.json
│  │        │  ├─ surface.compatibility.json
│  │        │  ├─ ultra-codex.index.json
│  │        │  └─ visual.recipe.json
│  │        ├─ index.json
│  │        ├─ materiality-catalog.pointer.json
│  │        ├─ README.md
│  │        ├─ route-budget.tablet-light-shell.pilot-05.json
│  │        ├─ surface-twin.tablet-light-shell.json
│  │        ├─ surface.compatibility.tablet-light-shell.json
│  │        └─ tablet-light-shell.tokens.json
│  └─ web
│     └─ eit-web-public-sober-shell
│        ├─ latest
│        │  ├─ index.json
│        │  ├─ README.md
│        │  └─ surface.compatibility.eit-web-public-sober.json
│        └─ pilot-11
│           ├─ index.json
│           ├─ README.md
│           └─ surface.compatibility.eit-web-public-sober.json
├─ scripts
│  ├─ original-verifiers
│  │  ├─ chart-lab
│  │  │  ├─ verify-surface-visual-governor-pilot02.mjs
│  │  │  └─ verify-surface-visual-governor-pilot16-recipe-studio-v2.mjs
│  │  ├─ mobile
│  │  │  └─ verify-surface-visual-governor-pilot09-mobile-thin-mist.mjs
│  │  ├─ pc
│  │  │  ├─ verify-surface-visual-governor-pilot03.mjs
│  │  │  └─ verify-surface-visual-governor-pilot04.mjs
│  │  ├─ tablet
│  │  │  ├─ verify-surface-visual-governor-pilot05.mjs
│  │  │  ├─ verify-surface-visual-governor-pilot06-pos-gate.mjs
│  │  │  ├─ verify-surface-visual-governor-pilot07-pos-light-safe.mjs
│  │  │  └─ verify-surface-visual-governor-pilot08-checkout-light-safe.mjs
│  │  └─ web
│  │     └─ verify-surface-visual-governor-pilot11-eit-web-sober.mjs
│  └─ print-tree.ps1
├─ tooling
│  └─ prisma-surface-governor
│     ├─ route-budget-enforcer
│     │  ├─ prisma.route-budget.policy.json
│     │  ├─ README.md
│     │  ├─ route-budget-enforcer.mjs
│     │  └─ verify-route-budget-enforcer.mjs
│     └─ surface-runtime-adapter
│        ├─ prisma.surface-runtime-adapter.schema.json
│        ├─ README.md
│        ├─ surface-runtime-adapter.mjs
│        └─ verify-surface-runtime-adapter.mjs
├─ manifest.json
├─ NEXT_STEPS.md
└─ README.md
```
