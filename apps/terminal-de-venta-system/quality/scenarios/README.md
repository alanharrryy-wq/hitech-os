# PRISMA Scenario Gates

Phase 3 validates operational scenarios without mutating production data.

Scenario rules:

- Do not start services.
- Do not mutate databases.
- Do not require Cloudflare.
- Do not invent evidence.
- Every scenario declares owner, vertical, layer, preconditions, expected evidence and checks.

Scenario status:

- READY: all checks passed and actual evidence exists.
- PARTIAL: some evidence exists but the scenario is not complete.
- MISSING: no usable evidence was found.
