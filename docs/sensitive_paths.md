# Sensitive Paths Governance

This policy-facing document maps sensitive paths to review expectations.

## Sensitive path classes
- CI and governance automation:
  - `F:\repos\hitech-os\.github\workflows\**`
- Runtime/back-end and contracts:
  - `F:\repos\hitech-os\services\**`
  - `F:\repos\hitech-os\packages\contracts\**`
  - `F:\repos\hitech-os\apps\keystone\app\api\**`
- Platform and tooling:
  - `F:\repos\hitech-os\tools\codex\**`
  - `F:\repos\hitech-os\tools\graphviz\**`
  - `F:\repos\hitech-os\tools\hos\**`
- Infrastructure and deployment:
  - `F:\repos\hitech-os\terraform\**`
  - `F:\repos\hitech-os\helm\**`
  - `F:\repos\hitech-os\k8s\**`
- Governance policy:
  - `F:\repos\hitech-os\policies\**`

## Guardrails in this pass
- CODEOWNERS now has explicit entries for sensitive prefixes.
- CI security workflow emits non-blocking reports:
  - sensitive path change report
  - secret-sprawl high-confidence scan report
  - CODEOWNERS coverage report

## Secret-sprawl controls
- Keep secret values outside Git (secret manager / CI secrets).
- Commit only secret names and wiring guidance.
- High-confidence secrets regex scan runs in report mode first.

## Privacy boundary note
`docs/knowledge/codex_chats/**` contains high-context exports.
If strict privacy boundaries are required by design, move this domain outside the runtime monorepo surface and treat it as controlled archival storage.
