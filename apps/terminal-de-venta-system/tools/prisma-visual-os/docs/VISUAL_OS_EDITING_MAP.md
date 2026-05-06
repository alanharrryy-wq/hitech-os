# PRISMA Visual OS Editing Map 00ZI

**Package:** `PRISMA_VISUAL_OS_EDITING_WORKBENCH_00ZI`  
**Version:** `20260505_v01`  
**Purpose:** make Visual OS editing fast, boring, and safe.

## Executive summary

Visual OS is stable after 00ZF and i01. The next problem is not whether it works; the next problem is knowing exactly where to edit without turning the repo into a flea-market extension cord.

This map is the canonical human guide for Visual OS edit ownership. The machine-readable sibling is:

```text
tools/prisma-visual-os/config/visual-os-editing-map.json
```

## Canonical ownership map

| Need | Edit lane | Primary files | Validation |
|---|---|---|---|
| Realtime API/state | `realtime-api` | `tools/prisma-visual-os/realtime/live-preview-server-00q.mjs` | Studio/00R/00S verifier or release gate |
| Tablet realtime route | `tablet-realtime-ui` | `products/tablet/app/app/visual-os/realtime/page.tsx` | 00T + i02 verifier |
| Tablet Pro route | `tablet-pro-ui` | `products/tablet/app/app/visual-os/pro/page.tsx` | Studio/00R/00S + i02 verifier |
| Doctors | `doctors` | `tools/prisma-visual-os/doctors/*` | 00U, 00X |
| AI doctor | `ai-doctor` | `tools/prisma-visual-os/doctors/ai_doctor_prisma_show_pos_00y.py` | 00Y |
| Release gates | `gates` | `tools/prisma-visual-os/gates/*` | 00N |
| QA | `qa` | `tools/prisma-visual-os/qa/*` | 00N / 00L chain |
| Scoring | `scoring` | `tools/prisma-visual-os/scoring/*` | Studio/00R/00S verifier |
| Generators | `generators` | `tools/prisma-visual-os/generators/*` | core/generator verifier |
| Launchers | `launchers` | `terminal_de_venta*.cmd`, `tools/prisma-visual-os/launchers/*` | i02 + release gate |
| Shims | `compatibility-shims` | root-level wrappers and relocated folders | 00ZF |
| Legacy tolerated | `legacy-tolerated` | `tools/visual`, `tools/prisma-pos-visual-control` | 01H when relevant |

## If I want to edit X, where do I go?

### Realtime API

Edit lane: `realtime-api`  
Primary file: `tools/prisma-visual-os/realtime/live-preview-server-00q.mjs`  
Keep: `http://127.0.0.1:4177/health` and `http://127.0.0.1:4177/state`.

Do not make Tablet sales depend on this API. Realtime is observability/editing, not POS life support.

### Visual OS realtime UI

Edit lane: `tablet-realtime-ui`  
Primary file: `products/tablet/app/app/visual-os/realtime/page.tsx`  
Canonical URL: `http://127.0.0.1:3120/visual-os/realtime`

### Visual OS Pro UI

Edit lane: `tablet-pro-ui`  
Primary file: `products/tablet/app/app/visual-os/pro/page.tsx`  
Canonical URL: `http://127.0.0.1:3120/visual-os/pro`

### Doctors

Edit lane: `doctors`  
Primary folder: `tools/prisma-visual-os/doctors`

Compatibility shims may exist at the root of `tools/prisma-visual-os`. Do not delete them just because they offend your sense of order.

### AI doctor

Edit lane: `ai-doctor`  
Primary file: `tools/prisma-visual-os/doctors/ai_doctor_prisma_show_pos_00y.py`

Keep it offline. No paid API calls. No OpenAI imports. This doctor reads local evidence and recommends next actions.

### Scoring

Edit lane: `scoring`  
Primary folder: `tools/prisma-visual-os/scoring`

Scoring changes must be deterministic and documented.

### QA/gates

Edit lanes: `qa` and `gates`  
Primary folders: `tools/prisma-visual-os/qa` and `tools/prisma-visual-os/gates`

The release gate must keep blockers explicit. A failed gate is not a caveat wearing sunglasses.

### Launchers

Edit lane: `launchers`

Launcher rules:

- Commands must work from any current directory.
- Prefer `%~dp0` or explicit roots.
- Show canonical URLs first.
- Do not present legacy routes as canonical launch URLs.

## Canonical URLs

```text
http://127.0.0.1:3120/
http://127.0.0.1:3130/
http://127.0.0.1:3140/
http://127.0.0.1:4177/health
http://127.0.0.1:4177/state
http://127.0.0.1:3120/visual-os/realtime
http://127.0.0.1:3120/visual-os/pro
```

## Legacy URLs

These may still exist, but must not be treated as canonical launch URLs:

```text
http://127.0.0.1:3120/prisma-dark-pos-reference
http://127.0.0.1:3140/prisma-app
```

## Compatibility shims

Shim detected does not mean failure. Shim deleted without a deprecation package does mean future pain.

Rules:

- Do not delete shims in normal feature work.
- Do not move files in i02.
- Add explanations before removing compatibility.
- 00ZF remains the final stabilization reference.

## What not to touch

- Tablet POS business logic
- PC
- Mobile
- shared contracts
- Cloudflare
- checkout behavior
- sync contracts
- 00ZF compatibility assumptions

## How to validate after editing

```powershell
node tools/prisma-visual-os/verify_prisma_visual_os_editing_workbench_00zi.mjs
python tools/prisma-visual-os/tree/prisma_visual_os_editing_workbench_00zi.py --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --verify
node tools/prisma-visual-os/verify_prisma_visual_os_pos_live_binding_00t.mjs
node tools/prisma-visual-os/gate_prisma_visual_release_00n.mjs
python tools/prisma-visual-os/tree/prisma_visual_os_final_stabilization_00zf.py --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --out-dir "F:\descargasf" --verify
```

## Helper commands

```powershell
python tools/prisma-visual-os/tree/prisma_visual_os_editing_workbench_00zi.py --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --list-lanes
python tools/prisma-visual-os/tree/prisma_visual_os_editing_workbench_00zi.py --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --lane realtime-api
python tools/prisma-visual-os/tree/prisma_visual_os_editing_workbench_00zi.py --target-root "F:\repos\hitech-os\apps\terminal-de-venta-system" --lane tablet-pro-ui --json
```

## Stop conditions

- `tools/prisma-visual-os` is missing.
- 00ZF is missing or failing.
- The edit touches Tablet POS business logic without explicit scope.
- A legacy URL is about to become canonical.
- The helper or verifier fails.

## Package marker

```text
PRISMA_VISUAL_OS_EDITING_WORKBENCH_00ZI
```
