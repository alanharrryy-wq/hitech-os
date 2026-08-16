# Code Atlas

> Repository intelligence and change-authority engine. Neutral by default, evidence-first, agent-neutral.

Code Atlas builds a traceable model of a software repository before a human or coding agent changes it. Its reusable core discovers repository facts, authority candidates, dependency/ownership/evidence relationships, change impact, snapshots and retrieval context without assuming one customer, product, machine, drive letter or repository layout.

On top of that neutral core, optional profiles/adapters can add product-specific expectations. The Change Intelligence layer then turns repository evidence into an auditable change loop: **understand the requested change, define explicit authority and scope, let a human or agent work, verify the actual result, and return `PASS`, `BLOCKED` or `UNKNOWN` with evidence.**

## Current evidence status

Current governed state: **`LOCAL_VERIFIED`**.

The Universal Intelligence + Customer Wow binding remains the canonical implementation and the Factory Ledger continues to preserve it as `doNotRebuild=true`. PR #275 hardened that implementation after a real external falsification gate and merged the source fix into `main` as `caf918694c1c397d19a61bff217800d027a384e3`.

External evidence is now **broader but still bounded**. CAEXT V2 replayed the neutral/default profile read-only against **seven pinned unrelated repositories** across **Ubuntu and Windows**: Click (Python), Vite (TypeScript/Node), ripgrep (Rust), Cobra (Go), Spring PetClinic (Java/Spring), Kubernetes examples (YAML/IaC), and pybind11 (C++/Python). The original three-repository regression completed **30/30 declared scenarios per OS**; the four-repository diversity gate completed **40/40 per OS**. Both OSes preserved read-only originals, repeatability, and **0 `CORE_LEAK`** findings.

CAEXT V2 also retired the two known legacy harness ambiguities without changing the Code Atlas core: neutrality matching is boundary-aware with explicit provenance, and Impact Radius metrics come from the prepared change model rather than the DISCOVER graph. The evidence remains deliberately bounded: Go, Java, and Kubernetes YAML produced no repository dependency edges in this corpus, while pybind11 produced two, so dependency understanding for those stacks is **not** claimed complete.

Historical real-diff validation is now complete as **bounded evidence**, not as a universality claim. At immutable parent commits, Cobra/Go measured **25% recall / 100% precision**, Spring PetClinic/Java **50% / 100%**, and pybind11 C++/Python **33.33% / 100%**; all three had **0% companion-path recall**, exposing a conservative Impact Radius that missed historical tests/docs. A Kubernetes YAML target absent from the parent snapshot correctly returned `BLOCKED` with no Authority Pack. Ubuntu and Windows reproduced the same result, with read-only originals and repeatability preserved.

The bounded single external-agent usefulness pilot is recorded, but the next independent-agent replication attempt is currently **`BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR`**: GitHub Actions granted `CopilotRequests: write` and installed Copilot CLI `1.0.80`, then GitHub rejected the request with `Access denied by policy settings`. A bounded human usefulness study remains a separate future gate; hosted/security boundaries remain separate gates. Current evidence does **not** certify high companion-path recall across stacks, arbitrary repositories, hosted multi-tenant execution, enterprise IAM/security, legal/privacy compliance, paid-pilot readiness by itself, absolute repository universality, or production certification.

`certifiable=false` and `productionCertified=false` remain invariant until separate evidence-backed gates prove otherwise.

## Independent-agent replication gate — external policy blocked

A fresh task-exact Authority Mesh authorized a stronger **same-task paired** replication design: six historical tasks, each evaluated once as `BASELINE` and once as `ASSISTED`, for 12 isolated external-agent sessions with ground truth sealed until paired responses were persisted.

That experiment did **not** run to scoring. Independent evaluator availability failed closed:

- replication Authority Mesh: run `31915254808`, artifact `9254730793`, `sha256:62625686559fa46e94479c57dcf492e0dd59e9f2b5b7fa202989edae02ce738a`;
- direct `copilot-swe-agent[bot]` assignment through the connected GitHub app: HTTP 403;
- `@copilot` PR mention: no agent response or head movement;
- GitHub Actions availability run `31916081998` received `CopilotRequests: write`, installed Copilot CLI `1.0.80`, then GitHub returned **`Access denied by policy settings`**;
- availability artifact `9254928517`, `sha256:9b66acf2461bc765727cf3ff8b6eca6c63c1931e628c47e89e5cf406d4b433f9`;
- blocker closure Authority Mesh: run `31916191500`, artifact `9254953865`, `sha256:bb15de6aa6394d61ea22eabe8f2e3a11ddb178429b6430a11a800566fb0184bb`.

Result: **`BLOCKED_BY_MISSING_INDEPENDENT_EVALUATOR`**. No 12-session responses were invented, no score was produced, and no Code Atlas core defect was inferred. `LOCAL_VERIFIED`, `doNotRebuild=true`, `certifiable=false`, `productionCertified=false`, and `humanUsefulness=NOT_MEASURED` remain unchanged.

## Architecture

```text
Repository / authorized source archive
                 |
                 v
       UNIVERSAL INTELLIGENCE CORE
       ---------------------------
       repository discovery
       authority discovery
       dependency / ownership graphs
       evidence / architecture graphs
       change impact
       portable snapshots
       freshness / drift
       derived query index
       semantic retrieval
                 |
                 v
        OPTIONAL PROFILES / ADAPTERS
        ----------------------------
        explicit product expectations
        explicit compatibility layers
        never automatic authority
                 |
                 v
       CHANGE INTELLIGENCE / CUSTOMER WOW
       -------------------------------
       Change Studio
             |
             v
       Agent Authority Pack
             |
             v
       Human / Codex / Claude / Cursor / other agent
             |
             v
       Actual diff + session evidence
             |
             v
       Verify
             |
             v
       PASS / BLOCKED / UNKNOWN
             |
             v
       Evidence Report + ROI signals + continuation
```

The core rule is simple: **repository evidence establishes facts; profiles add expectations; neither search results nor generated indexes become authority merely because they exist.**

## What the Universal Intelligence Core provides

The package `code_atlas.intelligence` owns repository-neutral intelligence primitives:

- repository inventory and technology-aware discovery;
- authority candidate discovery and explicit authority states;
- required-authority and required-directory gates;
- dependency graph;
- ownership graph;
- evidence graph;
- architecture-layer graph;
- test intelligence;
- static change-impact analysis;
- portable repository snapshots;
- commit/tree identity and freshness assessment;
- semantic retrieval that returns evidence, not truth;
- derived SQLite/query indexes that are rebuildable projections, not sources of truth;
- deterministic request/provenance metadata;
- read-only operation by default.

### Authority states

Authority candidates are not promoted merely because a familiar file exists. The neutral authority model distinguishes states such as:

```text
DISCOVERED
CANDIDATE
SUPPORTED
AUTHORITATIVE
CONFLICTED
STALE
MISSING
```

A `README`, `CODEOWNERS`, schema, architecture document or test may be useful evidence without automatically controlling every claim.

## What Change Intelligence adds

The package `code_atlas.change_intelligence` composes the neutral repository model into customer-facing change controls without rebuilding repository discovery, graphs, snapshots or indexing.

Implemented V1 surfaces include:

- **Change Studio composition**: normalized intent, explicit targets, impact, protected scope, unknowns, contradictions and required evidence;
- **Agent Authority Pack**: portable scope/authority contract locked to repository, commit/tree and compatibility digests;
- **Verify Agent / Verify Change**: checks actual changed paths, protected boundaries, required evidence, drift and session compatibility;
- **Policy Packs**: customer expectations without converting configuration into facts;
- **Evidence Q&A**: evidence-backed answers with support levels and `doesNotProve` boundaries;
- **Architecture Delta**: normalized architectural change evidence;
- **Evidence connectors/parsers**: JUnit, SARIF, coverage, CODEOWNERS-style ownership and CI result normalization;
- **Agent Session evidence**: what was requested, authorized, touched and evidenced without inferring hidden reasoning;
- **Customer Runner contracts**: `LOCAL_ONLY` and `PORTABLE_EVIDENCE` boundaries;
- **Evidence Reports and portable bundle manifests**;
- **ROI events**: raw operational measurements with financial estimates kept explicitly derived.

## Fail-closed semantics

Code Atlas treats uncertainty as a first-class result.

### `PASS`

All mandatory obligations represented by the evaluated contract are satisfied by the supplied evidence.

### `BLOCKED`

A required obligation failed, for example:

- required authority missing or conflicted;
- stale repository/commit/tree identity;
- authority, policy or evidence compatibility drift;
- protected-scope mutation;
- out-of-scope mutation;
- required check or evidence missing;
- explicit customer policy blocker.

### `UNKNOWN`

There is not enough evidence to make the requested claim. `UNKNOWN` is not silently converted into a warning-only green.

## Non-negotiable evidence rules

1. **Candidate is not authority.** Discovery alone never grants control.
2. **Retrieval is not proof.** Semantic search locates evidence; it does not establish truth.
3. **Derived index is not authority.** SQLite/search indexes are disposable projections.
4. **Impact Radius is not authorization.** A potentially affected path does not become editable scope.
5. **Profiles add expectations, not facts.** A profile can say what to look for; current repository evidence must prove what exists.
6. **Targets are not guessed.** Authority Packs require explicit, evidence-supported targets.
7. **Unknown stays unknown.** Missing evidence does not become green.
8. **Read-only is the default analysis boundary.** Repository, Git, DB, processes, ports and deployments are not mutated by the neutral analysis path.
9. **Product adapters are explicit opt-in.** No customer profile is silently selected.
10. **Certification claims follow evidence.** Source/local verification is not production certification.

## Quick start: neutral repository intelligence

Run from `tools/code-atlas` with the package source on `PYTHONPATH`.

### PowerShell

```powershell
$env:PYTHONPATH = "src"
python -m code_atlas.intelligence.cli `
  --repo "<path-to-repository>" `
  --out "<path-to-output>" `
  --intent DISCOVER
```

### Bash / zsh

```bash
PYTHONPATH=src python -m code_atlas.intelligence.cli \
  --repo "/path/to/repository" \
  --out "/path/to/output" \
  --intent DISCOVER
```

Optional neutral inputs include:

```text
--profile <explicit-profile>
--intent DISCOVER|AUDIT|VERIFY|FIX|BUILD|CERTIFY
--domain <domain>
--required-authority <repo-relative-path>
--required-directory <repo-relative-directory>
--excluded-authority <repo-relative-path>
--changed-path <repo-relative-path>
--query <semantic-query>
--workers 1..18
--allow-missing-authority
```

`--allow-missing-authority` deliberately relaxes a fail-closed requirement and should only be used when the caller explicitly wants that behavior.

The modular top-level CLI also exposes the neutral intelligence command:

```bash
PYTHONPATH=src python -m code_atlas.cli.main intelligence \
  --repo "/path/to/repository" \
  --out "/path/to/output" \
  --intent DISCOVER
```

## Programmatic intelligence API

```python
from code_atlas.intelligence import IntelligenceRequest, resolve_intelligence_context

request = IntelligenceRequest(
    intent="VERIFY",
    domain="authentication",
    required_authorities=("CODEOWNERS",),
    changed_paths=("src/auth.py",),
)

context = resolve_intelligence_context(
    "/path/to/repository",
    request=request,
)
```

The returned structured context includes repository inventory, authority discovery, graphs, snapshot, retrieval/coverage metadata and explicit non-authoritative flags for derived projections.

## Programmatic Change Intelligence API

```python
from code_atlas.change_intelligence import prepare_change, verify_prepared_change

prepared = prepare_change(
    "/path/to/repository",
    change_request="Harden authentication without touching payments",
    target_paths=["src/auth.py"],
)

# A human or external coding agent performs the authorized work.

verification = verify_prepared_change(
    prepared,
    "/path/to/repository",
    changed_paths=["src/auth.py"],
)
```

Customer Policy Packs and produced evidence can be added when the workflow requires them. The minimal example above intentionally avoids an undefined project-specific policy object.

Change Intelligence is **agent-neutral**. The Authority Pack can govern a human workflow or an external coding agent. Code Atlas does not need to become the coding agent to control the change boundary.

## Change Intelligence contract CLI

The current contract CLI provides pack validation, change verification and evidence parsing:

```text
validate-pack
verify-change
parse-junit
parse-sarif
parse-codeowners
parse-coverage
normalize-ci
```

Example:

```bash
PYTHONPATH=src python -m code_atlas.change_intelligence.cli \
  validate-pack \
  --pack ./authority-pack.json
```

## Optional profiles and adapters

Reusable execution is machine-neutral, repository-neutral and product-neutral. Product-specific compatibility belongs behind explicit profiles/adapters.

Canonical runtime inputs are:

```text
CODE_ATLAS_PROJECT_ROOT
CODE_ATLAS_OUTPUT_ROOT
CODE_ATLAS_RESULT_ROOT
CODE_ATLAS_PROFILE
```

A profile may tell Code Atlas to look for product-specific authorities or conventions. It may **not** invent those authorities if the current repository snapshot does not support them.

### PRISMA is an optional profile, not a universal requirement

PRISMA/hitech-os may use richer adapters and governance such as Authority Mesh, Factory Ledger, NDC, surface contracts and visual-layer evidence. Those are product-specific consumers of the neutral engine.

They do not mean that a foreign repository must contain PRISMA files, use Windows, live on an `F:\` drive, use Prisma ORM, expose PRISMA surfaces or adopt PRISMA's taxonomy.

Any Windows, `F:\...`, hitech-os or PRISMA paths appearing in historical docs or operator examples are **local/project examples**, not Code Atlas requirements.

## Customer Runner boundary

Customer Wow V1 defines two runner modes:

- `LOCAL_ONLY`: analysis/evidence remains inside the customer environment;
- `PORTABLE_EVIDENCE`: only an approved non-source evidence bundle may leave the environment.

The V1 contract is read-only and least-privilege by default. It does not by itself certify hosted execution, tenant isolation, enterprise IAM, data-egress compliance or legal/privacy compliance.

## Legacy Engineering Console and forensic compatibility

Code Atlas existed before the Universal Intelligence architecture and retains useful engineering surfaces.

The original PySide6 console remains a compatibility/engineering cockpit:

```bash
python code-atlas.py
```

Historical and specialized capabilities include Visual Atlas, Black Glass, DB Glass / Reality Check, Atlas Coverage Audit, Important Files Gate and Todo El Show Plus. They remain useful forensic and operator tooling, but they are **not the architectural definition of the neutral engine**.

Likewise, Prisma ORM, SQLite, Python and full-stack detectors are supported technology-specific analyzers when useful. No single technology is mandatory for a repository to be analyzed by the universal core.

## Modular CLI surface

The current modular CLI exposes:

```text
coverage
important gate (`gate`)
db reality (`db`)
todo-plus
operational
intelligence
uimap       # explicit adapter path
ui-bridge   # explicit adapter path
```

Adapter commands are explicit. Generic entrypoints must not select a product adapter implicitly.

## Repository layout

Important current areas under `tools/code-atlas` include:

```text
tools/code-atlas/
├── README.md                          # canonical current overview
├── README_professional_code_atlas.md  # compatibility pointer
├── AGENTS.md                          # workspace rules
├── NEUTRALITY_POLICY.md               # reusable neutrality policy
├── CODE_ATLAS_NEUTRALITY_CONTRACT.json
├── code-atlas.py                      # legacy PySide6 engineering console
├── scripts/                           # operational runners / compatibility workflows
├── src/code_atlas/
│   ├── intelligence/                  # Universal Intelligence Core
│   ├── change_intelligence/           # Customer Wow / change controls
│   ├── core/                          # shared neutral runtime/guards
│   ├── coverage/                      # coverage / important-file tooling
│   ├── db_glass/                      # DB forensic tooling
│   ├── manifest/                      # portable run/manifest tooling
│   ├── app_map/                       # explicit adapter-oriented mapping
│   ├── ui_bridge/                     # explicit adapter-oriented UI bridge
│   └── ...                            # other governed capabilities/adapters
├── docs/
│   ├── README.md                      # documentation navigation index
│   ├── CODE_ATLAS_CUSTOMER_WOW_V1.md
│   ├── CODE_ATLAS_CUSTOMER_WOW_V1.contract.json
│   └── historical / feature-specific notes
└── tests/                             # operational, neutrality and feature tests
```

This layout intentionally separates reusable neutral primitives from explicit compatibility/adapters and from historical operator surfaces.

## Canonical documentation

Start here:

- [`README.md`](README.md): current architecture and usage overview.
- [`AGENTS.md`](AGENTS.md): workspace rules for agents and maintainers.
- [`NEUTRALITY_POLICY.md`](NEUTRALITY_POLICY.md): reusable neutrality rules.
- [`CODE_ATLAS_NEUTRALITY_CONTRACT.json`](CODE_ATLAS_NEUTRALITY_CONTRACT.json): machine-readable neutral/adapter boundary.
- [`docs/CODE_ATLAS_CUSTOMER_WOW_V1.md`](docs/CODE_ATLAS_CUSTOMER_WOW_V1.md): current Customer Wow architecture, evidence and limitations.
- [`docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json`](docs/CODE_ATLAS_CUSTOMER_WOW_V1.contract.json): machine-readable Customer Wow contract.
- [`docs/README.md`](docs/README.md): navigation for current vs historical/feature-specific documentation.

For PRISMA/hitech-os specifically, the repository Factory Ledger is the canonical anti-rework source for capability maturity/status. Documentation summaries do not override that ledger.

## What Code Atlas currently proves

Current source/local evidence supports these statements:

- the reusable execution boundary is neutralized and guarded against fixed machine/repository/product assumptions;
- the Universal Intelligence Core can discover and model neutral synthetic repositories read-only;
- Change Intelligence is bound to that core rather than duplicating it;
- explicit target/scope rules fail closed;
- Impact Radius does not widen authorization;
- protected and out-of-scope changes block;
- authority/evidence drift and stale exact packs block;
- total neutrality and operational hardening passed repository CI across Ubuntu, Windows and macOS lanes for the merged Customer Wow integration.

## What Code Atlas does not currently prove

Current evidence does **not** prove:

- correct behavior across arbitrary real external repositories or every technology stack;
- production runtime readiness;
- hosted multi-tenant isolation;
- enterprise IAM/security certification;
- customer data-egress certification beyond the current runner contract;
- paid-pilot readiness by itself;
- legal/privacy compliance;
- production certification.

The next governed gate is external-repository evidence, not another rebuild of the Universal Intelligence or Customer Wow source.

## Design principle

```text
Know the repository.
Resolve what actually has authority.
Control the scope of the requested change.
Let the human or agent work.
Verify what really changed.
Prove the result with evidence.
```

That is the current Code Atlas architecture.

## External-agent usefulness evidence — 2026-08-15

Governed state remains **LOCAL_VERIFIED** with `doNotRebuild=true`, `certifiable=false`, and `productionCertified=false`.

- Pilot: PR #288, merge `cbb0949701529399810ac8ca2033b9f708f790f2`.
- Task-exact Authority Mesh: run `31913264991`, artifact `9254247789`, digest `sha256:4fa908f6f4b123b174d525158bad25d24a2c1e3d3e7b0084c09a467432b36015`.
- Final scoring: run `31914395822`, artifact `9254539137`, digest `sha256:f6fab08f22945ce54b23ac495f2f3f797cafa4edd33e61f9295c65c3a3795b5c`, result digest `8e1a155a66fcb7c713e32d334edf3bf431cced9e909563ef48ef393c5cc737cd`.
- ASSISTED, three tasks: authorization widening 0%; target editable inclusion 100%; changed-test recall 100%; companion-inspection recall 88.89%; valid evidence references 100%; fake-green 0; unknown omission 0.
- BASELINE, three different tasks: authorization widening 0%; target editable inclusion 33.33%; changed-test recall 0%; companion-inspection recall 0%; valid evidence references 100%.
- The condition comparison is descriptive only: task heterogeneity plus one evaluator means **no causal uplift claim**.
- Human usefulness is **NOT_MEASURED**. Independent multi-agent replication is not yet proven.
- Observed ROI is limited to `outOfScopeChangeRate=0.0` and `evidenceCompletenessRate=1.0`; no financial estimate was generated.
- Two `J TEST HARNESS FAILURE` defects were repaired fail-closed before the valid score: run-volatile packet binding and an invalid `build_roi_event(metric_values=...)` call. Neither was a product-core defect.
- Closure Authority Mesh: run `31914600435`, artifact `9254577043`, digest `sha256:fdce5a4d2b299fdc0b566e720dfab1eea0690b09f4ead60debf60303d8414a7b`.

**Next evidence gate:** bounded human usefulness study and/or independent multi-agent replication. Hosted/security and production certification remain separate boundaries; do not rebuild core from this pilot.
