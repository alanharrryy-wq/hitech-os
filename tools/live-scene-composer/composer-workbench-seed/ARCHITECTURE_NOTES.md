# Architecture Notes

## Why Dock/Menu/Toolbar Contribution Patterns Were Rejected

Dock/menu/toolbar contribution patterns from Repo Analyzer are tightly bound to a Qt host shell and imply that extension points are equivalent to visual shell slots.

Live Scene Composer workbench seed requires a different boundary:

- module registration is explicit and bounded
- module ownership is explicit (`owner` in manifest)
- UI layout is a simple host seam, not a plugin-driven shell mutation system

Keeping dock/menu/toolbar contribution APIs would overfit the seed to a host model that Composer does not own.

## Why Bridge Access Remains Adapter-Only

Runtime mutation writes are intentionally restricted behind `RuntimeMutationBridgeAdapter` + `MutationProvider`.

Modules do not receive raw bridge handles. They can only issue `requestMutation(intent)` through module context.

This preserves:

- policy enforcement centralization
- safe-mode defaults
- replaceable routing for future runtime bridge implementations

Commit operations in the current seed are explicitly blocked in stub mode to prevent accidental direct writes.

## How This Seed Preserves Sibling-Product Boundaries

The seed is isolated to:

- `tools/live-scene-composer/composer-workbench-seed`

No imports are added to or from sibling product packages (including runtime-debug-console).

No host product code outside this folder was modified.

The result is a generic workbench kernel that can evolve independently while keeping Live Scene Composer architecture boundaries explicit.
