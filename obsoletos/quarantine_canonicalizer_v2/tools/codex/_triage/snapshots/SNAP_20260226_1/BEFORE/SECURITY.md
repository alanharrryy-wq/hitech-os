# SECURITY POLICY

Version: 1.0.0
Last Updated: 2026-02-23

## Scope

Security baseline for the `hitech-os` monorepo.

## Baseline Controls

1. No secrets may be committed to source control.
2. `.env` files remain ignored by default.
3. Feature flags default OFF unless explicitly approved and documented.
4. Local-first deterministic execution is required for baseline validation.
5. External network access is optional and must not be required for core smoke checks.

## Reporting

1. Report security findings through repository maintainers with reproducible steps.
2. Include affected paths, impact, and minimal proof artifact.
3. Propose deterministic remediation and rollback notes.

## Response Discipline

1. Confirm issue scope first, then patch with least-risk change.
2. Add validation evidence (`health`, `lint`, `test`, smoke where relevant).
3. Record temporary exceptions in `docs/NOTEBOOK.md` with expiration.
