# Constitution Activation Plan v1 (DRAFT → ACTIVE)

This plan keeps governance **OFF by default** until the constitution is approved.

## Stage 0 — DRAFT (current)
- Tables exist as JSON contracts
- Validator works locally
- CI enforcement is OFF

**Exit criteria:**
- Constitution v1 text approved
- Table registry approved
- Table schema approved

## Stage 1 — ACTIVE (non-blocking)
- `status` changes from `draft` → `active`
- `authority_level` remains `warning` or `informational`
- CI may run validator but does not block merges (report-only)

**Exit criteria:**
- Keystone pilot uses the tables
- No major drift detected for 2–4 weeks

## Stage 2 — ENFORCED (selective)
- Promote *one* table at a time to `authority_level: enforced`
- Introduce deprecation notices first
- Add codemods for migrations

**Exit criteria:**
- Consistent compliance and low friction

## Stage 3 — ENFORCED (broad)
- Expand enforcement carefully (never all at once)
- Keep escape hatch for emergencies (documented)

## Safety Principles
- Never block without a clear migration path
- Prefer codemods over manual fixes
- Reduce friction before increasing strictness
