<!-- Generated from ATLAS_CHAT_SHARED_CORE.zip on 2026-05-08. Do not treat this as source code. -->


# ATLAS_SHARED_CORE_VISUAL_OS

Estado: atlas inicial mejorado.  
Alcance: `products/shared-ui/prisma/**`, `config/prisma-visual-os/**`, `styles/prisma-visual-os/**`, contratos Visual OS y QA cross-surface.

## Propósito

Visual OS es el contrato visual compartido de PRISMA. No es un folder de CSS bonito para que cada quien agarre color como dulces en piñata; es un sistema gobernado con tokens, controles, capas, presets, scorecards, release gates y QA tri-superficie.

## Raíces confirmadas

| Raíz | Responsabilidad |
|---|---|
| `products/shared-ui/prisma/README.md` | Activación de temas, tokens canónicos, componentes compartidos y reglas visuales. |
| `products/shared-ui/prisma/GOLDEN_VISUAL_SPEC.md` | Contrato visual de referencia POS: dark premium, light frosted, composición, proporciones y criterios PASS/FAIL. |
| `products/shared-ui/prisma/tokens/prisma-theme.css` | Tokens semánticos canónicos. |
| `products/shared-ui/prisma/components/prisma-components.css` | Componentes compartidos con `data-prisma-component`. |
| `products/shared-ui/prisma/visual-os/**` | Control plane, layers, presets, recipes, runtime schema, QA matrix, release gate, variant packs y tokens bridge. |
| `config/prisma-visual-os/**` | Controles activos, policies, presets, recipes y guardrails. |
| `styles/prisma-visual-os/**` | CSS generado/operativo para layers, controls y light operational POS. |
| `tools/prisma-visual-os/**` | Generadores, verifiers, gates, doctors, live preview y tree tooling. |
| `docs/design/PRISMA_VISUAL_OS_*` | Contratos, control plane, bindings, QA, release gates y planes de estabilización. |

## Contrato visual compartido

### Temas

`products/shared-ui/prisma/README.md` confirma activación por `data-theme` en `html`:

```text
data-theme="prisma-dark"
data-theme="prisma-light"
```

### Tokens de identidad

Tokens confirmados por `GOLDEN_VISUAL_SPEC.md`:

```text
--prisma-app-background
--prisma-surface
--prisma-glass-surface
--prisma-sidebar-surface
--prisma-card-surface
--prisma-cart-panel-surface
--prisma-text-primary
--prisma-text-secondary
--prisma-text-muted
--prisma-border-soft
--prisma-border-gold
--prisma-accent-gold
--prisma-accent-gold-soft
--prisma-accent-gold-strong
--prisma-accent-cool-frosted
--prisma-frosted-accent-gradient
--prisma-shadow-glass
--prisma-shadow-gold
```

### Componentes compartidos normalizados

`products/shared-ui/prisma/README.md` y `GOLDEN_VISUAL_SPEC.md` declaran componentes oficiales. Los más relevantes para Shared Core:

```text
AppShell, Sidebar, BrandBlock, NavItem, TerminalStatusCard, TopBar,
SearchBar, ScanButton, IconButton, UserMenu, CategoryRail, CategoryButton,
ProductGrid, ProductCard, ProductImageStage, FavoriteStar, Pagination,
CartPanel, CartHeader, CartItemRow, QuantityStepper, TotalsSummary,
CheckoutButton, SecondaryActionCard, Toast, EmptyState, ErrorState
```

## Capas Visual OS

`prisma-visual-os.layers.json` define 10 capas oficiales:

| Layer | Rol operativo |
|---|---|
| `background` | Fondo, textura, viñeta; no compite con texto. |
| `atmosphere` | Glow/bloom/haze; no lava contenido. |
| `shell` | Sidebar/header/marco; no roba prioridad al flujo. |
| `surface` | Cards/paneles; separa sin ensuciar. |
| `content` | Texto, precios, datos; gana sobre decoración. |
| `action` | Botones y CTA; `COBRAR` domina. |
| `state` | Error/warning/offline/stock; visible sin drama barato. |
| `focus` | Hover/active/focus ring; claro para touch/teclado. |
| `overlay` | Modales/drawers/payment; prioridad temporal. |
| `debug` | Guías visuales; apagado por defecto. |

Guardrails confirmados:

- Content gana sobre atmosphere cuando la legibilidad está en riesgo.
- Action gana sobre efectos premium en checkout y POS.
- Debug layer debe ser opt-in y jamás shippear visible por default.
- Tablet touch targets >= 44px; POS primary actions >= 52px.

## Controles y presets

### Controles declarados

`prisma-visual-os.controls.json` declara controles maestros como:

```text
brand_tone, surface_density, operational_contrast, depth_glass, commercial_emphasis, motion_temper, touch_safety, data_legibility, critical_action_weight, ambient_noise, state_signal_strength, surface_separation
```

### Presets oficiales

`prisma-visual-os.presets.json` declara:

```text
BLACK_PREMIUM, LIGHT_OPERATIONAL, DUAL_BALANCE, POS_TOUCH_REFERENCE, PC_DENSE_ADMIN, MOBILE_PULSE
```

Interpretación de presets:

| Preset | Uso compartido |
|---|---|
| `BLACK_PREMIUM` | Dark premium cinematográfico sin sacrificar claridad POS. |
| `LIGHT_OPERATIONAL` | Modo claro operativo/frosted para tutoriales, soporte y pantallas visibles al cliente. |
| `DUAL_BALANCE` | Balance de ecosistema PRISMA. |
| `POS_TOUCH_REFERENCE` | Referencia Tablet `/pos`, producto/carrito/total/COBRAR dominan. |
| `PC_DENSE_ADMIN` | Backoffice denso, legible, administrativo. |
| `MOBILE_PULSE` | Pulso rápido para dueño, alertas y resúmenes. |

## Runtime Visual OS 00D/00E

`PRISMA_VISUAL_OS_00D_00E_CONTRACT.md` confirma dos piezas:

1. **00D Visual Layers System**: define capas oficiales.
2. **00E Visual Controls Runtime**: define el archivo activo de perillas y genera CSS consumible por Tablet, PC y Mobile.

Contrato público para otros frentes:

```text
config/prisma-visual-os/prisma-visual-controls.active.json
styles/prisma-visual-os/prisma-visual-layers.css
styles/prisma-visual-os/prisma-visual-controls.generated.css
docs/design/PRISMA_VISUAL_OS_00D_00E_CONTRACT.md
```

Si faltan, paquetes posteriores deben declararse `BLOCKED_DEPENDENCY` y no aplicar cambios destructivos.

## Release gate Visual OS

`prisma-visual-os.release-gate.00n.json` confirma:

| Campo | Valor confirmado |
|---|---|
| Status válidos | `READY`, `BLOCKED_DEPENDENCY`, `FAIL` |
| Dependency score mínimo | 100 |
| Overall static score mínimo | 82 |
| Surface role fit score mínimo | 82 |
| State visibility score mínimo | 82 |
| Variant pack completeness mínimo | 5 |

Prefijos prohibidos en payload del release gate 00N:

```text
packages/shared-kernel/
shared/contracts/
products/tablet/app/
```

Exact forbidden:

```text
shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json
```

## Tri-surface governance

`PRISMA_TRI_SURFACE_VISUAL_GUARDIAN_00B.md` define superficies oficiales:

| ID canónico | Rol |
|---|---|
| `prisma.tablet.pos` | Venta, caja, ticket, operación local, eventos/outbox. Primaria y standalone. |
| `prisma.pc.backoffice` | Administración, inventario, auditoría, compras, dashboard, reconciliación. Asset complementario. |
| `prisma.mobile.app` | Consulta ligera, alertas, pulso operativo, seguimiento ejecutivo. Asset complementario. |

Estados obligatorios de cobertura:

```text
TOUCHED, VALIDATED, EXCLUDED
```

Estado prohibido:

```text
OMITTED
```

Regla crítica: si una entrega visual toca `products/shared-ui/prisma/**`, las tres superficies deben quedar `TOUCHED` o `VALIDATED`; ninguna puede quedar `EXCLUDED`.

## Dependencias consumidoras confirmadas

| Consumidor | Evidencia de `analysis/all_app_shared_dependency_hits.json` |
|---|---|
| Mobile | Importa tokens/componentes, usa `data-prisma-visual-os="MOBILE_PULSE"`, importa Visual OS tokens/layers/generated controls. |
| Tablet | Importa tokens/componentes/layers/generated controls/light operational tokens; usa licensing y Visual OS live binding. |
| PC | Aparece como consumidor de Visual OS, shared UI y/o runtime/backoffice bindings en dependencias cruzadas. |

## Workflow recomendado para cambio visual compartido

1. Clasificar si el cambio toca tokens, layers, controls, preset, recipe, component skin, shell o release gate.
2. Revisar `PRISMA_TRI_SURFACE_VISUAL_CHANGE_CONTRACT_00A/B` y Guardian 00B/00C.
3. Si toca `products/shared-ui/prisma/**`, declarar Tablet, PC y Mobile como `TOUCHED` o `VALIDATED`.
4. Actualizar control/preset/token en fuente canónica, no en CSS suelto.
5. Regenerar CSS cuando aplique.
6. Correr verificadores Visual OS y release gate.
7. Documentar rollback: restaurar control activo/tokens previos y regenerar CSS.

## Verificadores y herramientas detectadas

| Herramienta | Ruta |
|---|---|
| Generador controls 00E | `tools/prisma-visual-os/generate_prisma_visual_os_controls_00e.mjs` |
| Verifier core 00D/00E | `tools/prisma-visual-os/verify_prisma_visual_os_core_00d_00e.mjs` |
| Cross-surface QA 00L | `tools/prisma-visual-os/run_prisma_visual_cross_surface_qa_00l.mjs` |
| Release gate 00N | `tools/prisma-visual-os/gate_prisma_visual_release_00n.mjs` |
| Variant packs 00M | `tools/prisma-visual-os/print_prisma_visual_variant_packs_00m.mjs` |
| Doctors POS | `tools/prisma-visual-os/doctor_prisma_show_pos_scan_00u.py`, `00x.py`, AI doctor `00y.py` |
| Live preview | `tools/prisma-visual-os/live-preview-server-00q.mjs` |
| POS live binding verifier | `tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs` |

## Riesgos visuales

| Riesgo | Señal temprana | Mitigación |
|---|---|---|
| Drift por CSS local | Colores sueltos o overrides fuera de tokens | Migrar a tokens semánticos y verificar QA tri-superficie. |
| Light mode SaaS azul | Light deja de ser frosted/cálido y usa azul plano | Revalidar `GOLDEN_VISUAL_SPEC.md` y `LIGHT_OPERATIONAL`. |
| CTA débil | `COBRAR` compite con acciones secundarias | Revisar action layer, critical action weight y cart hierarchy. |
| Debug visible | Debug layers quedan encendidos | Gate/guardrail: debug opt-in y off por defecto. |
| Tablet inaccesible | Touch targets bajan de 44px | Verificar controls `touch_safety` y CSS resultante. |
| Shared path omitido | Se toca shared-ui y una superficie queda `OMITTED` | Guardian 00B: estado prohibido. |

## Pendientes visuales

1. Confirmar owner humano definitivo del Visual OS; los docs mencionan `Chat A`/`Chat B` como frentes de paquete.
2. Confirmar comandos finales porque algunos docs contienen rutas Windows con escapes dañados.
3. Confirmar si `products/shared-ui/prisma/visual-os/prisma-visual-os.tokens.css` o `tokens/prisma-theme.css` es fuente primaria para cada superficie; hoy ambos existen con responsabilidades distintas.
4. Confirmar política de versionado para presets `00A`, `00D/00E`, `00L/00M/00N`, `00R/00S`, `00T`, `00ZF`.
