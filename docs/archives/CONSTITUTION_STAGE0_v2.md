# CONSTITUTION — STAGE 0 (S0\_\*)

Version: 2.0.0
Status: Active
Last Updated: 2026-02-23
Scope: Entire monorepo (`hitech-os`)
Authority Tier: Supreme (Interpretation)
Enforced By: `docs/CONTRACT.md` (execution), tools/gates (verification)

> Stage 0 does not unlock features.
> Stage 0 unlocks governability.

This Constitution defines intent, meaning, and authority boundaries.
`docs/CONTRACT.md` defines enforcement, execution rules, and operational constraints.
If ambiguity exists, this Constitution resolves intent; the Contract resolves enforcement.

---

## PREAMBLE (Imperial, but binding)

This repository is governed, not improvised.

We optimize for:

- determinism over convenience,
- evidence over assumption,
- explicit contracts over implicit coupling,
- modular boundaries over tangled shortcuts.

No silent passes.
No undocumented exceptions.
If it is not in the output, it did not happen.

---

## GOVERNANCE PRIMITIVES (Binding Definitions)

- **Intent**: the meaning of a rule (why it exists).
- **Enforcement**: the executable mechanism that makes a rule unavoidable (how it is applied).
- **Determinism**: same inputs → same outputs; stable ordering; no machine-specific leakage.
- **Evidence**: required output artifacts proving a claim (“ran”, “passed”, “valid”).
- **Debt**: explicit, scoped, time-bounded allowance; never silent; must be recorded.
- **Blocker**: must-fix before a run/merge is considered valid.
- **Root Authority**: contracts/schemas/blueprints that define truth.
- **Non-root Output**: logs/reports requiring verification; cannot override roots.
- **Stage**: an unlock tier. Later stages cannot weaken Stage 0 intent.

---

## INTERPRETATION RULES (How to decide disputes)

1. **Contract wins on execution**  
   If the Contract specifies an enforcement behavior, it is authoritative for execution.

2. **Constitution wins on meaning**  
   If a rule is unclear, interpret it using Stage 0 intent (this document).

3. **No “text-only law”**  
   A rule that cannot be enforced is still binding, but must be scheduled for enforcement.
   Until enforced, any violation must surface as Evidence + Debt (never silent).

4. **Expected failure is not Debt**  
   If a preflight fails as expected and no swap/run was attempted and no files changed:
   do not manufacture Debt. Report INFO only. (Truth ≠ drama.)

5. **Exceptions are constitutional events**  
   Any exception requires:
   - scope
   - reason
   - expiration date
   - rollback plan
     recorded in `docs/NOTEBOOK.md`.

---

## AMENDMENTS (Change Discipline)

A constitutional change must include:

1. intent update here (this file),
2. enforcement update in `docs/CONTRACT.md` and/or tools/gates,
3. proof in output (diffs/reports/gates).

No “policy-only” changes without an enforcement plan.
No silent behavior changes.

---

# STAGE 0 — GLOBAL CONSTITUTION (S0\_\*)

Stage 0 is the root of all governance. No later stage may weaken it.

Each Tech Node below defines:

- Intent (why)
- Meaning (what it implies)
- Binding interpretation (how to reason about it)
- Contract anchor (where enforcement lives)

---

## S0_ORIG — Constitutional Origin

**Intent**
Declare this repo as a governed system (not a pile of scripts).

**Meaning**

- Authority must be explicit.
- Decisions must be justifiable by law, not preference.
- If a local workflow conflicts with the Contract, the Contract wins.

**Binding Interpretation**

- “Because it works” is not an argument.
- Any new rule must anchor to Stage 0 intent.
- Any new behavior must have an evidence path.

**Contract Anchor**

- `docs/CONTRACT.md` → header authority + Stage 0 entry

---

## S0_DET — Determinism Law

**Intent**
Make the system replayable, auditable, and stable across machines.

**Meaning**

- Same input payload must yield the same committed artifacts and CI outputs.
- Ordering must be stable (files, keys, lists).
- No leakage of machine-specific absolute paths into committed outputs.
- Time/randomness are illegal unless explicitly injected as input.

**Binding Interpretation**

- Determinism is a requirement, not an optimization.
- Any nondeterministic output must be treated as failure (or explicit Debt if temporarily allowed).

**Contract Anchor**

- `docs/CONTRACT.md` → S0_DET (Design Axioms) + S0_LEX (Determinism Requirements)

---

## S0_PRI — Enforcement Priority

**Intent**
Prevent “document civil wars” by defining an authority ladder and boundary logic.

**Meaning**
Authority order (highest to lowest):

1. `docs/CONTRACT.md`
2. code-level tests and health scripts
3. README guidance
4. local preferences

**Binding Interpretation**

- Conflicts must be resolved deterministically by authority tier.
- If two artifacts disagree, the higher-tier artifact governs.

**Contract Anchor**

- `docs/CONTRACT.md` → S0_PRI (Boundary Law) + S2_DEF (priority restatement)

---

## S0_LEX — Blueprint as Law Doctrine

**Intent**
Ensure “law” is executable, not decorative text.

**Meaning**

- If a rule is not enforceable (schema/gate/tool), it does not fully govern execution yet.
- Documentation without enforcement is non-authoritative for execution.

**Binding Interpretation**

- Blueprints must be designed to become gates.
- The repo must prefer enforceable contracts over interpretive prose.

**Contract Anchor**

- `docs/CONTRACT.md` → S0_LEX (Required/Forbidden determinism behaviors)

---

## S0_PROOF — Evidence Doctrine

**Intent**
“If it’s not in the output, it didn’t happen.”

**Meaning**

- Claims require proof artifacts.
- Proof must be stable, reviewable, and rooted.
- Feature flags are governance primitives: default OFF; explicit rollout/rollback.

**Binding Interpretation**

- Evidence defines reality for governance.
- Non-root outputs cannot override root authority.
- Flag additions require explicit ownership and documentation.

**Contract Anchor**

- `docs/CONTRACT.md` → S0_PROOF (Feature Flags Policy)

---

## S0_NSP — No Silent Pass Rule

**Intent**
Eliminate invisible failure and self-deception.

**Meaning**

- WARN must never be silent.
- WARN must always create explicit Debt, unless it is an expected preflight fail with no-op behavior.
- Source trees are code-only; dump artifacts are forbidden.

**Binding Interpretation**

- If a run “sort of passed”, it did not pass.
- If a warning exists, it must be tracked or the run is invalid.
- Expected failure must not generate fake Debt (INFO-only).

**Contract Anchor**

- `docs/CONTRACT.md` → S0_NSP (Artifact/Dump Prohibition) + tooling enforcement (`tools/health`)
- SAFE_SWAP scripts must follow “expected failure ≠ debt” discipline.

---

## S0_TRUST — Trusted Roots Definition

**Intent**
Define what is authoritative and what must be verified.

**Meaning**
Root authorities include:

- canonical contracts/schemas
- committed deterministic generated schemas
- blueprint law and gate definitions

Non-root outputs include:

- logs and worker reports without attestation

**Binding Interpretation**

- `packages/contracts` is canonical for shared shapes.
- Generated schemas are committed and deterministic.
- Python models must align to canonical shape and enums.
- Runtime services must validate against local rules.

**Contract Anchor**

- `docs/CONTRACT.md` → S0_TRUST (Contracts and Schema Authority + change flow)

---

## STAGE 0 OUTCOME

When Stage 0 is complete:

- Authority is defined.
- Determinism is required.
- Evidence is mandatory.
- Silent pass is impossible.
- Trust boundaries are explicit.

You still don’t have an empire.
You have rule of law.

---

## TRANSITION NOTE (Non-binding guidance)

Stage 1 builds minimal infrastructure (health, smoke, output minimum).
Stage 2 introduces non-regression, overlap enforcement, and drift detection.
But no stage may weaken Stage 0.
