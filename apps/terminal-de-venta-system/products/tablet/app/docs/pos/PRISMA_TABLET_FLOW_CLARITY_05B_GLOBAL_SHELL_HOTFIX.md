# PRISMA Tablet Flow Clarity 05B - Global shell hotfix

## Purpose

05A correctly introduced the compact topbar and collapsible sidebar, but the CSS was scoped too narrowly to routes that explicitly rendered `data-prisma-visual-surface="tablet-pos"`.

That meant the POS route behaved better, while other Tablet routes such as `/sales/today`, `/shift`, `/catalog`, `/stock`, `/sync`, `/offline`, `/settings/license`, and `/release-gate` could fall back to the older large shell behavior. The PRISMA logo collapse control also appeared to stop working on those routes because the checked-state selectors were tied to `tablet-pos` instead of the Tablet product shell.

## Fix

05B keeps the 05A component structure and adds a global Tablet shell override:

- collapse selector now targets `.shell[data-prisma-product="tablet"]`;
- compact header applies to every Tablet route;
- compact runtime chips apply to every Tablet route;
- header controls are constrained to avoid horizontal overflow;
- header text buttons hide labels until there is enough width;
- reduced motion remains respected.

## Scope

Touched:

- `components/tablet-shell/prisma-tablet-shell.module.css`
- `tools/verify_tablet_flow_guided_sidebar_04i.mjs`
- this documentation file

Not touched:

- backend
- DB
- Prisma schema
- sales logic
- cart logic
- sync contracts
- PC
- Mobile
- packshots
- product assets

## Acceptance

- PRISMA logo toggles sidebar collapse/expand on POS and non-POS Tablet routes.
- `/sales/today` keeps the same compact topbar layout as `/pos`.
- Main content does not shift into horizontal overflow because the topbar controls are too wide.
- Light keeps operational blue behavior from 05A.
- Dark keeps dark glass/gold behavior.
