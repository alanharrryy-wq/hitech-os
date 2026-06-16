# PRISMA Visual Capability Matrix

- Task: `PRISMA Tablet POS Sell premium visual continuation: audit and stabilize incomplete Codex visual changes for Tablet POS / Vender / Productos / Carrito / Checkout / Cobrar. Preserve real products, prices, SKUs, cart bindings, business logic and Mount Fuji/cloudy background. Scope is Tablet POS sell screen foreground only. Audit new CSS priority override usage and globals.css risk, separate useful visual changes from CSS contamination, then prepare authority for one definitive fix: product vitrines, premium cart column, stable iridescent Cobrar CTA, light tactile foreground. Exclude PC, Mobile, Chart Lab, database sync, schema changes, commits, push, merge, process kill, port cleanup, dev server start, Playwright loop and Prisma hot regeneration.`
- Status: `PASS`
- Generated: `2026-06-11T19:11:14-06:00`
- Visual required: `True`

| Capability | Kind | Available | Risk | Default decision | Evidence count | Contribution |
|---|---|---:|---|---|---:|---|
| background-catalog | repo_capability | yes | medium | review | 40 | Governed atmospheric/background assets per surface. |
| clsx | package | yes | low | use_if_relevant | 2 | Safe local class composition. |
| tailwind-merge | package | yes | low | use_if_relevant | 2 | Conflict-aware utility class merge if Tailwind utilities are in use. |
| authority-map | repo_capability | yes | low | mandatory | 2 | Connects recipes/components to allowed surfaces and authority constraints. |
| layer-budget | repo_capability | yes | low | mandatory | 12 | Limits visual depth/effects so premium layers do not crush performance or clarity. |
| lucide-react | package | yes | low | use_if_relevant | 2 | Lightweight governed icons for actions/status/navigation clarity. |
| cloudglass-assets | repo_capability | yes | medium | review | 40 | Liquid/Pill/Cloudglass references, assets, docs, runtime implementations and candidates. |
| framer-motion | package | yes | medium | use_if_relevant | 1 | Bounded microinteractions: tap feedback, panel reveal, cart/payment transitions. |
| gsap | package | yes | high | bounded_optional_high_risk | 3 | Timeline animation only when already used safely and not overkill. |
| motion | package | yes | medium | use_if_relevant | 3 | Bounded microinteractions if compatible with current import style. |
| react-spring | package | yes | medium | use_if_relevant | 1 | Spring microinteractions if target surface already uses it. |
| react-spring-web | package | no | medium | not_available | 0 | Spring microinteractions if target surface already uses it. |
| prisma-components | repo_capability | yes | low | prefer | 13 | Governed PRISMA surfaces, cards, panels, action buttons and product/cart/checkout components. |
| radix-dialog | package | yes | low | use_if_relevant | 2 | Accessible dialog/confirmation surfaces for checkout and guarded actions. |
| radix-dropdown-menu | package | yes | low | use_if_relevant | 2 | Accessible command/menu surfaces for structured actions. |
| radix-scroll-area | package | yes | low | use_if_relevant | 2 | Controlled scroll for product grids, carts and dense touch regions. |
| radix-select | package | yes | low | use_if_relevant | 2 | Accessible selects for filters, variants and checkout options. |
| radix-slot | package | yes | low | use_if_relevant | 2 | Composition primitive for PRISMA buttons/panels without DOM noise. |
| radix-tabs | package | yes | low | use_if_relevant | 2 | Accessible tabbed segmentation for categories or payment modes. |
| radix-tooltip | package | yes | medium | use_if_relevant | 2 | Non-blocking help for secondary controls when touch UX stays clear. |
| prisma-recipes | repo_capability | yes | low | prefer | 27 | Approved visual recipes including liquid/glass/pill/cloudglass where authorized. |
| vanilla-extract | package | yes | medium | use_if_relevant | 2 | Static governed tokens/styles when repo pattern already exists. |
| prisma-tokens | repo_capability | yes | low | prefer | 14 | Governed spacing, color, radius, shadow, typography and state primitives. |
| class-variance-authority | package | yes | low | use_if_relevant | 2 | Typed class variants for governed component states. |
| prisma-visual-os | repo_capability | yes | low | prefer | 25 | Governed controls, layers, presets, recipes and release gates. |
| ogl | package | yes | high | bounded_optional_high_risk | 2 | Bounded ambient/background WebGL only when layer budget allows. |
| three | package | yes | high | bounded_optional_high_risk | 2 | 3D/WebGL for lab/background use, rarely for operational POS. |

## Rule

For premium/visual work, the result package must list which available capabilities were used, which were rejected, and why. No blind all-library usage; no tiny cosmetic fake-premium.
