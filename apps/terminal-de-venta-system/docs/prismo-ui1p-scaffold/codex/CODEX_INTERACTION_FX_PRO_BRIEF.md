# PRISMO UI1P FX2 · Codex Interaction FX Pro Brief

## Mission
Turn PRISMO into a live **Adaptive Intelligence Theater Pro**. The UI must consume Theater Query / render_plan / memory / evidence contracts and render interactive surfaces. Do not build a static mock.

## Core changes from fix1
- Remove removed format selector permanently.
- Use 3 dependent controls: objective, domain, lens.
- Use free text + generated chips + command palette.
- Use **Auto Render Ensemble** to choose all applicable visual blocks.
- Exploit available libraries as governed effects:
  - Radix for accessible selects/dialogs/popovers/tabs/accordion.
  - Motion for React for hover/press/layout/reveal.
  - GSAP for stage/background choreography.
  - ECharts for chart_spec_preview/risk/evidence blocks.
  - TanStack Table only in technical drawer/evidence table.
  - React Hook Form + Zod for composer and contract validation.
  - Sonner for glass toasts.
  - cmdk for command palette.
  - Vaul for detail/evidence drawer.
  - resizable panels for optional workbench split.
  - SVG filters for subtle hydro rim, not text.

## Non-negotiable UX
The user should feel: choose intent, choose area, choose lens, write natural text, receive a premium rendered answer.

## No-go
No raw HTML. No `safe mode`, `preview only`, `coming soon`, `future`, `experimental` labels in main UI. No opaque glass. No static hardcoded cards as final wiring.

## Integration route
1. Discover real PRISMO Theater/control-center files.
2. Connect composer to `POST /api/prismo/theater/query` or adapter.
3. The adapter calls current learning endpoints and render_plan.
4. Render returned blocks through `PrismoAutoRenderEnsemble`.
5. Put technical overflow in drawer.
6. Save feedback.
7. Produce screenshots and result/fail ZIP.
