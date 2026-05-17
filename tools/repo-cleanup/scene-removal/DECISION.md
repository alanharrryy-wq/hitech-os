# Decision

Status: GO for explicit isolation from active scope.

Chosen route:

1. Remove Scene Studio/Pitch from active Keystone navigation and direct route execution.
2. Disable the Scene Studio runner API instead of repairing the stale runner contract.
3. Exclude off-scope Scene Studio/Pitch/dev-console/test files from Keystone TypeScript and Vitest validation.
4. Remove Scene Studio from root CI validation so it does not block cleanup.
5. Do not quarantine files in this branch because no source file needs to be moved to unblock the repo; isolation is smaller and more reversible.

Why this is safest:

- The failures are localized to Keystone Scene Studio/Pitch contract drift.
- PRISMA has no runtime dependency on those modules.
- A broad Scene Studio repair would consume effort on off-scope code and risk changing visual/demo behavior.
- Moving large trees to quarantine is recoverable, but it is heavier than needed because validation can be unblocked with explicit isolation.
- Stubbing active routes/API makes the decommission honest: Scene Studio/Pitch stops acting like available runtime functionality.

What this intentionally does not do:

- It does not redesign PRISMA.
- It does not change Tablet-first behavior.
- It does not make PC or Mobile required.
- It does not repair Scene Studio/Pitch types.
- It does not delete source files.
- It does not update visual baselines.
- It does not add dependencies.
