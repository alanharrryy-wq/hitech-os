# Code Atlas Customer Wow V1

Status: `PARALLEL_CONSUMER_SLICE_IMPLEMENTED_AWAITING_UNIVERSAL_CORE_BINDING`

Authority basis:

- task-exact Remote AutoMesh request `21dd25667cc8f5dd`
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

The customer buys the ability to understand and govern a change. The customer does not need access to internal motors or product-specific governance.

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
12. **Product semantics are adapters.** Project-specific ledgers, meshes, surfaces and gates remain opt-in semantics, not neutral assumptions.

## 4. Parallel slice implemented on the Customer Wow branch

The following neutral consumer pieces are source-implemented without binding to private Universal Core implementation details:

- fail-closed Change Studio composition over normalized evidence-bearing inputs;
- portable Agent Authority Pack generation and checksum validation;
- repository/commit/tree compatibility and authority/policy/evidence digest locks;
- Verify Agent scope, protected-boundary, evidence, drift and agent-session checks;
- Evidence Q&A support-level validation where retrieval is never proof;
- versioned Customer Policy Pack validation where configuration is not evidence;
- Architecture Delta normalization over two governed snapshots;
- neutral external evidence envelopes;
- parsers for JUnit, SARIF, coverage summaries, CODEOWNERS-style ownership and CI results;
- Agent Session evidence normalization without hidden-reasoning inference;
- raw ROI instrumentation with financial estimates kept explicitly derived;
- human-readable Markdown rendering for Change and Verification reports;
- portable evidence bundle manifest with repository-relative safe artifact names and checksums;
- Customer Runner contract with `LOCAL_ONLY` and `PORTABLE_EVIDENCE` modes, least privilege, mandatory read-only operation and no source-code egress in V1;
- neutral CLI for validating packs, verifying changes and parsing supported evidence formats.

The slice remains a consumer layer. It does not claim that repository discovery, authority resolution, graph generation, snapshot generation or semantic indexing are implemented here.

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

## 7. Compatibility with existing capability baseline

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

## 8. Negative-test baseline

The parallel slice includes fail-closed coverage for:

- stale commit/tree;
- authority digest drift after pack generation;
- missing required authority;
- out-of-scope modified file;
- protected file mutation;
- missing required evidence/checks;
- contradictory evidence;
- semantic result without supporting evidence;
- path traversal / unsafe paths;
- spaces, Unicode and long paths;
- malformed JUnit/CI inputs;
- stale connector provenance;
- secret-value ingestion attempt;
- cross-repository evidence contamination;
- agent session not matching the authority pack;
- incompatible profile version;
- cross-repository architecture delta;
- Customer Runner mutation attempts;
- prohibited egress in `LOCAL_ONLY` mode.

The remaining integration-specific negatives, including required-authority existence resolution against the Universal Core and real material graph drift, must be bound and tested after the Universal Core lands.

## 9. Cross-platform requirement

Customer-facing neutral code must preserve the current neutrality boundary and remain portable across Linux, Windows and macOS. It must not assume drive letters, developer homes, fixed ports or product names.

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

The parallel slice implements the consumer-side contracts and enforcement needed for this loop. Final completion waits only on binding those contracts to the canonical Universal Intelligence Core and proving the loop on unrelated external repositories.
