# Code Atlas Customer Wow V1

Status: `CONSUMER_CONTRACT_SOURCE_DESIGN`

Authority basis:

- task-exact PRISMA Remote AutoMesh request `21dd25667cc8f5dd`
- workflow run `31816725320`
- artifact `prisma-automesh-21dd25667cc8f5dd-31816725320-1`
- artifact digest `sha256:2c06fd785fdf137a647a13dbb7122707b9f2a9aaca1cc2d19595da3cc063a285`
- authority HEAD `ab0b1b966d1d4f34525bdf571e7652df557f1a2a`
- Mesh result: PASS, repo drift stable, provenance verified

This document freezes the customer-facing consumer contract while the neutral Universal Intelligence Core is being evolved separately. It deliberately avoids implementing or duplicating discovery, authority resolution, graphs, snapshotting or indexing. Customer Wow consumes those capabilities through neutral evidence-bearing interfaces once they are available.

`certifiable=false` and `productionCertified=false` remain invariant.

## 1. Product goal

Turn Code Atlas from a collection of powerful repository-analysis capabilities into one auditable customer loop:

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

The customer buys the ability to understand and govern a change. The customer does not need access to Code Atlas internal motors or PRISMA-specific governance.

## 2. Non-overlap rule

Customer Wow MUST NOT rebuild the Universal Intelligence Core.

The following belong below this layer and are consumed rather than reimplemented:

- repository discovery;
- authority discovery/resolution;
- dependency, ownership, evidence and architecture graphs;
- repository snapshot and commit/tree locking;
- universal index/query substrate;
- drift detection;
- physical and semantic evidence resolution;
- profile loading and neutral repository understanding.

If another branch introduces a canonical implementation for any of these, Customer Wow adapts to it. It does not fork or duplicate it.

## 3. Hard invariants

1. **Evidence before green.** No unsupported `PASS`.
2. **Retrieval is not proof.** Search, embeddings or LLM retrieval may locate evidence but cannot upgrade it to authority.
3. **Profiles add expectations, not facts.** A customer policy/profile may require an authority but may not claim it exists.
4. **Derived indexes are disposable.** SQLite/search indexes are projections and never the source of truth.
5. **Commit locked.** Every decision and portable pack records repository identity, commit/tree identity, profile version and evidence provenance.
6. **Material drift expires decisions.** Changed authorities, schemas, policies, gates or relevant graph edges invalidate stale packs unless a governed refresh proves compatibility.
7. **Agent neutral.** Packs and verification work for human developers and arbitrary coding agents.
8. **Read-only by default.** Analysis does not write to customer source, Git, databases, processes, ports or deployments.
9. **Secrets remain secret.** Sensitive-path discovery may record existence/classification but must not require ingesting secret values.
10. **Explainability is mandatory.** Every target, protected path, requirement and decision exposes why it exists and which evidence supports it.
11. **Unknown stays unknown.** Missing/contradictory evidence becomes `UNKNOWN` or `BLOCKED`, never inferred green.
12. **PRISMA is an adapter.** PRISMA-specific Factory Ledger, AutoMesh, NDC, surfaces and gates remain opt-in product semantics, not neutral assumptions.

## 4. Customer-facing capabilities

### 4.1 Change Studio

Input:

- natural-language or structured change request;
- repository snapshot identity;
- optional customer policy/profile;
- optional nominated targets or constraints.

Output MUST include:

- normalized change intent;
- primary targets;
- related/secondary targets;
- impact radius;
- protected/do-not-touch scope;
- owners/authority references when supported;
- known facts;
- inferences clearly marked as inferences;
- unknowns;
- contradictions;
- required evidence/tests/gates;
- readiness decision: `PASS | BLOCKED | UNKNOWN`;
- explicit `doesNotProve` boundary.

A Change Studio result without evidence provenance is invalid.

### 4.2 Agent Authority Pack

Portable instruction artifact for a human or coding agent.

Minimum fields:

- `packId`;
- repository identity;
- exact commit/tree identity;
- request digest;
- normalized task;
- allowed files/directories/scopes;
- protected files/directories/scopes;
- required checks;
- required evidence;
- forbidden operations;
- stop conditions;
- unresolved unknowns;
- authority/evidence references;
- tool/profile/schema versions;
- generated timestamp;
- canonical checksum.

A pack MUST fail closed if its repository state is stale or required authorities are unresolved.

### 4.3 Verify Agent

Input:

- original Agent Authority Pack;
- actual diff/change manifest and, when available, agent-session evidence;
- current repository snapshot;
- produced test/CI/evidence results.

Checks:

- exact pack/repo compatibility;
- stale snapshot/drift;
- actual changes inside allowed scope;
- protected scope untouched unless separately authorized;
- required checks executed;
- evidence complete and current;
- contradictions and newly introduced unknowns;
- unrequested changes;
- result provenance.

Output:

- `PASS`, `BLOCKED` or `UNKNOWN`;
- per-file/per-scope compliance;
- missing evidence;
- out-of-scope mutations;
- protected-boundary violations;
- stale authority/drift findings;
- `doesNotProve` statement;
- portable verification report.

### 4.4 Evidence Q&A

Customer asks questions such as:

- Who appears to own authentication?
- What depends on pricing?
- Which tests support checkout?
- Which authority changed since the previous snapshot?

Every answer MUST separate:

- answer/claim;
- support level;
- evidence references;
- inference, if any;
- contradictions;
- confidence basis;
- `doesNotProve`.

No answer may cite semantic similarity alone as proof.

### 4.5 Customer Policy Packs

A policy pack may declare customer expectations such as:

- protected paths;
- required authorities;
- required tests/reviews;
- forbidden operations;
- maximum acceptable impact/risk thresholds;
- security/privacy handling rules;
- domain-specific evidence requirements.

Policy packs MUST be versioned and explicit. They do not mutate the neutral core and do not become evidence merely because the customer configured them.

### 4.6 Architecture Delta

Compare two governed snapshots and explain material changes in:

- applications/services/packages;
- architecture layers;
- dependency edges;
- data/schema relationships;
- authority/ownership;
- CI/test gates;
- protected/sensitive scope;
- unknown/contradictory areas.

Output distinguishes `added`, `removed`, `changed`, `stale`, `unknown` and `unchanged`.

### 4.7 Evidence Connectors

Adapters consume external evidence without rebuilding the external tool.

Initial neutral connector classes:

- Git/PR/diff metadata;
- GitHub Actions-style CI results;
- SARIF;
- JUnit-compatible test results;
- coverage summaries;
- CODEOWNERS-style ownership;
- generic build/test command evidence.

Future connectors may include Sonar, Semgrep or other customer tools, but external tool output remains evidence with provenance, not automatic authority.

### 4.8 Agent Session Intelligence

When session information is available, record:

- requested task;
- authority pack used;
- agent/tool identity as declared by the evidence source;
- files inspected/changed;
- allowed vs out-of-scope changes;
- checks requested/executed;
- evidence completeness;
- human interventions;
- result.

Do not infer hidden agent reasoning.

### 4.9 ROI instrumentation

Measure operational outcomes without fabricating monetary value.

Raw metrics may include:

- context discovery time;
- change-scope identification time;
- human supervision time;
- out-of-scope change rate;
- reopened-work rate;
- evidence assembly time;
- change readiness throughput;
- blocked-before-change count;
- evidence completeness rate.

Loaded engineering cost and monetary ROI remain customer-provided or explicitly modeled assumptions. Keep raw observed metrics separate from derived financial estimates.

### 4.10 Customer Runner boundary

Future runner contract:

- executes inside customer-controlled infrastructure;
- least privilege and read-only by default;
- deterministic/redactable outputs;
- no production credentials required by default;
- customer controls what evidence leaves its environment;
- supports local-only mode;
- emits provenance-locked portable bundles.

This document does not claim the runner is production-ready.

## 5. Decision semantics

### PASS

All mandatory scope, authority, freshness and evidence obligations relevant to the requested decision are satisfied.

### BLOCKED

A known mandatory obligation failed, a protected boundary was violated, required evidence is absent, material drift invalidated the pack, or policy explicitly prevents proceeding.

### UNKNOWN

The system lacks sufficient evidence to make the required claim safely, or evidence is contradictory and no governing authority resolves the conflict.

`UNKNOWN` is a valid product result and MUST NOT be silently downgraded to warning-only green.

## 6. Consumer interface required from Universal Intelligence Core

Customer Wow does not prescribe implementation names. It requires semantic capabilities equivalent to:

```text
resolve_repository_snapshot()
resolve_change_targets(change_request, snapshot)
query_authority(domain_or_target, snapshot)
query_dependencies(targets, snapshot)
query_ownership(targets, snapshot)
query_protected_scope(targets, profile, snapshot)
query_evidence(requirement_or_claim, snapshot)
compare_snapshots(base, head)
validate_snapshot_freshness(snapshot)
explain_selection(entity_or_evidence)
```

Each response must be evidence-bearing and distinguish fact/inference/unknown/conflict. Binding to actual Universal Core APIs occurs only after the canonical implementation lands.

## 7. Compatibility with existing Code Atlas capability baseline

Customer Wow is a composition layer. It should preferentially consume existing hardened capabilities including, where applicable:

- Impact Radius Calculator;
- Ownership Map;
- Do Not Touch Map;
- Safe Scope Guard;
- Evidence Confidence Score;
- verifier/release readiness evidence;
- Atlas Query / Entity Detail foundations;
- snapshot/diff and staleness foundations;
- Evidence Bundle Index / Manifest Plus;
- secret exposure and PII/privacy handling;
- machine continuation/provenance.

Legacy registry labels are not certification. Existing source must be reconciled through current hardened contracts before reuse.

## 8. Negative-test minimum

Customer Wow implementation is incomplete without tests that prove fail-closed behavior for at least:

- stale commit/tree;
- changed authority after pack generation;
- missing required authority;
- out-of-scope modified file;
- protected file mutation;
- missing required test evidence;
- contradictory evidence;
- semantic-search result with no supporting evidence;
- customer policy requiring nonexistent source;
- path traversal / unsafe path;
- spaces, Unicode and long paths;
- malformed external connector payload;
- SARIF/JUnit/coverage evidence with stale provenance;
- secret-value ingestion attempt;
- unknown/unsupported repository profile;
- cross-repository evidence contamination;
- agent session not matching the authority pack;
- changed tool/profile/schema version that invalidates compatibility.

## 9. Cross-platform requirement

Customer-facing neutral code must preserve the current neutrality boundary and remain portable across Linux, Windows and macOS. It must not assume drive letters, developer homes, fixed ports or PRISMA product names.

## 10. Parallel-development rule

Until the Universal Intelligence Core branch lands:

- Customer Wow may create new contracts, schemas, pure consumer modules and isolated tests that do not duplicate the Universal Core.
- It must not edit the other branch, move its ref or predict private implementation details.
- Integration bindings remain adapters/interfaces until the canonical neutral core is available.
- Before final integration, re-run a fresh task-exact Authority Mesh against the then-current `main` and reconcile drift.

## 11. Definition of Customer Wow V1

The first commercially meaningful loop is complete only when a neutral external repository can demonstrate, with evidence:

1. analyze a bounded real change request;
2. show target, impact, protected scope, unknowns and required evidence;
3. export a portable Agent Authority Pack;
4. evaluate an actual diff/session against that pack;
5. fail closed on scope/evidence/drift violations;
6. emit a human-readable and machine-readable Evidence Report;
7. record ROI raw metrics without fabricating economic claims;
8. preserve source privacy and neutrality constraints.

Everything beyond this loop is secondary until the loop is demonstrated on unrelated external repositories.
