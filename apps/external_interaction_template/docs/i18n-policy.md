# i18n guardrails policy

## Core rule
UI text must be owned deliberately. No visible frontend copy should appear as an accidental inline string.

## Feature order of operations
1. Decide ownership.
   - Is this local copy?
   - Is this schema-driven content?
   - Is this actual state?
   - Is this backend evidence?
2. Put local copy under a clear namespace.
3. Do not place visible strings directly in JSX.
4. Use centralized enum display maps for states, roles, and statuses.
5. Declare the schema language contract explicitly.
6. Add minimum validation for locale switching and mixed-language regressions.

## Project rules
- Frontend-owned copy enters bilingual from day one.
- States and statuses use centralized label maps, not per-view improvisation.
- Dynamic schema content must choose a contract: `frontend-owned`, `source-language`, or `bilingual-data`.
- Backend evidence and raw errors stay as raw evidence unless a product decision says otherwise.

## Tooling
- `tools/enforce_i18n_guardrails.py` fails fast on message parity, placeholder drift, bad namespaces, and visible inline copy.
- `tools/i18n_guardrails_baseline.json` tracks current debt so CI only blocks new violations.
- `tools/new_feature_i18n_contract.py` scaffolds a new feature contract, bilingual keys, and a basic test.
