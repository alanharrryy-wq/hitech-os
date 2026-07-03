# TABLET MAMASTROPHIC VISUAL PLAN

Date: 2026-07-03

## Visual Direction

Premium tablet retail cockpit:

- bright, tactile, light surfaces
- fewer panels and less nesting
- clear primary actions
- human empty states
- no technical vocabulary in final UI
- intent colors per action, not one-blue everywhere

## Local Token Strategy

Use Tablet-local CSS custom properties where needed:

```css
--tab-ink-strong: #101828;
--tab-ink: #1D2939;
--tab-muted: #667085;
--tab-soft: #98A2B3;
--tab-line: rgba(16, 24, 40, .10);
--tab-line-bright: rgba(255, 255, 255, .58);
--tab-surface: rgba(255, 255, 255, .88);
--tab-surface-strong: rgba(255, 255, 255, .96);
--tab-blue: #2563EB;
--tab-cyan: #06B6D4;
--tab-emerald: #10B981;
--tab-amber: #F59E0B;
--tab-violet: #8B5CF6;
--tab-rose: #F43F5E;
--tab-slate: #475467;
```

Create tokens only inside Tablet-local modules/components. Do not patch global CSS unless unavoidable.

## Component Pattern

Add a Tablet-local action tile system:

- `QuickCreateTile`
- `QuickCreateGrid`
- `QuickCreateStrip`

Required properties:

- active tile must navigate, submit, open a real existing form/dialog, or invoke a real existing handler
- deferred tile must render as non-actionable with explicit blocked/deferred state
- no `alert()`
- no `coming soon`
- no fake form submission

## Interaction States

All new interactive controls must include:

- hover
- focus-visible
- active/pressed
- disabled/deferred
- reduced-motion handling when animation is introduced

## Search Plan

Autocollapsible search applies first where an existing search owner exists:

- POS: `PosProductSearch`
- Inventario/Stock: `CatalogStockSellingAssistScreen`
- Ventas hoy: `SalesTodayScreen`
- Historial: `SalesHistoryScreen`
- Devoluciones: use ticket selection/search entry
- Exportaciones: tile/form filters where applicable

Search must expand on focus/touch/input, not hover only.

## Panel Budget

Target max:

```text
Shell > Surface > Main region > Secondary/action region
```

Reduce or avoid:

- card inside card
- decorative panels without action
- always-open export overlays
- visible diagnostic panes in primary flow
