# PRISMA Visual OS Pro anti-pendejos layer focus 00ZK

Package marker: `PRISMA_VISUAL_OS_PRO_LAYER_FOCUS_00ZK`

## Objective

Make `/visual-os/pro` safer and easier to use before deeper feature work. The editor now explains what surface and layer are being edited, ghosts unrelated controls, renames knobs by layer, and previews affected CSS variables before the operator publishes or broadcasts a recipe.

## What changed

- Adds Simple / Advanced / Expert modes.
- Adds a surface status switcher for Tablet POS, PC Backoffice, and Mobile Pulse.
- Adds a scope banner: selected surface, selected layer, what changes, and what does not change.
- Adds dynamic knob labels per layer.
- Adds ghosting for unrelated knobs.
- Adds a layer focus map where the selected layer is solid and unrelated layers are ghosted.
- Keeps JSON payload in Advanced / Expert mode, not in Simple mode.

## Safety boundaries

This iteration does not touch:

- Tablet POS business logic.
- Checkout handlers.
- Payment flow.
- Cart calculations.
- Stock or inventory logic.
- PC business logic.
- Mobile business logic.
- Shared contracts.
- Cloudflare.
- Compatibility shims.

## User behavior

The editor should answer the operator before they move a knob:

- What surface am I editing?
- What layer am I editing?
- What will change?
- What will not change?
- Which knobs matter for this layer?
- Which CSS variables will be affected?

## Validation

Run from target root:

```powershell
node tools/prisma-visual-os/verify_prisma_visual_os_pro_layer_focus_00zk.mjs
```

Installer validation also runs i02, 00T, 00N, 00ZF, tablet typecheck, and tablet build when the environment allows.
