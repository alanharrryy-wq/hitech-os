# PRISMA Surface Visual Governor · Next Steps

## Current sane stop point

The system now has:

- Materiality Catalog
- Chart Lab Recipe Export
- PC/Tablet/POS/Checkout/Mobile/Web visual consumers
- Route Budget Enforcer
- Recipe Studio V2
- Surface Runtime Adapter
- Visual Regression Harness
- Documentation Hub

## Recommended next phase

**Phase 3 · Controlled Adoption**

1. Add a CI-like local command that runs Pilot 14/18 checks before visual PRs.
2. Connect Recipe Studio V2 to export candidate recipes into a staging folder.
3. Add manual approval gates before a recipe becomes `latest` for POS/Checkout.
4. Only then consider dynamic runtime application.

## Do not do next

- Do not auto-apply recipe changes to POS.
- Do not move every doc file manually.
- Do not delete evidence ZIPs.
- Do not deploy Chart Lab without rerunning no-leak checks.
