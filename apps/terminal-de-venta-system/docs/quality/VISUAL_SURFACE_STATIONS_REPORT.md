# Visual Surface Stations Report

- status: `CERTIFIED`
- generated: `2026-06-19T10:14:18.680Z`
- branch: `feat/prisma-premium-design-mise-en-place-v1`
- task: `Build PRISMA Premium Visual Mise en Place v1 across Tablet, Mobile/App, PC, Web/Edit, Control Center, Chart Lab and Shared UI, preparing all surfaces to use the full available visual library/effect/token/component ecosystem for future premium design.`

| Priority | Surface | Style Profile | Must Use | Should Use | Guardrail |
| --- | --- | --- | --- | --- | --- |
| 1 | tablet | light, tactile, high-contrast-soft, touch-first, operational clarity | authority-map, layer-budget, prisma-recipes, prisma-tokens, prisma-visual-os | prisma-components | dark/obsidian dominant Tablet theme; global CSS blast; background layer that blocks selling flow; Tablet keeps local-sale autonomy; visual layers cannot block product, cart, checkout or shift operations. |
| 2 | mobile | thin, fast, truthful, compact, low-overhead touch | authority-map, layer-budget | clsx, lucide-react, radix-slot | heavy WebGL; large atmospheric backgrounds; desktop/tablet density; Mobile/App stays compact and assistive; it does not become POS. |
| 3 | pc | desktop-grade, dense but readable, controlled glass/graphite only if PC governor allows | authority-map, layer-budget | clsx, lucide-react, radix-dialog, radix-tabs, radix-tooltip | Tablet-only visuals copied blindly; unbounded WebGL in operational surfaces; PC remains governance/backoffice; do not copy Tablet selling density into PC. |
| 4 | web | public/portal appropriate, lightweight, governed branding | authority-map, layer-budget | n/a | POS operational assumptions in public surfaces; Web/Edit stays public or editorial safe; do not import POS assumptions. |
| 5 | control-center | general governed PRISMA surface | authority-map, layer-budget | n/a | Control Center stays operator status and release control, with public-safe redaction. |
| 6 | chart-lab | visual experimentation with evidence and lab boundaries | authority-map, layer-budget | background-catalog, cloudglass-assets, framer-motion, gsap, motion, ogl, react-spring, three | promoting lab visuals to production without governor/evidence; Chart Lab can experiment, but lab visuals need governor evidence before production use. |
| 7 | shared-ui | cross-surface primitives and recipes with strict compatibility | authority-map, layer-budget | class-variance-authority, clsx, radix-slot, tailwind-merge | breaking changes without tri-surface evidence; Shared UI changes require cross-surface compatibility evidence before promotion. |
