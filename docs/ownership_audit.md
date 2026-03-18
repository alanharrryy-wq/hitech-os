# Ownership Audit - HITECH OS

## Current CODEOWNERS coverage status
CODEOWNERS file:
- `F:\repos\hitech-os\.github\CODEOWNERS`

Current content:
- wildcard fallback owner plus explicit sensitive-path entries:
  - `.github/workflows`
  - `services`
  - `packages/contracts`
  - `apps/keystone/app/api`
  - `tools/codex`
  - `tools/graphviz`
  - `tools/hos`
  - `terraform`
  - `helm`
  - `k8s`
  - `policies`

Measured status (tracked files):
- tracked files: 4414
- owned files: 4414
- unowned files: 0
- coverage: 100%
- distinct owners: 1
- single-owner mode: true

Report source:
- `F:\repos\hitech-os\tools\scripts\report_codeowners_coverage.mjs`
- sample output path:
  - `F:\repos\hitech-os\tools\_local\reports\ci\codeowners_coverage.local.json`

## Unowned paths/packages
- None at file coverage level under current wildcard owner model.

Important caveat:
- 100% wildcard ownership is not equivalent to resilient ownership. It still has bus-factor and review-capacity risk.
- Path precision is improved, but owner concentration risk remains until secondary owners are added.

## Sensitive paths needing mandatory review
The following should require explicit code owner approval with at least one backup reviewer:
1. `F:\repos\hitech-os\.github\workflows\**`
2. `F:\repos\hitech-os\apps\keystone\app\api\**`
3. `F:\repos\hitech-os\services\**`
4. `F:\repos\hitech-os\packages\contracts\**`
5. `F:\repos\hitech-os\tools\codex\**`
6. `F:\repos\hitech-os\tools\graphviz\**`
7. `F:\repos\hitech-os\tools\hos\**`
8. `F:\repos\hitech-os\terraform\**`
9. `F:\repos\hitech-os\helm\**`
10. `F:\repos\hitech-os\k8s\**`
11. `F:\repos\hitech-os\policies\**`

## Secret-sprawl ownership notes
- `F:\repos\hitech-os\docs\security\SECRETS.md` is currently minimal.
- Secret control should be owner-scoped with mandatory review on:
  - CI workflow changes
  - deployment/infra paths
  - runtime contract/API paths

## Minimal CODEOWNERS policy proposal (do not guess people)
Use placeholders until maintainers confirm owners:

```txt
# baseline fallback
* @repo-maintainers

# mandatory governance/infra owners
/.github/workflows/ @ci-owners @repo-maintainers
/services/ @backend-owners @repo-maintainers
/packages/contracts/ @contract-owners @repo-maintainers
/apps/keystone/app/api/ @api-owners @repo-maintainers
/tools/codex/ @platform-owners @repo-maintainers
/tools/graphviz/ @platform-owners @repo-maintainers
/tools/hos/ @platform-owners @repo-maintainers
/terraform/ @infra-owners @repo-maintainers
/helm/ @infra-owners @repo-maintainers
/k8s/ @infra-owners @repo-maintainers
/policies/ @governance-owners @repo-maintainers
```

## Rollout recommendation
1. Phase 1 (soft): generate coverage report in CI artifact only.
2. Phase 2 (enforced): require code owner review for sensitive paths.
3. Phase 2b: require 2 reviewers for selected high-risk paths (`contracts`, `workflows`, `infra`).

## Evidence references
- `F:\repos\hitech-os\.github\CODEOWNERS`
- `F:\repos\hitech-os\tools\scripts\report_codeowners_coverage.mjs`
- `F:\repos\hitech-os\tools\_local\reports\ci\codeowners_coverage.local.json`
