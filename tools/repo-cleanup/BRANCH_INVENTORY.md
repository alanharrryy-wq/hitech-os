# PRISMA Repository Branch Inventory

Status: READ_ONLY_INVENTORY

Repository root:

`F:\repos\hitech-os`

Default branch:

`origin/main`

Current branch:

`prisma/launcher-os-quality-phase4`

## Open PRs

GitHub open PR inventory was collected with:

```powershell
gh pr list --state open --limit 100 --json number,title,headRefName,baseRefName,isDraft,url,mergeStateStatus,updatedAt,author
```

Important PRs for PRISMA cleanup:

| PR | State | Draft | Base | Head | Theme | Risk |
| --- | --- | --- | --- | --- | --- | --- |
| #71 | BEHIND | false | `main` | `prisma/launcher-os-quality-phase4` | PRISMA launcher / quality phase 4 | HIGH: current branch, huge diff, behind main |
| #70 | CLEAN | true | `agent-workbench-rescue-20260508_020502_utc` | `codex/prisma-sync-observability-20260512` | PRISMA sync observability | MEDIUM: non-main base |
| #68 | BEHIND | true | `main` | `agent-workbench-rescue-20260508_020502_utc` | agent workbench preservation | HIGH: broad preservation base |
| #66 | CLEAN | false | `codex/prisma-terminal-split-20260506` | `feat/prisma-mobile-crystal-command` | Mobile intelligence UI | HIGH: non-main base and overlaps PRISMA mobile |
| #43 | DIRTY | false | `main` | `prisma/tablet-pos-pages-shell-03` | older full-tree PRISMA consolidation | CRITICAL: 3487 files and many collisions |
| #41 | DIRTY | false | `main` | `codex/gitignore-restored-untracked-ignore` | gitignore local preservation | MEDIUM |
| #40 | BEHIND | false | `main` | `codex/policy-no-move-no-delete` | no-move/no-delete policy | MEDIUM |
| #39 | DIRTY | false | `main` | `codex/capatch-gitignore-and-archive-policy` | CAPATCH hygiene | MEDIUM |
| #38 | DIRTY | true | `main` | `codex/capatch-phase0-close-fix` | CAPATCH runtime | HIGH |
| #37 | DIRTY | false | `main` | `feature/cloudflare-tooling` | Cloudflare tooling | MEDIUM |
| #36 | DIRTY | false | `main` | `feature/synapse-x-app` | Synapse app | HIGH |
| #35 | DIRTY | false | `main` | `feature/external-interaction-template` | EIT app | HIGH |
| #33 | DIRTY | false | `main` | `feature/code-atlas-capatch-runtime` | Code Atlas CAPATCH | HIGH |
| #32 | DIRTY | false | `main` | `feature/keystone-scene-studio-and-pitch` | Keystone scene studio | CRITICAL: baseline typecheck failure is Keystone |
| #30 | DIRTY | true | `main` | `codex/synapse-x-engine-ui-host` | Synapse X | HIGH |
| #28 | DIRTY | true | `main` | `codex/code-atlas-capatch-workspace` | Code Atlas CAPATCH workspace | HIGH |
| #23 | DIRTY | false | `main` | `feat/keystone-pitch-tabs-demo` | Keystone pitch | HIGH |
| #16-#22 | CLEAN chain | false | stacked branches | stack-clean series | stack migration chain | HIGH until replay plan exists |

Dependabot PRs:

- #47 `dependabot/github_actions/pnpm/action-setup-6`
- #48 `dependabot/github_actions/actions/checkout-6`
- #49 `dependabot/github_actions/actions/setup-python-6`
- #50 `dependabot/github_actions/actions/upload-artifact-7`

These are separate dependency-update PRs and must not be mixed into PRISMA cleanup.

## Local Branch Observations

Current branch:

- `prisma/launcher-os-quality-phase4`
- Ahead of `origin/main` by 28 commits, behind by 1.
- Has open PR #71.

Safety branch created:

- `safety/prisma-cleanup-20260517-0722`

High-risk old PRISMA branches:

- `prisma/tablet-pos-pages-shell-03`
- `prisma/full-tree-governed-v42`
- `prisma/full-tree-governed-v43`
- `prisma/full-tree-governed-v44`
- `feature/prisma-terminal-runtime-cleanup`
- `feat/prisma-mobile-crystal-command`

Preservation / policy branches:

- `agent-workbench-rescue-20260508_020502_utc`
- `codex/gitignore-restored-untracked-ignore`
- `codex/policy-no-move-no-delete`

## Working Tree Theme Map

Current uncommitted work under `apps/terminal-de-venta-system` groups approximately as:

| Theme | Evidence | Risk |
| --- | --- | --- |
| Round 2 commerce productization | schemas, docs/release/prisma-round2, shared event map, QA audit, smoke aggregator | MEDIUM: coherent and recently validated |
| Round 2.1 product integrity | `verify_prisma_product_integrity.mjs`, product integrity run bundle, workspace lane docs | LOW/MEDIUM: coherent and validated |
| Control Center / Phase 5 | `prisma-control-center/**`, `quality/**`, phase5 runner | HIGH: large dirty lane, separate validation needed |
| Web/EIT product lane | `products/web/app/**` | HIGH: untracked, off-release, dependency policy needs approval |
| Repo cleanup reports | `tools/repo-cleanup/**` | LOW: audit/report only |

## Branch Handling Recommendation

Do not merge or close any open PR until the baseline typecheck blocker is resolved.

Do not branch-split the dirty working tree yet. The tree contains interleaved themes and must be isolated by explicit paths after validation is green.
