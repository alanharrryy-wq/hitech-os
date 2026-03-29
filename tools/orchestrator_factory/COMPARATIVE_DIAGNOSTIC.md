# Comparative Diagnostic

This document records the design judgment used to unify the two source bundles into one stronger framework.

## 1. What Zip A does well

Zip A is the better constitutional base.

### Strengths preserved
- one governance package explicitly outranks all downstream packages
- package boundaries are crisp and easy to reason about
- path ownership, dependency order, and handoff discipline are front-and-center
- merge behavior is governed instead of improvised
- insert-only and wiring-only policies are realistic and useful for bounded execution
- package-local prompts reinforce scope discipline
- freeze levels and cross-package contract flow are already present
- the package folders are lightweight enough to launch quickly

### Why this matters
Zip A already solves the most dangerous multi-chat failure mode: multiple chats behaving like multiple architects. That constitutional instinct is the right backbone.

## 2. What Zip B does well

Zip B is the better tactical donor.

### Tactical strengths extracted
- deterministic zip bundle contract
- path-policy-driven worker isolation
- generated work packets
- generated prompts
- round-based coordination
- validation pipeline for bundle structure, ownership, payload integrity, and overlap
- acceptance report generation
- retry prompt generation
- deterministic packaging utilities
- lightweight schemas and tests
- explicit mission-control role

### Why this matters
Zip B turns coordination from narrative into artifacts. That is the missing factory-floor machinery.

## 3. Where Zip A remains dominant

Zip A remains dominant in every area that defines authority.

### Areas where Zip A wins by default
- governance philosophy
- package ownership model
- freeze and handoff logic
- shared contract framing
- dictionary and naming governance
- change budgets and stop conditions
- review and boundary discipline

### Practical consequence
The final framework uses Zip B only as a tactical subsystem subordinate to the constitutional layer. Tactical convenience never outranks governance.

## 4. Exact ideas extracted from Zip B

The following donor mechanisms were kept and generalized:

1. **Rounds inside a larger execution model**
   - Kept, but nested inside a stronger project and run lifecycle.
   - Final form: `project -> run -> round -> package -> artifact`.

2. **Deterministic worker bundles**
   - Kept and generalized.
   - Final form: package bundle contract with manifest, report, summary, and payload.

3. **Path-policy enforcement**
   - Kept and generalized.
   - Final form: active runtime path policies frozen during homologation and interpreted per round.

4. **Generated work packets**
   - Kept and generalized.
   - Final form: package work packets derived from constitutional and project-level artifacts.

5. **Acceptance and overlap reports**
   - Kept and generalized.
   - Final form: package-scoped validation, overlap detection, acceptance evaluation, and integration readiness summary.

6. **Retry loops**
   - Kept and generalized.
   - Final form: package-only retry prompts based on acceptance outputs.

7. **Mission-control mechanics**
   - Kept, but collapsed into the governance chat by default to fit the target 1+6 operating model.

8. **Tooling and tests**
   - Kept conceptually and rewritten into a universal execution tooling folder.

## 5. Which exact parts of Zip B remain tactical-only and do not govern

These ideas were intentionally downgraded to tactical or optional reference material only:

- the fixed lane taxonomy (`lane-01-landing`, `lane-02-portal-shell`, etc.)
- the repo target shape centered on `apps/site`, `apps/portal`, `packages/ui`, `services/api`
- the assumption that one specific package owns contracts and fixtures by default
- the idea that mission control must be a separate dedicated chat
- donor assumptions about `apps/web` as a legacy source zone
- repo-specific forbidden roots and Cloudflare-adjacent implementation bias
- mixed-language documentation surface as a default operating language

These were useful as patterns, not as constitution.

## 6. What was deleted, merged, generalized, or rewritten

### Deleted
- company-specific vocabulary as constitutional language
- Cloudflare as a constitutional platform assumption
- portal and landing terminology as default package authority
- lane-specific repo ownership as universal truth

### Merged
- Zip A governance plus Zip B mission control into a single default governance-plus-mission-control chat
- Zip A package structure plus Zip B worker-bundle mechanics into a package-based round system
- Zip A freeze logic plus Zip B acceptance artifacts into a unified run lifecycle

### Generalized
- security/auth/tenant -> identity, access, and trust
- data/bitacora/persistence -> domain, data, and persistence
- API contracts/service wiring -> service contracts and orchestration
- frontend/portal/client state -> experience, clients, and interactions
- Cloudflare infra/deployment -> platform, infrastructure, and delivery
- QA/release/operations -> quality, release, and operations

### Rewritten because neither source was strong enough alone
- run ID standard
- project ID and traceability model
- idea intake and homologation
- canonical source rules
- documentation layering
- decision logging
- review model
- conflict resolution and escalation
- starter-kit packaging
- inner reusable starter zip
- universal prompt usage model

## Bottom line

- **Zip A supplied the constitution.**
- **Zip B supplied the factory tooling.**
- The final bundle deliberately protects that hierarchy.
