# Code Atlas

> Repository intelligence and change-authority engine. Neutral by default, evidence-first, agent-neutral.

Code Atlas builds a traceable model of a software repository before a human or coding agent changes it. Its reusable core discovers repository facts, authority candidates, dependency/ownership/evidence relationships, change impact, snapshots and retrieval context without assuming one customer, product, machine, drive letter or repository layout.

On top of that neutral core, optional profiles/adapters can add product-specific expectations. The Change Intelligence layer then turns repository evidence into an auditable change loop: **understand the requested change, define explicit authority and scope, let a human or agent work, verify the actual result, and return `PASS`, `BLOCKED` or `UNKNOWN` with evidence.**

## Current evidence status

Current governed state: **`LOCAL_VERIFIED`**.

The Universal Intelligence + Customer Wow binding remains the canonical implementation and the Factory Ledger continues to preserve it as `doNotRebuild=true`. PR #275 hardened that implementation after a real external falsification gate and merged the source fix into `main` as `caf918694c1c397d19a61bff217800d027a384e3`.

External evidence is now **limited but real**: the neutral/default profile was replayed read-only against pinned unrelated repositories **Click (Python), Vite (TypeScript/Node monorepo), and ripgrep (Rust)**. The post-fix full replay completed **30/30 declared scenarios**, **3/3 repeatability**, read-only compliance, and zero critical behavior failures after manual adjudication of legacy harness reporting. The hardened source also passed **140 Code Atlas tests** and **6/6 PR CI workflows**.

The evidence specifically supports fail-closed undeclared dirty-worktree detection, evidence-bearing Rust source targets with bounded repository-provable Rust dependencies, and normalized JS/TS parent-relative dependency resolution. It does **not** establish correctness for arbitrary repositories or stacks.

The next evidence gate is **broader repository/stack diversity, independent second-machine repeatability, and hosted/security boundary evidence**. Current evidence does **not** certify hosted multi-tenant execution, enterprise IAM/security, legal/privacy compliance, paid-pilot readiness by itself, absolute repository universality, or production certification.

`certifiable=false` and `productionCertified=false` remain invariant until separate evidence-backed gates prove otherwise.

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
