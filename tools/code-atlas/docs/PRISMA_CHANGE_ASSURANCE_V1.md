# PRISMA Change Assurance V1

Status: `CANONICAL_V1_PRODUCT_CONTRACT`  
Engine: `Code Atlas`  
Principle: **No evidence. No green.**  
Tagline: **Know what can change. Control what does. Prove the result.**

## 1. Permanent identity

The permanent product name is **PRISMA Change Assurance**. `Code Atlas` is the engine name. The previous product name, **PRISMA Change Intelligence**, is deprecated and may remain only where it is explicitly classified as compatibility or immutable historical evidence.

The stable machine registry path remains `PRISMA Factory Ledger/PRISMA_CHANGE_INTELLIGENCE_CAPABILITY_MAP.json` in this migration wave as `COMPAT_ALIAS_KEEP`. The file content is the canonical Change Assurance V2 registry. This preserves automation and avoids a second source of truth.

Machine contract: `tools/code-atlas/CODE_ATLAS_CHANGE_ASSURANCE_CONTRACT.json`.

## 2. Six stages

1. `UNDERSTAND` — establish bounded repository reality and provenance.
2. `RESOLVE` — resolve targets, impact and explicit unknowns.
3. `AUTHORIZE` — resolve authority, conflicts and protected boundaries before mutation.
4. `OBSERVE` — compare and observe change against locked snapshots/provenance.
5. `VERIFY` — evaluate evidence through agent-neutral verification contracts.
6. `PROVE` — package reproducible evidence, limitations and utility measurements.

These stage names are frozen by the machine contract and registry.

## 3. V1 Definition of Done

The canonical live status for every item lives in the single capability registry. The contract below defines meaning, not a second checklist database.

| ID | Stage | Definition of Done | Current governed status |
|---|---|---|---|
| A | UNDERSTAND | Universal bounded repository understanding | `PARTIAL` |
| B | RESOLVE | Useful Impact Radius | `PARTIAL` |
| C | UNDERSTAND | Edge provenance | `PARTIAL` |
| D | RESOLVE | Better UNKNOWN | `PARTIAL` |
| E | AUTHORIZE | Conflict-first authority | `PARTIAL` |
| F | OBSERVE | Change comparison | `DONE` |
| G | VERIFY | Agent-neutral independent verification | `PARTIAL` |
| H | PROVE | Portable reproducible runner | `PARTIAL` |
| I | PROVE | Evidence Bundle | `PARTIAL` |
| J | PROVE | Utility evidence | `BLOCKED` |

`V1 complete` is therefore **false**. This is intentional.

Checklist F is now `DONE / LOCAL_VERIFIED`: `compare_observed_states` produces deterministic added/removed/changed/unchanged deltas from explicit same-repository snapshot lineage and bounded caller-supplied evidence. Code Atlas Operational Hardening run `32337152354` passed on Ubuntu, Windows and macOS; Ubuntu reported `139/139` tests PASS, including all 12 focused OBSERVE comparison tests. Partial, stale, conflicted, inferred, missing-evidence, cross-repository and malformed lineage cases remain fail-closed. F does not authorize mutation and does not prove universal, production, enterprise or paid-pilot readiness. A V1 item becomes `DONE` only when its registry row carries evidence, positive tests and native negative tests. Missing external evidence stays blocked instead of being painted green with a roller from the tianguis.

Allowed V1 statuses are `DONE`, `PARTIAL`, `MISSING`, `BLOCKED`, `NOT_REQUIRED_V1`, and `EXPERIMENTAL`.

## 4. Hard invariants

- `Candidate != Authority`
- `Impact Radius != Authorization`
- `Retrieval != proof`
- `UNKNOWN != PASS_WITH_WARNING`
- Proof-bearing claims require snapshot/provenance locking.
- Verification must be agent-neutral. Same-agent assertion is not independent verification.

`UNKNOWN` is a valid result. When critical evidence is absent, stale, contradictory, unsupported or incomplete, the system must remain `UNKNOWN`, `BLOCKED`, or `NOT_EVALUATED` as appropriate.

## 5. Evidence and claim boundary

Current source and historical evidence supports bounded capabilities only. It does **not** by itself prove:

- universal repository understanding across arbitrary stacks;
- production certification;
- enterprise readiness;
- paid-pilot readiness;
- complete dynamic/runtime impact discovery;
- external human usefulness;
- successful independent-agent replication.

A retrieval hit is discovery, not proof. An impact set is analysis, not authorization. A candidate owner is evidence to resolve, not authority to invent.

## 6. Legacy rename policy

Every occurrence of the deprecated product name must be classified before change:

- `PUBLIC_IDENTITY_RENAME`
- `CANONICAL_DOC_RENAME`
- `MACHINE_CONTRACT_RENAME`
- `INTERNAL_SYMBOL_MIGRATE`
- `COMPAT_ALIAS_KEEP`
- `HISTORICAL_EVIDENCE_KEEP`
- `FALSE_POSITIVE`

New public identity use is forbidden. Existing PRs, issue comments, immutable evidence bundles and historical artifacts remain `HISTORICAL_EVIDENCE_KEEP`; they are not rewritten to manufacture a cleaner past. Stable filenames, import paths or persisted identifiers remain `COMPAT_ALIAS_KEEP` until a separately governed compatibility-safe migration proves they can move without breaking consumers.

## 7. Native negative-test doctrine

The V1 gate must treat failure paths as product behavior, not decorative QA. Representative scenarios include:

- allowed target versus outside-scope target;
- protected target;
- missing critical evidence;
- stale snapshot or authority drift;
- unknown target;
- new/untracked path;
- dirty or partial evidence state;
- unsupported parser/source family;
- missing companion evidence;
- legacy public-name reintroduction;
- missing stage;
- `DONE` without evidence/tests/negative tests;
- unauthorized claim;
- `UNKNOWN` promoted to PASS or `PASS_WITH_WARNING`.

## 8. Anti-rework rule

Universal Intelligence and Customer Wow foundations already recorded as mature or verify-only remain reuse/advance work. `doNotRebuild=true` is binding. This V1 contract adds identity, evidence boundaries and a governed completion checklist; it does not authorize a parallel repository engine, graph engine, authority engine, verification engine, evidence engine, runner, or Cloud Center surface.

## 9. Authority provenance for this migration

This contract was authorized read-only against repository head `45762d1a6251195dae0e229dfe6fa1aed74645fa` and tree `ce37544fb6f431586bc5f472124c0d6a3bc1c2a8` by PRISMA Remote AutoMesh run `32332472480`, artifact `9393519072`, request digest `81bf9492592090b52cc2a07b0138aa09454a423b7eca07abac9f65b1ab2798e7`, with 100% required-authority coverage and zero blockers.

This provenance authorizes the bounded governance files in that exact task. It does not certify production, runtime, paid-pilot, Cloud Center, Tablet, PC, Mobile, Chart Lab, Shared UI, database or Prisma behavior.
