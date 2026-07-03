# PRISMA App Capability Requirements

- Task: `Corregir LICFLOW3 Cloudflare licensing routes para que POST /api/licenses/activate, /refresh y /revoke funcionen contra app.hitechrts.com sin downgrades, sin duplicar LICFLOW2, sin tocar secretos, sin copiar DB, sin deploy automático no autorizado y preservando Worker real prisma-cloud-semilla y D1 real prisma_cloud_semilla.`

| App | must_use | should_use | consider_required | bounded_optional | high_risk_optional | forbidden_for_scope |
|---|---|---|---|---|---|---|
| productization | authority-map, layer-budget | — | background-catalog, class-variance-authority, cloudglass-assets, clsx, framer-motion, lucide-react, motion, prisma-components, prisma-recipes, prisma-tokens, prisma-visual-os, radix-dialog, radix-dropdown-menu, radix-scroll-area, radix-select, radix-slot, radix-tabs, radix-tooltip, tailwind-merge, vanilla-extract | — | gsap, ogl, react-spring, three | — |
| tablet | authority-map, layer-budget | class-variance-authority, clsx, framer-motion, lucide-react, motion, radix-dialog, radix-scroll-area, radix-select | background-catalog, cloudglass-assets, prisma-components, prisma-recipes, prisma-tokens, prisma-visual-os, radix-dropdown-menu, radix-slot, radix-tabs, radix-tooltip, tailwind-merge, vanilla-extract | — | gsap, ogl, react-spring, three | — |
