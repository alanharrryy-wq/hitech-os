# Code Atlas Customer Wow V1

Status: `UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED_EXTERNAL_REPO_EVIDENCE_PENDING`

Authority basis:

- fresh task-exact Remote AutoMesh request `8d8cbd595e9da7ab`
- workflow run `31837217415`
- artifact `prisma-automesh-8d8cbd595e9da7ab-31837217415-1`
- artifact digest `sha256:ec23c953cc9d3b42a7c3403e3701e25a279a89f79e77e6b0af3fc6ef32967acb`
- authority HEAD `2889cc3a6581b4c91adc3a9b7cc626d78756ed64`
- Mesh result `PASS_COMPOSED_AUTHORITY_MESH`
- required authority coverage: 7 / 7 in both lanes, 0 missing
- repository drift stable; provenance verified
- Universal Intelligence PR #270 merge commit `83a83bf50691e866d31465993d7145e033fb2cc0`

Customer Wow V1 is now bound to the canonical neutral Universal Intelligence Core. The binding consumes repository inventory, authority discovery, system graphs, portable snapshots, coverage and retrieval through a structured neutral API. It does not duplicate discovery, graphing, indexing, snapshot or drift primitives.

`certifiable=false` and `productionCertified=false` remain invariant.

## 1. Product goal

Turn Code Atlas repository intelligence into one auditable customer loop:

```text
CHANGE REQUEST
      |
      v
CHANGE STUDIO
      |
      v
EVIDENCE-SUPPORTED CHANGE MODEL
 target / scope / impact / protected / unknowns / required evidence
      |
      v
AGENT AUTHORITY PACK
      |
      v
HUMAN OR ANY CODING AGENT
      |
      v
ACTUAL DIFF / SESSION EVIDENCE
      |
      v
VERIFY AGENT
      |
      v
PASS / BLOCKED / UNKNOWN
      |
      v
EVIDENCE REPORT + ROI SIGNALS + CONTINUATION
```

The customer buys the ability to understand and govern a change. The customer does not need access to internal motors or product-specific governance.

## 2. Canonical layering

### Universal Intelligence Core

Owned by `code_atlas.intelligence` and reused rather than rebuilt:

- repository discovery;
- authority discovery and resolution;
- dependency, ownership, evidence and architecture graphs;
- static change impact;
- repository snapshot and commit/tree locking;
- universal index/query substrate;
- semantic retrieval;
- drift/freshness primitives;
- profile loading and neutral repository understanding.

### Customer Wow / Change Intelligence

Owned by `code_atlas.change_intelligence`:

- Change Studio composition;
- Agent Authority Pack;
- verification of actual changed paths and evidence;
- customer Policy Packs;
- evidence-backed Q&A;
- Architecture Delta;
- external evidence connectors/parsers;
- Agent Session evidence;
- Customer Runner contracts;
- Evidence Reports and portable bundles;
- ROI raw-event instrumentation.

The binding entry points are:

- `code_atlas.intelligence.resolve_intelligence_context(...)`
- `code_atlas.change_intelligence.prepare_change(...)`
- `code_atlas.change_intelligence.verify_prepared_change(...)`

## 3. Hard invariants

1. **Evidence before green.** No unsupported `PASS`.
2. **Retrieval is not proof.** Search or semantic retrieval locates evidence but cannot promote it to authority.
3. **Profiles and policies add expectations, not facts.**
4. **Derived indexes are disposable projections, never authority.**
5. **Authority Packs are repository/commit/tree locked.**
6. **Authority, policy and evidence compatibility drift fails closed.**
7. **Impact Radius informs, never authorizes.** An impacted file is not automatically editable.
8. **Targets are never guessed.** A pack requires explicitly nominated targets supported by repository evidence. Missing target evidence produces `UNKNOWN`/`BLOCKED`, not an invented target.
9. **Allowed scope is explicit.** It consists only of nominated targets plus explicitly supplied additional scope.
10. **Protected scope remains authoritative over a broadened allowed scope.**
11. **Agent neutral.** Packs and verification apply to humans and arbitrary coding agents.
12. **Read-only analysis by default.** No customer-source, Git, DB, process, port or deploy mutation is required for analysis.
13. **Secrets remain secret.** Sensitive-path discovery does not require secret-value ingestion.
14. **Explainability is mandatory.** Targets, authorities, blockers and decisions carry provenance/reasons.
15. **Unknown remains unknown.** Missing or contradictory evidence never becomes warning-only green.
16. **Product semantics are explicit adapters.** PRISMA-specific governance remains opt-in.

## 4. Evidence compatibility rule

A legitimate change to an explicitly authorized target must not invalidate its own pack merely because that target also appears in the evidence graph.

Customer Wow therefore locks evidence with this rule:

`LOCK_EVIDENCE_OUTSIDE_EXPLICIT_ALLOWED_SCOPE`

Only the exact `allowedScope` is excluded from the evidence compatibility digest. Evidence drift anywhere outside that scope still causes `COMPATIBILITY_LOCK_MISMATCH` and blocks verification.

This preserves both properties:

- an authorized target can actually be changed;
- unrelated evidence cannot silently drift underneath an existing authority decision.

The verification run also preserves the original task domain so preparation and verification evaluate the same semantic evidence universe.

## 5. Decision semantics

### PASS

All mandatory scope, authority, freshness and evidence obligations represented by the pack are satisfied.

### BLOCKED

A mandatory obligation failed, including missing required authority/evidence, protected mutation, out-of-scope change, stale commit/tree, compatibility drift or a customer policy blocker.

### UNKNOWN

The system lacks sufficient evidence for the requested claim, including the absence of an explicit evidence-supported target.

`UNKNOWN` is a valid product result and must never be silently downgraded to green.

## 6. Implemented Customer Wow surface

The source-ready layer includes:

- fail-closed Change Studio composition;
- portable Agent Authority Pack with deterministic checksum;
- repository/commit/tree and authority/policy/evidence compatibility locks;
- Verify Agent scope, protected-boundary, evidence and session enforcement;
- structured binding to Universal Intelligence;
- evidence-backed Q&A support levels;
- Customer Policy Pack validation;
- Architecture Delta normalization;
- external evidence envelopes;
- JUnit, SARIF, coverage, CODEOWNERS-style ownership and CI parsers;
- Agent Session evidence normalization without hidden-reasoning inference;
- raw ROI events with economic estimates explicitly derived;
- human-readable Change and Verification reports;
- portable evidence bundle manifests;
- Customer Runner `LOCAL_ONLY` and `PORTABLE_EVIDENCE` contracts;
- least-privilege/read-only runner defaults and no source-code egress in V1;
- neutral CLI for pack validation, verification and evidence parsing.

## 7. Verification evidence

The final binding was exercised in a neutral synthetic Git repository rather than relying on PRISMA product semantics.

The operational suite on the final fix ran **106 tests** and passed. It covers both the pre-existing hardening baseline and the new Universal-to-Customer-Wow integration.

New integration coverage includes:

- structured Universal context is public and derived projections remain non-authoritative;
- explicit supported target produces an Authority Pack;
- static impact is visible but does not widen allowed scope;
- no target fails closed without guessing;
- legitimate in-scope worktree target change with required evidence passes;
- evidence drift outside allowed scope blocks;
- authority drift blocks;
- missing required authority blocks;
- new commit expires an exact pack;
- out-of-scope and protected mutations block.

Repository CI evidence on the final integration head:

- Code Atlas Operational Hardening: PASS;
- total neutrality gate: `PASS_CODE_ATLAS_TOTAL_NEUTRALITY`, blocking count 0;
- Ubuntu operational suite: 106 tests, `OK`;
- Windows operational hardening: PASS;
- Windows neutrality/portability: PASS;
- macOS neutrality/portability: PASS;
- CI: PASS;
- Zero Priority Gate: PASS;
- ForgeOS Quality Gate: PASS;
- repo-analyzer-self-test: PASS;
- CLA Check: PASS.

A prior integration run intentionally remains useful evidence: it exposed that an authorized target invalidated its own evidence lock. The correction narrowed the compatibility digest only around explicit allowed scope and added a negative test proving outside-scope evidence drift remains blocking. No fake green was used.

## 8. Customer Runner boundary

V1 supports governed runner contracts for:

- `LOCAL_ONLY`: analysis/evidence stays inside the customer environment;
- `PORTABLE_EVIDENCE`: only an approved non-source evidence bundle may leave the environment.

The runner contract is read-only and least-privilege by default. It does not certify production tenant isolation, hosted execution, enterprise IAM or legal/privacy compliance.

## 9. What this status proves

`UNIVERSAL_CORE_BOUND_LOCAL_VERIFIED_EXTERNAL_REPO_EVIDENCE_PENDING` proves:

- the neutral Customer Wow composition layer is source implemented;
- it is bound to the canonical Universal Intelligence Core rather than duplicating it;
- fail-closed preparation and verification work against a neutral Git fixture;
- the reusable source boundary remains neutral across repository CI platforms;
- protected scope, authority drift, evidence drift, stale commit/tree and missing-evidence cases remain blocking;
- the final source/test integration is locally/CI verified.

## 10. What this status does NOT prove

It does not prove:

- correct behavior across arbitrary real external repositories/stacks;
- production runtime readiness;
- hosted multi-tenant isolation;
- enterprise IAM/security certification;
- customer data-egress certification beyond the runner contract;
- paid-pilot readiness by itself;
- legal/privacy compliance;
- production certification.

No claim such as `productionCertified=true`, `enterprise-ready`, `paid-pilot-certified` or universal external-repo compatibility is authorized by this evidence.

## 11. Next gate

The next allowed gate is **external repository evidence**, not another source rebuild.

Run the complete loop read-only on unrelated external repositories with explicit authorization and record:

1. repository/authority discovery quality;
2. time to a supported change target;
3. Change Studio target/impact/protected/unknown/evidence usefulness;
4. Authority Pack portability;
5. actual diff/session verification;
6. negative scope/drift/evidence behavior;
7. source/privacy boundary behavior;
8. repeatability across machines/stacks;
9. founder/operator intervention required;
10. ROI raw metrics.

Until that evidence exists, Customer Wow V1 remains source/local verified and evidence-gated, not production certified.
