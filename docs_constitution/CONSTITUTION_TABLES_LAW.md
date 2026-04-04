# Constitution — Tables as Law (Appendix)

This appendix defines how **tables become law** in HITECH OS.

## 1) Source of Truth
The canonical representation of each table is its JSON file in:

- `docs/constitution/tables/<TABLE_ID>.json`

Any Markdown-rendered table is **informational only** unless it is derived from the JSON spec.

## 2) Authority
Each table declares an `authority_level`:

- `informational` — advisory; validator reports only
- `warning` — validator returns non-zero only if `--strict` is enabled
- `enforced` — validator returns non-zero by default (CI-blocking when wired)

## 3) Change Policy
Tables must declare `change_policy`. A table update is valid only if:
- version bumps on breaking changes (semver)
- includes migration note (in PR discipline)
- has approvals (process outside this repo can enforce it)

## 4) OFF by Default
Governance enforcement must remain **OFF by default** until the Constitution is approved.

## 5) Validator
The validator enforces:
- JSON Schema validity
- Cross-table invariants (where applicable)

Run:
- `python tools/hos/constitution/validate_tables.py --root .`
