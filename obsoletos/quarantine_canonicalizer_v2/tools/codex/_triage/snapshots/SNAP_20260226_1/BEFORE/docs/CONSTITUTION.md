# CONSTITUTION — HITECH OS (Stage 0–4)

Version: 3.0.0
Status: Active
Last Updated: 2026-02-23
Scope: Entire monorepo (`hitech-os`)
Authority Tier: Supreme (Interpretation)

This document defines intent, meaning, and authority boundaries.
`docs/CONTRACT.md` defines enforcement and execution.
If ambiguity exists: Constitution resolves meaning; Contract resolves execution.

---

## GOVERNANCE AXIOMS (Non-negotiable)

A1. Governance over improvisation.  
A2. Determinism over convenience.  
A3. Evidence over assumption.  
A4. Ownership over anonymity.  
A5. No silent failure.

No Stage may weaken these axioms.

---

## AUTHORITY LADDER (Conflict Resolution)

Highest → lowest:

1. Constitution (intent / meaning)
2. Contract (enforcement rules / IDs / gates)
3. Tests & CI gates (proof)
4. Tooling outputs (reports/logs)
5. Local preferences (never override above)

---

## THE 10 LAWS (Constitutional Laws)

L1 — Law of Primacy  
Constitution defines principles; Contract makes them executable; tests prove; tooling automates; preferences never override.

L2 — Law of No Unreviewed Power  
No sovereign-branch change without review + required checks.

L3 — Law of Ownership  
Critical paths must have explicit owners; owner approval required for changes.

L4 — Law of Audited Escapes  
Exceptions exist, but require second approval + auditable evidence output.

L5 — Law of Determinism  
Same inputs + same config → same outputs. Host leakage is illegal.

L6 — Law of Reproducibility  
Releases must be reproducible byte-a-byte OR provide explicit evidence for deltas.

L7 — Law of Output Evidence  
“If it’s not in the output, it didn’t happen.” Critical steps must emit structured evidence.

L8 — Law of Provenance  
Release artifacts must include verifiable provenance.

L9 — Law of Trust Roots  
Root authority (contracts/keys/layouts) must be explicit; non-root outputs cannot override roots.

L10 — Law of No Silent Pass  
WARN always creates Debt — except declared expected no-op failures.

---

## DEFINITIONS (Binding)

- Determinism: same inputs → same outputs; stable ordering; no host leakage.
- Evidence: required output artifacts proving a claim.
- Debt: explicit allowance with owner + scope + expiration; never silent.
- Expected no-op failure: a declared preflight failure where no swap/run was attempted AND no files changed.
- Root authority: constitutions/contracts/schemas/layouts/keys that define truth.
- Non-root output: logs/reports requiring verification; cannot override roots.

---

# STAGE 0 — GLOBAL CONSTITUTION (S0\_\*)

Stage 0 is the root. It enables governability, not features.

Each node defines:
Intent (why) → Meaning (what) → Binding Rules (how disputes resolve) → Enforcement Hooks (where Contract/tooling must implement).

---

## S0_ORIG — Constitutional Origin

Intent:
Prevent power without legitimacy.

Meaning:

- Sovereign branches require PR + reviews + checks.
- Critical paths require owners.
- Exceptions must be audited.

Binding Rules:

- “Direct push” to sovereign branches is illegal.
- No critical-path change without owner approval.
- Break-glass requires second approval + evidence marker.

Enforcement Hooks:

- Branch protection / rulesets
- CODEOWNERS/OWNERS with “require code owner review”
- Output evidence must record break-glass events

---

## S0_DET — Determinism Law

Intent:
Make the system replayable and auditable.

Meaning:

- Same input must yield same output.
- Ordering must be stable.
- Time/randomness illegal unless injected as input.

Binding Rules:

- Timestamps must be normalized.
- Arrays/sets must be deterministically ordered.
- No absolute path leakage.

Enforcement Hooks:

- Determinism check gates
- Canonical serialization rules

---

## S0_PRI — Enforcement Priority

Intent:
Prevent policy wars and ambiguity.

Meaning:

- Constitution decides meaning; Contract decides execution.
- Every enforceable rule must map to a LAW_ID.

Binding Rules:

- All gates must reference a LAW_ID.
- Conflicts require constitutional amendment.

Enforcement Hooks:

- CI lint for LAW_ID mapping
- Explicit Law references in Contract

---

## S0_LEX — Blueprint as Law

Intent:
Law must be executable.

Meaning:

- Text-only policy does not govern execution.
- Rules must be enforceable or scheduled.

Enforcement Hooks:

- Policy-as-code
- Schema validation gates

---

## S0_PROOF — Evidence Doctrine

Intent:
Reality is defined by output.

Binding Rules:

- Critical jobs must emit OMP output.
- No OMP → invalid run.
- Evidence must be deterministic.

Enforcement Hooks:

- OMP schema validation gate
- Required artifact presence

---

## S0_NSP — No Silent Pass

Intent:
Eliminate invisible failure.

Binding Rules:

- WARN → DEBT (unless expected no-op).
- No dump artifacts in source paths.

Enforcement Hooks:

- Warning parser gate
- Debt ledger enforcement

---

## S0_TRUST — Trusted Roots

Intent:
Define authority boundaries.

Binding Rules:

- Releases require signature + provenance + SBOM.
- Non-root outputs cannot override roots.

Enforcement Hooks:

- Release trust gate
- Progressive P1 → P2+ hardening

---

# HARDENING LEVELS

P1:

- CODEOWNERS
- Determinism gate
- OMP validation
- Basic release trust signals

P2+:

- Policy registry
- in-toto style attestations
- Transparency logging
- Escalation automation

---

## OUTPUT MINIMUM PROTOCOL (OMP)

Each critical job emits ONE deterministic file:

STATUS | REPORT | BLOCKERS | DEBT | NEXT

No variable timestamps.
Implementation details live in CONTRACT.
