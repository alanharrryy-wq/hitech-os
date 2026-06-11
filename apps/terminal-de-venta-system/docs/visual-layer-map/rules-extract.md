# Reglas Atlas / Governor / Visual OS encontradas

## docs/PRISMA_DARK_DESIGN_SYSTEM.md

Hits: Glass, Pill

```text
- app background,
- glass panels,
- elevated cards,
- inner highlights,
```

```text
  --prisma-radius-xl: 24px;
  --prisma-radius-pill: 999px;

  --prisma-space-1: 4px;
```

```text

### Glass panel

```css
```

## docs/PRISMA_DARK_POS_GOLDEN_VISUAL_SPECS.md

Hits: Glass

```text
| Language | es-MX |
| Visual style | Dark premium glassmorphism with warm gold accents |

## 4. Global composition
```

```text

The visual language is **dark glass + warm gold + illuminated product catalog**.

It is not “black background and yellow buttons.” That is how civilization collapses one UI at a time.
```

```text
| `--bg-card` | `#1C1E28` | product cards |
| `--bg-glass` | `rgba(25,27,36,.70)` | glass surfaces |
| `--bg-glass-strong` | `rgba(30,32,42,.84)` | active panels |

```

## docs/PRISMA_DARK_UI_KIT.md

Hits: Glass, Pill

```text
24. `ShortcutHint`
25. `GlassPanel`

---
```

```text
- Width: 200px.
- Background: near-black glass.
- Right border: subtle.
- Padding: 20px.
```

```text

Dark glass card, soft border, 12-14px radius.

---
```

## docs/PRISMA_LIGHT_DESIGN_SYSTEM.md

Hits: Pill, Light Design, Contrast

```text
# PRISMA Light Design System

**System:** PRISMA Light POS
```

```text
  --prisma-light-radius-xl: 28px;
  --prisma-light-radius-pill: 999px;

  --prisma-light-shadow-xs: 0 5px 14px rgba(20, 26, 38, 0.05);
```

```text
- Total is the largest number in the cart.
- Avoid low-contrast gray for operational text.

---
```

## docs/PRISMA_LIGHT_POS_GOLDEN_VISUAL_SPECS.md

Hits: Glass

```text

The visual language is **white frosted glass + deep navy text + blue primary action + realistic product catalog**.

It is not "white background and blue buttons." That is how civilization collapses one UI at a time.
```

```text
| `--bg-card` | `rgba(255,255,255,.88)` | product cards |
| `--bg-frosted` | `rgba(255,255,255,.72)` | glass surfaces |

### Blues
```

## docs/PRISMA_LIGHT_UI_KIT.md

Hits: Pill

```text

- White pill background.
- Integrated buttons.
- Quantity centered.
```

## docs/PRISMA_LIGHT_VISUAL_GUIDELINES.md

Hits: Responsive

```text

## 13. Responsive rules

Primary target: 4:3 landscape.
```

## docs/PRISMA_TWO_SKIN_VISUAL_CONTRACT.md

Hits: Glass

```text
|---|---|---|---|
| `dark` | PRISMA Dark POS | dark premium glass, cinematic, gold | warm gold |
| `light` | PRISMA Light POS | white/frosted premium, clean, operational | blue primary |

```

```text
| App background | graphite/black atmosférico | blanco/frío con radial azul suave |
| Panels | dark glass | white/frosted glass |
| Primary accent | gold | blue |
| Active nav | gold glass | blue gradient |
```

```text
| Primary accent | gold | blue |
| Active nav | gold glass | blue gradient |
| Active category | gold circle/glow | blue circle/ring/glow |
| Total amount | gold | blue |
```

## docs/PRISMA_VISUAL_GUIDELINES.md

Hits: Glass, Responsive

```text

PRISMA Dark POS is a premium dark point-of-sale interface for fast retail operation. It combines dark cinematic depth, glass panels, warm gold accents and large illuminated product cards.

It must look like a serious intelligent sales terminal, not like somebody downloaded a random admin template and put a sombrero on it.
```

```text
| Warm gold | Main action and selected states |
| Glass panels | Translucent panels with subtle borders |
| Product-first | Big product images with pedestal glow |
| POS-first | Search, product selection, cart, total, charge |
```

```text
1. deep background,
2. glass sidebar/cart,
3. product cards,
4. inner highlights,
```

## docs/PRISMA_VISUAL_QA_TWO_SKINS_CHECKLIST.md

Hits: Glass

```text
- [ ] background deep/dark atmosférico;
- [ ] panels dark glass;
- [ ] active `Ventas` en gold;
- [ ] active `Todos` en gold;
```

```text
- [ ] `COBRAR` gold;
- [ ] product cards dark glass;
- [ ] glows visibles;
- [ ] no neon gamer;
```

## _dependency_graphs/visual_control_map_terminal-de-venta-system_silver_frost_cyan_20260518_164438.md

Hits: Glass, Contrast

```text
  subgraph qt_backdrop[Qt Backdrop]
    qt_backdrop_painter["Glass Backdrop Painter"]
    qt_backdrop_palette["Glass Backdrop Palette"]
  end
```

```text
    qt_backdrop_painter["Glass Backdrop Painter"]
    qt_backdrop_palette["Glass Backdrop Palette"]
  end
  subgraph svg_theme[Svg Theme]
```

```text
| `qt_selector_progress_layout` | Qt Selector / Progress Assembly | `ui_qt` | Ensamble real de header, form_card, preview_card, footer, hero, body y chips dentro de SelectorDialog y ProgressUI. | `SelectorDialog._build_ui` |
| `qt_backdrop_painter` | Glass Backdrop Painter | `qt_backdrop` | Motor de dibujo del fondo glass: orbs, stars, spark flashes, sheen, vignette y campos de plata. | `FrostedGlassBackdrop.paintEvent` |
| `qt_backdrop_palette` | Glass Backdrop Palette | `qt_backdrop` | Paleta, mezclas, halos y decisión de variante selector/progress para el fondo glass de PySide. | `_glass_palette` |
| `svg_theme_defs` | SVG Theme Defs | `svg_theme` | Empaqueta gradients, grid pattern, filters, markers y CSS final en el bloque <defs> del SVG temático. | `_build_theme_svg_defs` |
```

## tools/prisma-surface-visual-governor/NEXT_STEPS.md

Hits: Governor

```text

1. `governor_inventory_engine.py`
2. `route_budget_audit_engine.py`
3. `public_leak_sanitizer_engine.py`
```

## tools/prisma-surface-visual-governor/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Toolbox Hub

**Ubicación:** `<REPO_ROOT>\apps\terminal-de-venta-system\tools\prisma-surface-visual-governor`
```

```text

**Ubicación:** `<REPO_ROOT>\apps\terminal-de-venta-system\tools\prisma-surface-visual-governor`
**Generado:** 2026-05-27T11:37:13

```

```text

Este folder es el **centro de mando local** del PRISMA Surface Visual Governor.

No reemplaza las rutas vivas de las apps. Las organiza, espejea e indexa para que el siguiente trabajo, especialmente motores `.py`, tenga una base limpia.
```

## tools/prisma-surface-visual-governor/TREE.md

Hits: Governor, Liquid, Glass

```text
```txt
prisma-surface-visual-governor
├─ contracts
│  ├─ runtime-adapters
```

```text
│     │  ├─ result_zip_inventory.json
│     │  └─ surface_governor_inventory.json
│     ├─ 00_PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_INDEX.md
│     ├─ 01_WHERE_EVERYTHING_LIVES.md
```

```text
│     │  └─ surface_governor_inventory.json
│     ├─ 00_PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_INDEX.md
│     ├─ 01_WHERE_EVERYTHING_LIVES.md
│     ├─ 02_PILOT_STATUS_MATRIX.md
```

## tools/prisma-visual-os/README_PRISMA_VISUAL_OS_LIVE_STUDIO_00O_00T.md

Hits: Visual OS, Glass, Contrast

```text
# PRISMA Visual OS / Live Studio Pro — README operativo canon

**Fecha de corte:** 2026-05-04
```

```text

PRISMA Visual OS ya tiene una cabina operativa viva para controlar y diagnosticar la experiencia visual del POS sin convertir el checkout en feria de neón.

Estado actual confirmado:
```

```text

> Visual OS puede escuchar, diagnosticar y emitir controles.
> POS puede recibir estado vivo.
> POS no acepta CSS live que mueva layout, tape cobro o cambie geometría operativa.
```

## tools/_local/inbox/prismo-command-nexus-20260526_140537/PRISMO_ONE_SHOT_IMPLEMENTATION_CLOSURE_PACK_20260526/06_PRISMO_CONTROL_CENTER_UI_STATE_MACHINE.md

Hits: Glass, Cloudglass

```text

Usar Cloudglass gobernado:

- Composer: G3/G4 premium.
```

## tools/_local/inbox/prismo-command-nexus-20260526_140537/PRISMO_DOCUMENTATION_SUITE_20260526_WITH_GEMINI_RECIPE/PRISMO_DOCUMENTATION_SUITE_20260526/06_RUNTIME/PRISMO_DB_AUTHORITY_RUNTIME_RULES.md

Hits: ATLAS

```text

Static atlas discovery can find unused, empty or stale databases. Runtime resolver and environment determine active DB.
```

## tools/_local/inbox/prismo-command-nexus-20260526_140537/PRISMO_DOCUMENTATION_SUITE_20260526_WITH_GEMINI_RECIPE/PRISMO_DOCUMENTATION_SUITE_20260526/11_UIUX/PRISMO_VISUAL_DIRECTION.md

Hits: Glass, Cloudglass

```text

- Graphite/cloudglass background.
- Double glass major panels.
- Hydro rim only on major frames.
```

```text
- Graphite/cloudglass background.
- Double glass major panels.
- Hydro rim only on major frames.
- Glow only for semantic state.
```

## tools/_local/inbox/prismo-command-nexus-20260526_140537/PRISMO_DOCUMENTATION_SUITE_20260526_WITH_GEMINI_RECIPE/PRISMO_DOCUMENTATION_SUITE_20260526/16_EVIDENCE/PRISMO_EVIDENCE_FILE_INDEX.md

Hits: ATLAS, Governor, Liquid, Glass, Accessibility, Contrast, Responsive

```text
| `tools/verify-ack-required.mjs` | 970 | `2026-05-22T12:47:00` |
| `tools/verify-code-atlas-boundaries.mjs` | 6137 | `2026-05-22T12:47:00` |
| `tools/verify-license-ops-console.mjs` | 3757 | `2026-05-22T12:47:00` |
| `tools/verify-no-fake-green.mjs` | 938 | `2026-05-22T12:47:00` |
```

```text
| `tools/verify_pc_to_tablet_catalog_delta_closure_01.mjs` | 8823 | `2026-05-22T13:19:17` |
| `tools/verify_prisma_chart_atlas_01.mjs` | 8416 | `2026-05-22T15:57:50` |
| `tools/verify_prisma_echarts_pack_01.mjs` | 7103 | `2026-05-22T15:57:50` |
| `tools/verify_prisma_event_sync_architecture_01.mjs` | 9392 | `2026-05-17T14:26:30` |
```

```text
| `tools/_local/evidence/chart-lab/handoff-pack-2026-05-22T21-55-23-533Z/payload/shared/prisma-charts/prismaChartAdapters.ts` | 47183 | `2026-05-22T15:31:25` |
| `tools/_local/evidence/chart-lab/handoff-pack-2026-05-22T21-55-23-533Z/payload/shared/prisma-charts/prismaChartAtlas.ts` | 5064 | `2026-05-22T15:32:14` |
| `tools/_local/evidence/chart-lab/handoff-pack-2026-05-22T21-55-23-533Z/payload/shared/prisma-charts/prismaChartContracts.ts` | 19561 | `2026-05-22T15:29:03` |
| `tools/_local/evidence/chart-lab/handoff-pack-2026-05-22T21-55-23-533Z/payload/shared/prisma-charts/prismaChartFlags.ts` | 1232 | `2026-05-17T14:26:30` |
```

## tools/_local/inbox/prismo-command-nexus-20260526_140537/PRISMO_DOCUMENTATION_SUITE_20260526_WITH_GEMINI_RECIPE/PRISMO_DOCUMENTATION_SUITE_20260526/16_EVIDENCE/PRISMO_KNOWN_CONTRADICTIONS.md

Hits: ATLAS

```text

`products/pc/app/data/canonical.db` may exist or appear in static atlas output, but it is **not** authority by filename.

**Authority rule:**
```

## tools/_local/inbox/prismo-command-nexus-20260526_140537/PRISMO_DOCUMENTATION_SUITE_20260526_WITH_GEMINI_RECIPE/PRISMO_DOCUMENTATION_SUITE_20260526/17_IMPLEMENTATION_RECIPES/PRISMO_GEMINI_COMMAND_NEXUS_ONE_SHOT_RECIPE.md

Hits: Glass, Cloudglass

```text

PRISMO será un módulo interno del Control Center que convierte Gemini en un analista técnico-operativo de PRISMA: consulta autoridad documental, cruza evidencia temporal, clasifica certezas, detecta contradicciones, genera briefs y devuelve respuestas visuales seguras dentro de una consola Cloudglass premium.

---
```

```text

La UI debe seguir Cloudglass Executive OS:

```txt
```

```text
1. Fondo graphite/icefield con gradientes CSS, no imagen obligatoria.
2. Surface principal tipo Cloudglass G3/G4.
3. Composer central destacado.
4. Bordes finos y glow semántico sólo en estados.
```

## tools/prisma-visual-os/docs/README_PRISMA_VISUAL_OS_FINAL_00ZF.md

Hits: Visual OS

```text
# PRISMA Visual OS Final 00ZF

Visual OS is stable when the final 00ZF verifier passes.
```

```text

Visual OS is stable when the final 00ZF verifier passes.

00ZF keeps compatibility shims, keeps legacy evidence, and makes 00T a hard gate again.
```

## tools/prisma-visual-os/docs/README_PRISMA_VISUAL_OS_TREE_00ZE.md

Hits: Visual OS

```text
# PRISMA Visual OS Tree 00ZE

Esta carpeta documenta el cierre de la migración del árbol `tools/prisma-visual-os`.
```

## tools/prisma-visual-os/docs/VISUAL_OS_EDITING_MAP.md

Hits: Visual OS, Glass

```text
# PRISMA Visual OS Editing Map 00ZI

**Package:** `PRISMA_VISUAL_OS_EDITING_WORKBENCH_00ZI`
```

```text
**Version:** `20260505_v01`
**Purpose:** make Visual OS editing fast, boring, and safe.

## Executive summary
```

```text

Visual OS is stable after 00ZF and i01. The next problem is not whether it works; the next problem is knowing exactly where to edit without turning the repo into a flea-market extension cord.

This map is the canonical human guide for Visual OS edit ownership. The machine-readable sibling is:
```

## tools/prisma-visual-os/docs/VISUAL_OS_LIVE_STATUS_TRUTH_00ZL.md

Hits: Visual OS

```text
# PRISMA Visual OS live status truth 00ZL

Package: `PRISMA_VISUAL_OS_LIVE_STATUS_TRUTH_00ZL`
```

```text

Make the Visual OS live status honest and useful after `i04`.

The `i04` layer-focus UI installed successfully, but browser screenshots showed:
```

```text

- Do not make Visual OS required for checkout.
- Do not edit Tablet POS business logic.
- Do not touch PC business logic.
```

## tools/prisma-visual-os/docs/VISUAL_OS_PRO_ANTI_PENDEJOS_LAYER_FOCUS_00ZK.md

Hits: Visual OS

```text
# PRISMA Visual OS Pro anti-pendejos layer focus 00ZK

Package marker: `PRISMA_VISUAL_OS_PRO_LAYER_FOCUS_00ZK`
```

## tools/prisma-visual-os/docs/VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM.md

Hits: Visual OS

```text
# PRISMA Visual OS route truth + LAN POS binding 00ZM

Package marker: `PRISMA_VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM`
```

```text
- Tablet POS runtime: `/pos`
- Visual OS Pro: `/visual-os/pro`
- Realtime API: `:4177`

```

```text

Visual OS must derive realtime from that same host:

- `http://192.168.1.14:4177/health`
```

## tools/prisma-visual-os/launchers/README.md

Hits: Visual OS

```text
# Visual OS launchers

Carpeta reservada para una migración futura de launchers `.cmd`.
```

## tools/prisma-visual-os/tree/PRISMA_VISUAL_OS_TREE_00ZA_INDEX.md

Hits: Visual OS

```text
# PRISMA Visual OS Tree 00ZA

Este índice fue generado por `prisma_visual_os_tree_reorg_00za.py`.
```

## tools/prisma-visual-os/tree/PRISMA_VISUAL_OS_TREE_00ZB_INDEX.md

Hits: Visual OS

```text
# PRISMA Visual OS tree 00ZB

Estado: compat shims para primeros movimientos low-risk.
```

## tools/prisma-visual-os/tree/PRISMA_VISUAL_OS_TREE_00ZC_INDEX.md

Hits: Visual OS

```text
# PRISMA Visual OS Tree 00ZC

Estado: stage 1, plan-only. Instala un planner para doctors/verifiers; no mueve archivos candidatos.
```

## tools/prisma-visual-os/tree/PRISMA_VISUAL_OS_TREE_00ZE_INDEX.md

Hits: Visual OS

```text
# PRISMA Visual OS Tree Reorg Close 00ZE

**Paquete:** `PRISMA_VISUAL_OS_TREE_REORG_CLOSE_00ZE_20260505_v02`
```

```text
**Paquete:** `PRISMA_VISUAL_OS_TREE_REORG_CLOSE_00ZE_20260505_v02`
**Estado:** cierre de migración de árbol Visual OS.
**Regla:** la raíz de `tools/prisma-visual-os` conserva shims de compatibilidad; la implementación vive en subcarpetas gobernadas.

```

## tools/prisma-visual-os/tree/PRISMA_VISUAL_OS_TREE_00ZF_INDEX.md

Hits: Visual OS

```text
# PRISMA Visual OS Tree 00ZF Index

00ZF is the final stabilization layer after 00ZE.
```

```text
- launchers: copied launchers for the new layout.
- docs and _plans: local Visual OS documentation.

Root scripts remain compatibility shims. `tools/prisma-pos-visual-control` stays as legacy archive. `tools/visual` stays as reference visual scope.
```

## tools/prisma-visual-os/_plans/PRISMA_VISUAL_OS_FINAL_STABILIZATION_00ZF.md

Hits: Visual OS

```text

Goal: finish the Visual OS migration and stabilize all hard gates.

Scope:
```

## tools/prisma-visual-os/_plans/PRISMA_VISUAL_OS_TREE_REORG_CLOSE_00ZE.md

Hits: Visual OS

```text

Cerrar la migración de Visual OS corrigiendo verificadores que todavía leían shims raíz como si fueran implementación completa.

## Cambios
```

## tools/prisma-surface-visual-governor/docs/EXTERNAL_REFERENCE_ATMOSPHERE_DO_NOT_FORGET_GENERATED.md

Hits: Liquid

```text
- No reemplazar con gradientes tristes.
- POS/Checkout no recibe Storm/Liquid/Aurora/WebGL/Pixi/heavy blur.
- Tablet productiva prefiere light/soft/snow/cloud/mist.
- Control Center puede usar Storm/Graphite/Vault y Aurora sólo gobernado.
```

```text
- Control Center puede usar Storm/Graphite/Vault y Aurora sólo gobernado.
- Chart Lab puede usar Liquid/Vapor/Showcase con route budget.
```

## tools/prisma-surface-visual-governor/docs/EXTERNAL_REFERENCE_ATMOSPHERE_PACK_GENERATED.md

Hits: Governor

```text
- Assets integrated: **1**
- Assets dir: `tools/prisma-surface-visual-governor/assets/external-reference-atmospheres/unsplash-intricate-explorer`

## Family counts
```

## tools/prisma-surface-visual-governor/docs/EXTERNAL_REFERENCE_FAMILY_ALIAS_NORMALIZER_GENERATED.md

Hits: Liquid

```text
- `light_architecture_material`: **1**
- `liquid_teal_vapor`: **2**
- `mobile_thin_mist_blue`: **1**
- `storm_forest_vault`: **1**
```

```text
- `light_architecture_material`: **1**
- `liquid_teal_vapor`: **3**
- `mobile_thin_mist`: **6**
- `storm_graphite_vault`: **3**
```

## tools/prisma-surface-visual-governor/docs/MATERIALITY_INTEGRATION_DO_NOT_FORGET_GENERATED.md

Hits: Liquid

```text
- Las imágenes reales son parte del Atmosphere Engine.
- Storm/Liquid/Vapor son familias premium, no default productivo.
- Tablet productiva es light-first.
- POS/Checkout sólo light-safe y con gate.
```

## tools/prisma-surface-visual-governor/docs/MATERIALITY_INTEGRATION_LEDGER_GENERATED.md

Hits: Governor, Visual OS, Liquid, Glass, Cloudglass

```text

Este ledger une el plan pasado de imágenes/presets con el Surface Visual Governor actual.

- El set de imágenes se convierte en familias del Atmosphere Engine.
```

```text
- El Ultra Codex se usa como catálogo paramétrico.
- La receta Cloudglass se vuelve budgets por ruta.
- POS/Checkout quedan bloqueados contra familias visuales peligrosas.
- Tablet productiva queda light-first.
```

```text
|---|---:|---|---|---|
| `pc_graphite_cloudglass_stack` | 3 | `pc, chart_lab, control_center_separate, control_center_embedded` | `pos_checkout` | Casa matriz Cloudglass: base graphite + fracture/light + mist/dust. |
| `storm_graphite_dark_showcase` | 108 | `pc_reference, chart_lab, control_center_separate, control_center_embedded, visual_os` | `tablet_productive, pos_checkout, checkout, web_eit_public` | Premium oscuro para showcase, Visual OS, Chart Lab y PC referencia. No POS/Checkout. |
| `liquid_vapor_reference` | 57 | `chart_lab, control_center_separate, control_center_embedded, visual_os, pc_reference` | `tablet_productive, pos_checkout, checkout, dense_tables` | Familia wow con humo/líquido. Entra con route budget y bozal. |
```

## tools/prisma-surface-visual-governor/docs/MATERIALITY_PREVIEW_BOARD_GENERATED.md

Hits: Governor, Visual OS, Liquid, Glass, Cloudglass

```text
|---|---:|---|
| `pc_graphite_cloudglass_stack` | 3 | Casa matriz premium: base graphite, fracturas, luz y mist/dust. Ideal para PC Dashboard/Hoy y superficies ejecutivas. |
| `storm_graphite_dark_showcase` | 80 | Showcase oscuro premium. Entra en Chart Lab, Visual OS, Control Center y PC referencia. Prohibido en POS/Checkout. |
| `liquid_vapor_reference` | 57 | Familia wow con líquido, humo y vapor. Se usa con bozal: Chart Lab, Visual OS, Control Center, PC referencia. |
```

```text
| `pc_graphite_cloudglass_stack` | 3 | Casa matriz premium: base graphite, fracturas, luz y mist/dust. Ideal para PC Dashboard/Hoy y superficies ejecutivas. |
| `storm_graphite_dark_showcase` | 80 | Showcase oscuro premium. Entra en Chart Lab, Visual OS, Control Center y PC referencia. Prohibido en POS/Checkout. |
| `liquid_vapor_reference` | 57 | Familia wow con líquido, humo y vapor. Se usa con bozal: Chart Lab, Visual OS, Control Center, PC referencia. |
| `tablet_light_soft_clouds` | 27 | Light-first, táctil, clara y luminosa. Base correcta para Tablet productiva, settings, sync y quizá mobile. |
```

```text
| `storm_graphite_dark_showcase` | 80 | Showcase oscuro premium. Entra en Chart Lab, Visual OS, Control Center y PC referencia. Prohibido en POS/Checkout. |
| `liquid_vapor_reference` | 57 | Familia wow con líquido, humo y vapor. Se usa con bozal: Chart Lab, Visual OS, Control Center, PC referencia. |
| `tablet_light_soft_clouds` | 27 | Light-first, táctil, clara y luminosa. Base correcta para Tablet productiva, settings, sync y quizá mobile. |
| `mobile_thin_mist` | 24 | Bajo ruido, liviano, battery-friendly y reduced-motion. |
```

## tools/prisma-surface-visual-governor/evidence/result_zip_inventory.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Result ZIP Inventory

| Modified | Status | ZIP | Size |
```

```text
|---|---:|---|---:|
| 2026-05-27T11:17:40 | PASS | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_19_DOCS_HUB_RESULT_20260527_111712.zip` | 14662 |
| 2026-05-27T04:23:00 | PASS | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_18_RESULT_20260527_042137.zip` | 9922 |
| 2026-05-27T04:07:00 | PASS | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040636.zip` | 18226 |
```

```text
| 2026-05-27T11:17:40 | PASS | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_19_DOCS_HUB_RESULT_20260527_111712.zip` | 14662 |
| 2026-05-27T04:23:00 | PASS | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_18_RESULT_20260527_042137.zip` | 9922 |
| 2026-05-27T04:07:00 | PASS | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040636.zip` | 18226 |
| 2026-05-27T04:01:24 | FAIL | `PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_17_RESULT_20260527_040057.zip` | 6422 |
```

## tools/prisma-surface-visual-governor/tooling/prisma-surface-governor/route-budget-enforcer/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Route Budget Enforcer Runtime

Pilot 15 Hotfix 02 installs a reusable route-budget policy and enforcer.
```

```text
- POS governance gate manifests may document denied terms without being treated as active CSS usage.
- PC dashboard accepts existing Governor/dashboard markers instead of requiring the exact literal `governed`.
- Public Surface Governor scan still blocks local paths and DB tokens.

```

```text
- PC dashboard accepts existing Governor/dashboard markers instead of requiring the exact literal `governed`.
- Public Surface Governor scan still blocks local paths and DB tokens.

This tool is intentionally conservative for POS, checkout, mobile and public shells.
```

## tools/prisma-surface-visual-governor/public-mirrors/tablet/tablet-light-shell/latest/README.md

Hits: Governor

```text

Public tablet artifacts for PRISMA Surface Visual Governor.

This folder is safe-public metadata and Atmosphere Engine assets. It must not contain local DB paths, secrets, SQLite files or deploy tokens. Active CSS uses light-first tablet assets only.
```

## tools/prisma-surface-visual-governor/public-mirrors/tablet/tablet-light-shell/pilot-05/README.md

Hits: Governor

```text

Public tablet artifacts for PRISMA Surface Visual Governor.

This folder is safe-public metadata and Atmosphere Engine assets. It must not contain local DB paths, secrets, SQLite files or deploy tokens. Active CSS uses light-first tablet assets only.
```

## tools/prisma-surface-visual-governor/public-mirrors/tablet/pos-final-gate/latest/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Pilot 06 POS Final Gate Audit

Este gate deja POS listo para revisión final sin modificar `/pos` ni `/checkout`.
```

## tools/prisma-surface-visual-governor/public-mirrors/tablet/pos-final-gate/pilot-06/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Pilot 06 POS Final Gate Audit

Este gate deja POS listo para revisión final sin modificar `/pos` ni `/checkout`.
```

## tools/prisma-surface-visual-governor/public-mirrors/pc/dashboard/latest/README.md

Hits: Governor

```text

Public dashboard artifacts for PRISMA Surface Visual Governor.

This folder is safe-public metadata and Atmosphere Engine assets. It must not contain local DB paths, secrets, SQLite files or deploy tokens.
```

## tools/prisma-surface-visual-governor/public-mirrors/pc/dashboard/pilot-04/README.md

Hits: Governor

```text

Public dashboard artifacts for PRISMA Surface Visual Governor.

This folder is safe-public metadata and Atmosphere Engine assets. It must not contain local DB paths, secrets, SQLite files or deploy tokens.
```

## tools/prisma-surface-visual-governor/public-mirrors/chart-lab/recipe-export/latest/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Pilot 02 · Chart Lab Recipe Export

This public folder contains the generated recipe export contract for Chart Lab.
```

## tools/prisma-surface-visual-governor/public-mirrors/chart-lab/recipe-export/pilot-02/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Pilot 02 · Chart Lab Recipe Export

This public folder contains the generated recipe export contract for Chart Lab.
```

## tools/prisma-surface-visual-governor/engines/python/README.md

Hits: Governor

```text

- `governor_inventory_engine.py`
- `route_budget_audit_engine.py`
- `public_leak_sanitizer_engine.py`
```

## tools/prisma-surface-visual-governor/docs/repo-docs/00_PRISMA_SURFACE_VISUAL_GOVERNOR_MASTER_INDEX.md

Hits: Governor, Visual OS

```text
# PRISMA Surface Visual Governor · Master Documentation Hub

**Generated:** 2026-05-27T11:17:40
```

```text
**Drop/evidence:** `<OUTPUT_DIR>`
**Purpose:** centralizar el mapa de documentación, herramientas, contratos públicos y evidencia del Surface Visual Governor.

## Estado resumido
```

```text

- `docs/surface-visual-governor`
- `node_modules/.pnpm/node_modules/@hitech/mobile/docs/surface-visual-governor`
- `node_modules/.pnpm/node_modules/@hitech/pc/docs/surface-visual-governor`
```

## tools/prisma-surface-visual-governor/docs/repo-docs/01_WHERE_EVERYTHING_LIVES.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Where Everything Lives

## Repo root
```

```text

`docs/surface-visual-governor`

## App docs
```

```text

- `docs/surface-visual-governor`
- `node_modules/.pnpm/node_modules/@hitech/mobile/docs/surface-visual-governor`
- `node_modules/.pnpm/node_modules/@hitech/pc/docs/surface-visual-governor`
```

## tools/prisma-surface-visual-governor/docs/repo-docs/02_PILOT_STATUS_MATRIX.md

Hits: Governor, Visual OS

```text
# PRISMA Surface Visual Governor · Pilot Status Matrix

| Pilot | Title | Latest status | Latest ZIP |
```

```text
|---:|---|---|---|
| 1 | Visual OS Materiality Catalog | NO_RECEIPT_FOUND | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_01_RESULT_20260526_154622.zip |
| 2 | Chart Lab Recipe Export | PASS | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_02_RESULT_20260526_185618.zip |
| 3 | PC Referencia Visual | PASS | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_03_RESULT_20260526_191908.zip |
```

```text
| 1 | Visual OS Materiality Catalog | NO_RECEIPT_FOUND | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_01_RESULT_20260526_154622.zip |
| 2 | Chart Lab Recipe Export | PASS | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_02_RESULT_20260526_185618.zip |
| 3 | PC Referencia Visual | PASS | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_03_RESULT_20260526_191908.zip |
| 4 | PC Dashboard / Hoy | PASS | PRISMA_SURFACE_VISUAL_GOVERNOR_PILOT_04_RESULT_20260526_192341.zip |
```

## tools/prisma-surface-visual-governor/docs/repo-docs/03_NEXT_STEPS.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Next Steps

## Current sane stop point
```

## tools/prisma-surface-visual-governor/docs/repo-docs/pilot-15-route-budget-enforcer-runtime.md

Hits: Governor

```text

This pilot installs a reusable PRISMA Surface Visual Governor route-budget enforcer.

It does not modify UI routes. It adds tooling under:
```

```text

- `tools/prisma-surface-governor/route-budget-enforcer`
- `docs/surface-visual-governor/pilot-15-route-budget-enforcer-runtime.md`

```

```text
- `tools/prisma-surface-governor/route-budget-enforcer`
- `docs/surface-visual-governor/pilot-15-route-budget-enforcer-runtime.md`

Hotfix 02 distinguishes governance manifest documentation from active visual/runtime usage.
```

## tools/prisma-surface-visual-governor/docs/repo-docs/_hub/README.md

Hits: Governor

```text

Generated machine-readable inventory for PRISMA Surface Visual Governor.

Files in this folder are indexes and evidence pointers, not product runtime code.
```

## tools/prisma-surface-visual-governor/docs/app-docs/chart-lab/pilot-02-chart-lab-recipe-export.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Pilot 02 · Chart Lab Recipe Export

## What this installed
```

```text

`products/chart-lab/app/public/surface-visual-governor/recipe-export/latest/`

- `chart.recipe.json`
```

```text

`products/chart-lab/app/src/prisma-surface-governor/chart-lab-recipe-export.ts`

This helper exposes stable paths and a small fetch function for Chart Lab UI integration in a later patch.
```

## tools/prisma-surface-visual-governor/docs/app-docs/chart-lab/pilot-16-chart-lab-recipe-studio-v2.md

Hits: Governor

```text

- `products/chart-lab/app/public/surface-visual-governor/recipe-studio-v2/latest/index.json`

Safety:
```

## tools/prisma-surface-visual-governor/docs/app-docs/pc/pilot-03-pc-referencia-visual.md

Hits: Governor, Visual OS

```text
# PRISMA Surface Visual Governor · Pilot 03 · PC Referencia Visual

## Estado esperado
```

```text
- `products/pc/app/app/referencia-visual/page.tsx`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/prisma-pc-reference-visual.css`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/index.json`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/route.visual-reference.pilot-03.json`
```

```text
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/prisma-pc-reference-visual.css`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/index.json`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/route.visual-reference.pilot-03.json`
- `products/pc/app/public/surface-visual-governor/reference-visual/pilot-03/surface-twin.pc-reference.json`
```

## tools/prisma-surface-visual-governor/docs/app-docs/pc/pilot-04-pc-dashboard-governed-hoy.md

Hits: Governor

```text
- `app/dashboard/prisma-surface-dashboard.module.css`
- `public/surface-visual-governor/dashboard/pilot-04/*`
- `public/surface-visual-governor/dashboard/latest/*`
- `scripts/verify-surface-visual-governor-pilot04.mjs`
```

```text
- `public/surface-visual-governor/dashboard/pilot-04/*`
- `public/surface-visual-governor/dashboard/latest/*`
- `scripts/verify-surface-visual-governor-pilot04.mjs`

```

```text
- `public/surface-visual-governor/dashboard/latest/*`
- `scripts/verify-surface-visual-governor-pilot04.mjs`

## Siguiente paso natural
```

## tools/prisma-surface-visual-governor/docs/app-docs/tablet/pilot-05-tablet-light-shell.md

Hits: Governor, Contrast

```text

- Tablet debe ser clara, táctil, luminosa y de alto contraste suave.
- Atmosphere Engine usa assets reales, pero con scrim claro y baja intensidad.
- No dark storm como fondo activo.
```

```text
- `products/tablet/app/app/prisma-tablet-light-shell.module.css`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/pilot-05/*`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/latest/*`
- `products/tablet/app/scripts/verify-surface-visual-governor-pilot05.mjs`
```

```text
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/pilot-05/*`
- `products/tablet/app/public/surface-visual-governor/tablet-light-shell/latest/*`
- `products/tablet/app/scripts/verify-surface-visual-governor-pilot05.mjs`

```

## tools/prisma-surface-governor/route-budget-enforcer/README.md

Hits: Governor

```text
# PRISMA Surface Visual Governor · Route Budget Enforcer Runtime

Pilot 15 Hotfix 02 installs a reusable route-budget policy and enforcer.
```

```text
- POS governance gate manifests may document denied terms without being treated as active CSS usage.
- PC dashboard accepts existing Governor/dashboard markers instead of requiring the exact literal `governed`.
- Public Surface Governor scan still blocks local paths and DB tokens.

```

```text
- PC dashboard accepts existing Governor/dashboard markers instead of requiring the exact literal `governed`.
- Public Surface Governor scan still blocks local paths and DB tokens.

This tool is intentionally conservative for POS, checkout, mobile and public shells.
```

## tools/prisma-salvage/candidates/architecture_docs/docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md

Hits: UI States

```text

## 14. UI states

Estados canonicos:
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/ACCESSIBILITY_AND_CONTRAST.md

Hits: Accessibility, Contrast

```text
# Accessibility And Contrast

Regla madre:
```

```text

Tablet: touch targets grandes, contraste claro para total/cobrar/error/offline/sync, mensajes es-MX no tecnicos. PC: focus visible, teclado en tablas/filtros/dialogs, estados empty/loading/error/offline/success consistentes.
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/PRISMA_BLACK_CSS_LAYER_NORMALIZATION_01F.md

Hits: Glass

```text

The current visual stack already has haze, glass, glow and blend effects. Adding more effects now would make the layers harder to reason about. 01F therefore adds ownership markers and validation instead of new decoration.

## 2. Governance source used
```

```text
| Background | theme/shared components/global shells | one scene per screen |
| Panel | app shell, sidebar, hero, ticket/catalog panels | interprets the background with glass |
| Card | product/KPI/module/status cards | frames content; does not create weather |
| Product stage | POS product/pedestal areas | allowed local glow island |
```

```text
- No new background.
- No stronger glass.
- No aggressive dedupe of gradients or blend modes.

```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/PRISMA_BLACK_VISUAL_GOVERNANCE_BASELINE_01E.md

Hits: Glass, Contrast

```text

PRISMA Black ya tiene una dirección clara: dark glass, premium, ejecutivo, con acentos dorados y sensación de centro de mando. El problema no es falta de efectos. El problema es que los efectos pueden duplicarse por capa: fondo, shell, panel, card, stage y botón.

Este baseline evita que el siguiente pass vuelva a meter haze, blur y glow como si fueran salsa de puesto: todo encima de todo y luego nadie sabe qué estaba sabiendo raro.
```

```text
Capa 2: Paneles grandes
  - glass fuerte
  - backdrop blur
  - borde direccional
```

```text
Capa 3: Cards
  - glass ligero
  - borde fino
  - contenido legible
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/PRISMA_BLACK_VISUAL_GOVERNANCE_PASS_01D.md

Hits: Glass

```text

- Tokens para fondo cinematográfico, glass, blur, bordes, glows y motion.
- Capa de fondo global con haze/motion sutil y `prefers-reduced-motion`.
- Paneles grandes con glass fuerte.
```

```text
- Capa de fondo global con haze/motion sutil y `prefers-reduced-motion`.
- Paneles grandes con glass fuerte.
- Cards con glass ligero.
- Product stage como vitrina local.
```

```text
- Paneles grandes con glass fuerte.
- Cards con glass ligero.
- Product stage como vitrina local.
- Flags CSS para apagar haze, noise, motion, card blur y product glow.
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/PRISMA_BLACK_VISUAL_REFINEMENT_01G.md

Hits: Contrast

```text
3. **Sin rediseño funcional**. No se tocan rutas, datos, lógica ni layout estructural.
4. **Visual premium conservador**. Se permite limpiar contraste, profundidad, sombra, blur y acabado de superficies.

## Cambio introducido por 01G
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/PRISMA_REFERENCE_VISUAL_TARGET_01H.md

Hits: Glass

```text

- dark glass cinematografico
- fondo azul-negro profundo
- brillo dorado calido
```

```text
- blur
- glassmorphism
- bordes
- brillos
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/PRISMA_TRI_SURFACE_VISUAL_CHANGE_CONTRACT_00A.md

Hits: Glass, Contrast

```text
blur
glass
border
shadow
```

```text
crear fondos premium distintos por ruta sin contrato;
crear variantes gold/glass por pantalla sin ownership;
duplicar haze local cuando ya existe haze de escena;
resolver Mobile como mockup aislado sin tokens compartidos;
```

```text
| Fondo / stage | atmósfera global | 1 escena dominante por pantalla |
| Panel | interpretar fondo | glass o solid, no ambos peleando |
| Card | enmarcar información | no reinventar clima propio |
| Contenido | informar | máximo contraste razonable |
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/RESPONSIVE_BREAKPOINTS.md

Hits: Responsive

```text
# Responsive Breakpoints

Regla madre:
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/TABLET_TOUCH_UI_GUIDE.md

Hits: Tablet Touch

```text
# Tablet Touch Ui Guide

Regla madre:
```

## tools/prisma-salvage/candidates/architecture_docs/docs/design/UI_STATES_AND_FEEDBACK.md

Hits: UI States

```text
# Ui States And Feedback

Regla madre:
```

## tools/prisma-salvage/candidates/architecture_docs/docs/mobile/PRISMA_APP_MOBILE_07_API_CLIENT_UI_BINDING.md

Hits: Responsive

```text
- componentes para KPIs, caja, ventas, inventario, alertas, reportes y sucursales;
- CSS responsive de vista móvil premium;
- verificador propio `verify:ui-binding`.

```

## tools/prisma-pos-visual-control/docs/CONTROL_PLANE_README.md

Hits: Glass

```text

- glass blur and opacity
- glow and highlights
- card radius and depth
```

## tools/prisma-pos-visual-control/docs/SHELL_ATMOSPHERE_LOCK_README.md

Hits: Glass

```text
- Shell cinematic background, haze, bloom, vignette and subtle texture.
- Sidebar glass, active nav glow and PRISMA brand presence.
- Header glass and content separation.
- POS surface bridge so catalog, ticket and COBRAR stay above the background.
```

```text
- Sidebar glass, active nav glow and PRISMA brand presence.
- Header glass and content separation.
- POS surface bridge so catalog, ticket and COBRAR stay above the background.

```

## tools/prisma-pos-visual-control/docs/VISUAL_CONTROL_MATRIX.md

Hits: Glass, Accessibility, Contrast

```text
|---|---|---|---|---|---|
| `pos.glass.blur` | `pos.surface, shell.surface` | Primary blur for POS glass surfaces. | `12..56px` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glass.opacity` | `pos.surface` | Glass surface opacity control. | `0.36..0.92` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glass.border.opacity` | `pos.surface, shell.surface` | Border visibility for glass panels. | `0.08..0.42` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
```

```text
| `pos.glass.blur` | `pos.surface, shell.surface` | Primary blur for POS glass surfaces. | `12..56px` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glass.opacity` | `pos.surface` | Glass surface opacity control. | `0.36..0.92` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glass.border.opacity` | `pos.surface, shell.surface` | Border visibility for glass panels. | `0.08..0.42` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glow.intensity` | `product.stage, cta` | General glow strength for premium highlights. | `0.0..0.8` | High visual drift if pushed to ext
```

```text
| `pos.glass.opacity` | `pos.surface` | Glass surface opacity control. | `0.36..0.92` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glass.border.opacity` | `pos.surface, shell.surface` | Border visibility for glass panels. | `0.08..0.42` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.glow.intensity` | `product.stage, cta` | General glow strength for premium highlights. | `0.0..0.8` | High visual drift if pushed to extremes; verify /pos screenshots and coverage report. | `products/tablet/app/components/pos/pos.visual.tokens.json` |
| `pos.highlight.opacity` | `cards, ticket, controls` | Opacity for highlight washes and hairline shines. | `0.0..0.42` | High visual drif
```

## tools/prisma-pos-visual-control/docs/VISUAL_PRESET_COOKBOOK.md

Hits: Glass, Contrast

```text
## retail_sharp
Menos blur, más nitidez, más contraste operativo.

## low_glow
```

```text
## low_glow
Baja brillo cuando el glass empieza a parecer feria patronal.

## reference_match
```
