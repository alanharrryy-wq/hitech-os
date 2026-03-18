# Golden Path (Monorepo Hardening)

This is the default local workflow for deterministic development and CI parity.

## Prerequisites
- Node `>=20 <26`
- pnpm `>=9 <10`
- Python `3.11+`

## Install
```powershell
pnpm run golden:install
```

## Validate (fast governance + boundaries)
```powershell
pnpm run golden:validate
```

This runs:
1. dependency policy validation (`policy:deps:validate`)
2. policy-driven boundary validation (`workspace:validate`)
3. dependency hygiene checks (`deps:check`)
4. affected/ownership reports
5. no-new-cycles check
6. release discipline report
7. sensitive-path + secret-sprawl report
8. repo hygiene report
9. Graphviz scoped index + top-risk refresh
10. engineering health summary generation

## Graph entrypoint
```powershell
pnpm run golden:graph
```

Outputs:
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_summary.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\scope_top_risks.json`
- `F:\repos\hitech-os\tools\graphviz\graphs\index.scoped.html`

## CI parity commands
```powershell
pnpm run workspace:validate
pnpm run deps:check
pnpm run guardrails:cycles
pnpm run guardrails:release
pnpm run guardrails:sensitive
pnpm run guardrails:repo-hygiene
pnpm run engineering-health:collect
```

## Keystone runner policy
Do not start framework servers directly.
Use:
```powershell
pnpm -C apps/keystone keystone:scene:studio
```
