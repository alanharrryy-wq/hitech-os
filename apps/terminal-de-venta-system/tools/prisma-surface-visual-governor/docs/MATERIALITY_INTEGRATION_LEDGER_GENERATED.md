# PRISMA M-02 · Materiality Integration Ledger

- Generated: `2026-05-27T16:08:39`
- Engine: `M-02.1-materiality-integration-ledger`
- Repo: `<REPO_ROOT>\apps\terminal-de-venta-system`
- Materiality audit ZIP: `<OUTPUT_DIR>\PRISMA_MATERIALITY_CATALOG_AUDIT_RESULT_20260526_141527 (1).zip`
- Assets visuales detectados: **516**
- Rutas detectadas: **108**

## Qué integra

Este ledger une el plan pasado de imágenes/presets con el Surface Visual Governor actual.

- El set de imágenes se convierte en familias del Atmosphere Engine.
- El Ultra Codex se usa como catálogo paramétrico.
- La receta Cloudglass se vuelve budgets por ruta.
- POS/Checkout quedan bloqueados contra familias visuales peligrosas.
- Tablet productiva queda light-first.

## Familias visuales

| Familia | Assets | Permitido | Bloqueado | Nota |
|---|---:|---|---|---|
| `pc_graphite_cloudglass_stack` | 3 | `pc, chart_lab, control_center_separate, control_center_embedded` | `pos_checkout` | Casa matriz Cloudglass: base graphite + fracture/light + mist/dust. |
| `storm_graphite_dark_showcase` | 108 | `pc_reference, chart_lab, control_center_separate, control_center_embedded, visual_os` | `tablet_productive, pos_checkout, checkout, web_eit_public` | Premium oscuro para showcase, Visual OS, Chart Lab y PC referencia. No POS/Checkout. |
| `liquid_vapor_reference` | 57 | `chart_lab, control_center_separate, control_center_embedded, visual_os, pc_reference` | `tablet_productive, pos_checkout, checkout, dense_tables` | Familia wow con humo/líquido. Entra con route budget y bozal. |
| `tablet_light_soft_clouds` | 27 | `tablet_productive, tablet_settings, tablet_sync, mobile` | `pc_dark_showcase` | Light-first para Tablet productiva. POS sólo con gate explícito. |
| `mobile_thin_mist` | 24 | `mobile` | `pos_checkout` | Bajo ruido, battery-friendly, reduced motion. |
| `web_eit_sober` | 260 | `web_eit_public` | `showcase, demo` | Público sobrio. Nada de exceso visual. |
| `control_center_visual_governance` | 9 | `control_center_separate, control_center_embedded, visual_os` | `pos_checkout` | Gobierno, salud, evidencia y command surfaces. |
| `unclassified_visual_asset` | 28 | `requires_review` | `all_until_classified` | Requiere decisión humana antes de uso. |

## Budgets por objetivo

| Budget | Surface | Goal | Background | Glass | Rim | Motion | WebGL |
|---|---|---|---|---|---|---|---|
| `pc_dashboard_hoy` | `pc` | Centro de decisiones premium. | `high` | `medium-high` | `signature_only` | `ambient + micro` | `none unless demo` |
| `pc_settings_license` | `pc` | Claridad de configuración. | `low-medium` | `low-medium` | `R0-R2` | `micro` | `none` |
| `chart_lab` | `chart_lab` | Taller visual / Power Studio. | `high` | `medium` | `R1-R4` | `ambient + chart motion` | `optional gated` |
| `tablet_productive` | `tablet` | Touch claro, light-first. | `light / low noise` | `low-medium` | `R0-R2` | `micro` | `none` |
| `pos_checkout` | `tablet_pos_checkout` | Vender rápido y tocar fácil. | `light-only` | `low` | `R0-R1` | `micro/reduced` | `forbidden` |
| `mobile` | `mobile` | Supervisor ligero. | `low noise` | `low` | `R0-R1` | `reduced/micro` | `none` |
| `web_eit` | `web_eit` | Público sobrio. | `low` | `low` | `R0-R1` | `minimal` | `none` |
| `control_center` | `control_center` | Gobierno, salud y evidencia premium. | `medium-high` | `medium-high` | `R1-R4 controlled` | `ambient + micro` | `demo/reference only` |

## Siguiente paso

M-03 debe generar un Preview Board/contact sheet de assets reales por familia y superficie antes de aplicar más UI.