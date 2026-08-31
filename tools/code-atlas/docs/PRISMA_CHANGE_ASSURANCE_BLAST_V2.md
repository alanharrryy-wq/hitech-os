# PRISMA Change Assurance Blast Intelligence V2

Status: `LOCAL_VERIFIED_BOUNDED_IMPACT_INSPECTION`  
Engine: `Code Atlas`  
Checklist owner: `B / RESOLVE / Useful Impact Radius`  
Principle: **No evidence. No green.**  
Invariant: **Impact Radius != Authorization.**

## 1. Purpose

Blast Intelligence V2 is an additive evolution of the existing Code Atlas `changeImpact` capability. It does **not** create a second dependency graph, authority engine, change model, verifier, registry, or product surface.

The canonical conservative projection remains `changeImpact.impacted`, produced by the existing static transitive reverse-dependency graph. Blast V2 adds a narrower, explained inspection projection that can distinguish:

- paths that should be inspected now;
- paths that are evidence bridges used to prove a relationship but are not themselves promoted to primary inspection;
- conservative or inferred candidates that remain inspect-only;
- unresolved or unsupported relationships that remain explicit `UNKNOWN` evidence.

Blast V2 never expands `Authority Pack.allowedScope`. A path appearing in `inspectionPaths`, `evidenceBridgePaths`, `inspectOnlyCandidates`, history, ownership, or semantic ranking is not authorization to edit that path.

## 2. Canonical output contract

Blast V2 lives under the existing `changeImpact` object. The compatibility projection remains intact.

| Field | Meaning | Authorization effect |
|---|---|---|
| `impacted` | Existing conservative transitive reverse-dependency radius | None |
| `rawInspectionPaths` | Pre-focus additive inspection candidates | None |
| `inspectionPaths` | Focused paths recommended for direct inspection | None |
| `evidenceBridgePaths` | Intermediate paths needed to prove a supported chain | None |
| `inspectOnlyCandidates` | Conservative, structural, ownership, history, deferred or inferred candidates | None |
| `whyIsThisInBlast` | Per-path evidence, reason, support level and disposition | None |
| `unknownOrUnsupported` | Explicit unresolved/unsupported relationships and focus ambiguity | None |
| `inspectionV2.relations` | Typed relationships with evidence/provenance | None |
| `focusV2` | Deterministic bounded focus decision and branch evidence | None |
| `blastDigest` | Deterministic digest of the V2 inspection state | None |

The legacy `impacted` field is intentionally not overwritten by the focused projection. Existing consumers keep the conservative radius; V2-aware consumers gain more useful inspection semantics without breaking the compatibility contract.

## 3. Evidence tiers

Blast V2 uses three evidence tiers:

- `SUPPORTED`: repository-provable static relationships or typed companion evidence. Examples include a repository-resolved C/C++ include edge or a deterministic same-test-stem cross-language companion.
- `INFERRED`: bounded evidence useful for inspection but insufficient for proof or authorization. Historical co-change and shared ownership are in this tier and remain `INSPECT_ONLY`.
- `UNKNOWN`: unresolved, unsupported, ambiguous or insufficiently proven relationships. `UNKNOWN` is not converted to `PASS_WITH_WARNING` and is never painted green.

Every non-`UNKNOWN` relation emitted by Blast V2 carries evidence. Missing relation provenance is a product failure in the historical evidence gate.

## 4. Language-family behavior

### Go

Blast V2 **reuses** the existing `GO_BOUNDED_V1` `actionableReview`; it does not rebuild Go impact intelligence. The focused primary inspection set uses the existing exact direct Go relationships plus test-companion closure. Structural-only conservative paths remain inspect-only.

This preserves the previously governed rule:

`CHANGED_PLUS_DIRECT_EXACT_GO_REVERSE_DEPENDENCIES_PLUS_TEST_COMPANION_CLOSURE`

and its existing authorization boundary:

`ACTIONABLE_REVIEW_NEVER_EXPANDS_ALLOWED_SCOPE`

### C / C++

Blast V2 adds repository-provable local include relationships and typed cross-language test companions. For high-fanout include hubs, the engine uses a deterministic semantic branch focus only to rank **inspection**, never authority.

A high-fanout branch is promoted only when one branch has uniquely stronger bounded semantic path evidence. If the branch is ambiguous, the candidates remain inspect-only and an explicit `UNKNOWN` record is emitted with reason:

`HIGH_FANOUT_STATIC_BRANCH_NOT_UNIQUELY_SUPPORTED_BY_SEMANTIC_EVIDENCE`

Intermediate headers that merely connect the changed file to the relevant test become `evidenceBridgePaths`. They prove the chain without bloating the primary inspection set.

### Java

Java keeps the existing bounded Java dependency evidence. Blast V2 does not force the Go or C/C++ focus model onto Java. The canonical Java impact remains unchanged unless a separately governed Java-specific improvement is supported by fresh evidence.

### Unsupported or mixed families

Unsupported static-language families remain explicit `UNKNOWN` where appropriate. Mixed or unsupported change families do not borrow another language family's focus policy. The engine fails closed rather than guessing semantics.

## 5. Additional bounded evidence

The additive enrichment layer may expose:

- repository-resolved C/C++ include edges;
- typed cross-language test companions;
- bounded exact path references from contract/config/API/schema-like files;
- bounded Git historical co-change as `INFERRED / INSPECT_ONLY`;
- shared CODEOWNERS as `INFERRED / INSPECT_ONLY`.

Historical co-change and ownership are deliberately not primary proof. They are hints to inspect, not instructions to mutate.

Semantic terms from the change request may influence high-fanout **inspection ranking only**. Semantic retrieval remains discovery, not proof.

## 6. Historical real-diff evidence

The V2 evidence harness reuses the existing immutable historical real-diff carrier and its four cases. The in-run legacy `impactRadius.impacted` projection is the baseline; there is no parallel baseline engine.

Final cross-platform evidence run: `33420061268`.

Artifacts:

- Ubuntu: artifact `9768535858`, SHA-256 `3569274b8f1e0e7dc3a6bdc0cf695e7a0ba15228eff9838f7c10c9dd58298e04`.
- Windows: artifact `9768544881`, SHA-256 `90a69c21153a1991a952d6a650511847328553a7cc0d394b812e3e0a5eed356d`.

Both lanes completed `SUCCESS`, reported `VERIFY_BLAST_V2_HISTORICAL_EVIDENCE_CAPTURED`, kept the external historical repositories read-only, produced no authorization widening, and matched on the measured accuracy results.

| Case | Baseline recall / precision / companion | Blast V2 primary recall / precision / companion | Primary predicted | Primary false positives |
|---|---:|---:|---:|---:|
| Go / `spf13/cobra` | 75.0 / 9.38 / 66.67 | **75.0 / 75.0 / 66.67** | 4 | 1 |
| Java / Spring PetClinic | 100 / 100 / 100 | **100 / 100 / 100** | 2 | 0 |
| Mixed C++ / Python / `pybind11` | 33.33 / 100 / 0 | **100 / 100 / 100** | 3 | 0 |
| Kubernetes missing-parent new path | N/A | N/A, fail-closed | N/A | N/A |

### Go result

The conservative Cobra radius still contains 32 paths and remains the compatibility baseline. Blast V2 reuses the existing Go actionable review and narrows primary inspection to:

- `command.go`
- `command_test.go`
- `completions.go`
- `completions_test.go`

The historical diff still contains the known documentation false negative `site/content/completions/_index.md`. Blast V2 does not hide this blind spot.

### pybind result

The historical pybind change actually modified:

- `include/pybind11/detail/function_ref.h`
- `tests/test_copy_move.cpp`
- `tests/test_copy_move.py`

The legacy radius predicted only the changed header. Blast V2 primary inspection predicts exactly those three files, producing 100/100/100 recall/precision/companion recall.

The static chain is still preserved as evidence:

`function_ref.h -> pybind11.h -> stl.h -> test_copy_move.cpp`

but the intermediate `pybind11.h` and `stl.h` are `evidenceBridgePaths`, not primary inspection targets. `test_copy_move.py` is linked by deterministic typed test-companion evidence.

The broader conservative all-candidate set remains intentionally large and low precision. That is visible evidence, not a hidden success claim.

## 7. Determinism and portability

A first implementation failed the new repeatability test because Windows-style `\\` paths and POSIX `/` paths could produce different Blast digests. This was classified as a **PRODUCT** failure, not dismissed as harness noise.

The fix canonicalizes changed paths with the existing repository-safe path normalization before graph construction. The negative test remains in the suite.

A second routing defect was also caught during historical testing: the legacy graph exposes a `GO_BOUNDED_V1` actionable projection even when the changed target is not Go. The V2 focus router now activates Go focus only for all-Go targets and C/C++ focus only for all-C/C++ targets. Java and unsupported/mixed families cannot accidentally inherit another language's focus semantics.

## 8. Operational hardening

Final Code Atlas Operational Hardening run: `33420061279`.

- Ubuntu operational lane: PASS.
- Windows operational lane: PASS.
- macOS portability lane: PASS.
- Windows portability lane: PASS.
- Ubuntu operational suite: **183 tests, all PASS**.
- Neutrality gate: `PASS_CODE_ATLAS_TOTAL_NEUTRALITY`.
- Neutrality blocking findings: `0`.
- Semantic neutrality blockers: `0`.
- Implicit adapter imports: `0`.

The focused Blast V2 tests include positive behavior and native negative/falsification cases for ambiguous high fanout, unsupported language, unresolved includes, path traversal, cross-platform path normalization, provenance requirements, history/ownership inspection boundaries, evidence bridges, and Authority Pack non-widening.

## 9. Known limitations

Blast V2 does not claim:

- complete dynamic/runtime impact discovery;
- complete macro, reflection, dependency-injection, build-tag, cgo, plugin or generated-code semantics;
- arbitrary-language completeness;
- universal accuracy or an accuracy SLA;
- that every conservative inspect-only candidate is useful;
- that the Cobra documentation false negative is solved;
- that semantic ranking is proof;
- that history or ownership is proof;
- that an impact or inspection set authorizes a source mutation;
- production, enterprise, hosted, paid-pilot, legal/privacy or security certification.

`productionCertified=false` remains explicit.

## 10. Reuse rule

Future work must reuse this capability in place:

- preserve the conservative `impacted` compatibility projection;
- preserve `GO_BOUNDED_V1` instead of rebuilding Go impact;
- preserve evidence bridges and inspect-only separation;
- preserve explicit UNKNOWN on ambiguity or unsupported semantics;
- preserve deterministic evidence/provenance and digests;
- preserve `Impact Radius != Authorization`;
- expand language-specific focus only from fresh external evidence, not benchmark chasing.

If a future stack cannot be proven with bounded repository facts, the correct result is `UNKNOWN` or a conservative inspect-only projection, not a fabricated green answer.
