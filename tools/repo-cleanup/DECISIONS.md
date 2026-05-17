# PRISMA Repository Cleanup Decisions

Status: INITIAL_DECISIONS_ONLY

Repository root:

`F:\repos\hitech-os`

## Decision 1: Stop Consolidation On Baseline Typecheck Failure

Decision:

Stop before topic branch creation, PR creation, quarantine moves, merge, or close operations.

Reason:

`pnpm run typecheck` failed in `F:\repos\hitech-os\apps\keystone` before cleanup began. The user explicitly required baseline validation and instructed that PRs should be merged only after validation passes.

Replacement/survivor:

None chosen yet.

Risk:

HIGH if ignored. Merging PRISMA cleanup into a failing baseline would make it impossible to prove cleanup preserved buildability.

## Decision 2: Preserve Dirty Working Tree

Decision:

Do not reset, clean, delete, or force checkout any dirty files.

Reason:

The working tree contains mixed user/pre-existing work and validated PRISMA Round 2 work. It must be split by explicit paths later.

Replacement/survivor:

Deferred.

Risk:

HIGH if broad Git operations are used.

## Decision 3: Keep `products/web/app` Off-Release For Now

Decision:

Treat `F:\repos\hitech-os\apps\terminal-de-venta-system\products\web\app` as preserved but off-release.

Reason:

It is untracked and has dependency ranges set to `latest`. It should not be promoted into the active workspace without an approved lockfile contract.

Replacement/survivor:

The active PRISMA workspace remains Tablet, PC, Mobile, and Chart Lab.

Risk:

MEDIUM. It is valuable product material, but not release-ready.

## Decision 4: Do Not Resolve Branch Collisions Yet

Decision:

Record collisions only.

Reason:

Collision resolution requires a green baseline and careful comparison of branches. The current repository-wide typecheck is not green.

Replacement/survivor:

Deferred.

Risk:

CRITICAL if branch content is merged before the Keystone blocker is fixed.
