# PRISMA Visual OS live status truth 00ZL

Package: `PRISMA_VISUAL_OS_LIVE_STATUS_TRUTH_00ZL`
Iteration: `i04b`

## Purpose

Make the Visual OS live status honest and useful after `i04`.

The `i04` layer-focus UI installed successfully, but browser screenshots showed:

- `/visual-os/pro` reporting realtime `error`.
- The Tablet POS passive badge reporting `00T Live error sin receta`.
- PC and Mobile tiles saying `listo para receta`, which could be misread as live connection even when global realtime was failing.

## Changes

- `PosLiveBinding` now listens to the named SSE event `prisma.visual.controls`.
- `PosLiveBinding` preserves the legacy 00T verifier literal for tablet_pos filtering while adding named event support.
- `PosLiveBinding` also hydrates the latest recipe from `/state` so it can recover a recipe after page load.
- `PosLiveBinding` keeps the last known recipe visible during transient EventSource reconnects.
- `/visual-os/pro` surface tiles now avoid fake optimism: non-selected surfaces show `no confirmado` unless they actually received a payload.
- `/visual-os/pro` realtime status label now says `error: revisa 4177` instead of a bare `error`.

## Non-goals

- Do not make Visual OS required for checkout.
- Do not edit Tablet POS business logic.
- Do not touch PC business logic.
- Do not touch Mobile business logic.
- Do not touch shared contracts.
- Do not touch Cloudflare.

## Manual check

1. Start Visual OS realtime on `http://127.0.0.1:4177`.
2. Open `http://127.0.0.1:3120/visual-os/pro`.
3. Open `http://127.0.0.1:3120/`.
4. Move a Pro control.
5. Confirm the 00T badge shows a recipe name instead of `sin receta`.

If realtime is down, the UI should say so clearly. No more magical optimism, because software already lies enough before breakfast.
