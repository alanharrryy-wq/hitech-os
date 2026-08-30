# PRISMA Authority Mesh / AutoMesh v2 operator runbook

Status: `CURRENT_OPERATOR_RUNBOOK`
Scope: PRISMA / hitech-os governance and repository-change workflows
Boundary: GitHub-first, evidence-first, fail-closed
Production certification: `false`

This runbook describes the current PRISMA Authority Mesh and AutoMesh revalidation behavior after PR #487. It is product-specific governance built on Code Atlas. It is not a requirement of the reusable Code Atlas neutral core and it does not replace the Factory Ledger, governing contracts, or task-exact Authority Mesh evidence.

## Core invariant

`main` movement triggers relevant-drift evaluation, not unconditional authority destruction.

A task-bound Authority Mesh is anchored to an immutable repository state and to its own authority/readset. When `main` advances, do not blindly keep the old Mesh and do not blindly throw it away. Revalidate it against the new canonical HEAD.

```text
old authority + current main
          |
          v
relevant-drift evaluation
          |
          +-- same HEAD ----------------> PASS_ALREADY_CURRENT
          |
          +-- unrelated drift ----------> PASS_NO_RELEVANT_DRIFT
          |                                rebound authority to current HEAD
          |
          +-- relevant drift -----------> full fresh Authority Mesh
          |
          +-- non-ancestor history -----> full fresh Authority Mesh
          |
          +-- invalid/unprovable evidence -> BLOCKED, fail closed
```

## Canonical operator lifecycle

1. Resolve the current canonical `main` HEAD.
2. Classify anti-rework / Factory Ledger obligations before authorizing technical work.
3. Build a task-exact AutoMesh request using canonical surface, domain, intent, required authorities, required directories, exclusions and 100% minimum coverage where the task requires it.
4. Trigger the remote Mesh with `/prisma-automesh task <urlsafe-base64-no-padding>`.
5. Require `PASS_COMPOSED_AUTHORITY_MESH`, required authority coverage at the task threshold, zero blockers and the expected HEAD before mutation.
6. Perform mutation on an isolated branch/PR. Do not mutate `main` directly.
7. If `main` moves before a governed mutation or merge, revalidate the prior artifact instead of assuming stale or safe.
8. Run the repository checks required by the affected scope and contracts.
9. Guard `main` and the PR head immediately before merge. Use an expected-head merge guard when the integration path supports it.
10. When a trust anchor, AutoMesh workflow or the revalidation engine itself changes, execute post-merge E2E against prior evidence to prove the relevant-drift/full-refresh path.

## GitHub-only commands

### Request a task-exact Authority Mesh

```text
/prisma-automesh task <URLSAFE_BASE64_REQUEST_WITHOUT_PADDING>
```

Request encoding rules:

- serialize the request as JSON;
- encode with URL-safe Base64, using `-` and `_` where required;
- strip trailing `=` padding;
- use only canonical values accepted by the gateway for `surface`, `domain` and `intent`;
- bind `expectedHead` to the current canonical `main` when the task requires exact-head authority;
- use 2 to 12 lanes when using the current composed AutoMesh request shape;
- do not force an invalid taxonomy value through the gateway. Fix the request instead.

Operational learning: a documentation task is governed under the canonical `governance` domain. A made-up `documentation` domain fails request validation and must not be bypassed.

### Revalidate an existing Authority Mesh

```text
/prisma-automesh revalidate <artifact-id> sha256:<artifact-digest>
```

The digest must identify the GitHub artifact envelope or the accepted authority payload as supported by the revalidator. Never omit digest verification.

## Revalidation outcomes

| Status | Meaning | Operator action |
|---|---|---|
| `PASS_ALREADY_CURRENT` | Prior authority already targets current HEAD. | Reuse validated authority bytes. No repack or full Mesh is needed. |
| `PASS_NO_RELEVANT_DRIFT` | `main` moved, but the delta does not intersect task-bound authority. | Use the rebound authority attestation tied to current HEAD. |
| `BLOCKED_RELEVANT_DRIFT` | Delta intersects required authority, protected scope, trust anchors, Layer Map bindings or certified pins. | Run the full fresh Mesh path against current HEAD. |
| `BLOCKED_NON_ANCESTOR_DRIFT` | Prior base is unavailable or is not an ancestor of current HEAD. | Run a full fresh Mesh. Do not guess history. |
| `BLOCKED_INVALID_PRIOR_AUTHORITY` | Artifact, manifest, chain, digest or other required evidence is invalid/unprovable. | Fail closed. Obtain fresh trusted authority rather than repairing evidence by inference. |

A full-refresh fallback is allowed only when the prior evidence was valid enough to trust the normalized request and the revalidator explicitly marks the fallback as allowed. Invalid prior evidence does not receive a prose override.

## What counts as relevant drift

The current evaluator considers task-bound evidence rather than merely comparing two SHA strings. Relevant inputs include:

- normalized-request `requiredAuthorities`;
- normalized-request `requiredDirectories`;
- lane `AUTHORITY_READSET.lock.json` required authorities/directories;
- `SUPPORTED` lane readset files;
- global revalidation trust anchors;
- visual Layer Map paths for visual tasks;
- certified pinned file identity mismatches;
- protected prefixes represented by the task evidence.

Semantic retrieval rows in state `CANDIDATE` do not become authority merely because they were retrieved. `Candidate != Authority` remains invariant.

## Trust anchors

The revalidation workflow itself is a trust anchor. Current trust-sensitive inputs include the AutoMesh workflows, Factory Ledger authority/evidence sources and gates, Code Atlas neutrality/change-assurance contracts, the Mesh gateway and the revalidation engine.

A change to a trust anchor is relevant drift by design and must not be hidden behind the fast path.

## Cross-platform identity and CRLF

Do not compare a Windows checkout hash directly to a canonical Git blob and call the mismatch drift. Checkout bytes may use CRLF while the repository object is canonical.

AutoMesh evidence can carry both:

- the SHA-256 captured for the selected checkout file; and
- the certified `repository_inventory.gitBlobSha` for the same repository path.

The v2 revalidator binds the supported readset pin to the certified inventory identity at the captured base commit, then validates current identity through the Git object database. This keeps Windows/Linux/macOS behavior portable without weakening evidence.

If the inventory path, worktree SHA-256 or `gitBlobSha` relationship is contradictory or tampered, fail closed. Do not normalize the contradiction away.

## Artifact and ZIP security

Authority artifacts are evidence, not ordinary ZIP convenience files. The revalidator rejects unsafe evidence including:

- path traversal such as `../`;
- absolute or Windows-style unsafe member paths;
- duplicate members and normalized-path collisions;
- symlink members;
- files present in the composed payload but absent from its manifest;
- manifest hash or byte-size mismatches;
- oversized members/archives;
- pathological compression ratios;
- ambiguous authority payloads;
- invalid revalidation chains.

Accepted authority envelopes include the original composed result, a GitHub-wrapped revalidated result and a direct composed payload when its required manifest/report structure is present and unambiguous.

A revalidated artifact can be revalidated again. The chain is accepted only when its revalidation digest, report status, current HEAD and read-only/non-production claims remain internally consistent.

## Visual tasks

Visual mutation remains stricter than ordinary governance work.

For a visual task, revalidation fails closed unless the authority artifact contains the governed legacy surface Mesh evidence and a `LAYERS_MAP.json` for the visual scope. The Layer Map contributes exact sensitive paths to drift evaluation.

No Layer Map means no visual authorization. Functional PASS does not substitute for visual evidence.

## Efficiency and concurrency

AutoMesh v2 is designed for parallel work without turning `main` into a single-file checkout line at the supermarket.

- Revalidation uses a bounded/sparse checkout for the fast path.
- The full repository is materialized only when relevant or non-ancestor drift requires a fresh Mesh.
- Exact same-head revalidation reuses validated authority bytes instead of recompressing a large artifact.
- Revalidation requests use request/comment-scoped concurrency so independent read-only work does not share one issue-wide lock.
- Mutation and merge gates may remain stricter than read-only analysis.
- Parallel agents should isolate task/branch/PR state and reconcile only where affected authority, files, owners or shared dependencies actually intersect.

Do not reduce validation coverage simply to save seconds. Optimize setup, I/O, checkout and repeated evidence work first.

## Required evidence to retain

For a governed Authority Mesh flow, preserve the evidence required by the task and contracts, normally including:

- GitHub workflow run ID and exact `head_sha`;
- artifact ID, name and digest;
- `PRISMA_MESH_GATEWAY_REPORT.json`;
- `PRISMA_MESH_REVALIDATION.json` when revalidation occurred;
- `MANIFEST.json`;
- `authority/normalized_request.json`;
- lane `AUTHORITY_READSET.lock.json` files;
- app/surface impact and contract/gate evidence emitted by the Mesh;
- Layer Map evidence when visual scope requires it;
- final PR/check/merge evidence for mutation closure.

Do not promote `productionCertified` from source existence, a successful revalidation or a passing local/CI run. It remains false until a separate evidence-backed production gate proves otherwise.

## Troubleshooting

### Request token rejected

Use URL-safe Base64 and remove trailing `=`. Do not use ordinary padded Base64 when the gateway token grammar rejects it.

### `INVALID_DOMAIN`, `INVALID_SURFACE` or invalid intent

Use the gateway's canonical taxonomy. Do not create convenient pseudo-surfaces such as `Tooling` or pseudo-domains such as `documentation` when the schema expects another canonical identifier.

### `main` moved

Do not automatically restart the entire task and do not automatically keep old authority. Run revalidation.

### Relevant drift detected

Let the workflow materialize the full repository and execute fresh preflight, task-exact parallel Mesh and compose stages. Do not manually relabel the drift as harmless.

### Invalid prior authority

Fail closed and obtain fresh trusted evidence. Digest/manifest/chain failures are not eligible for a confidence-based waiver.

### Windows-only pin mismatch

Verify whether the evidence correctly binds checkout SHA-256 to certified `repository_inventory.gitBlobSha`. Do not patch tests to ignore CRLF.

### Historical v1 artifact chaining failure

Older behavior could reject a GitHub artifact whose inner member was `prisma-automesh-revalidated-result.zip`. v2 accepts and verifies the revalidated envelope and its chain. Do not revive the old workaround.

## Evidence for the current v2 behavior

Source integration:

- PR #487: `perf(automesh): harden and accelerate revalidation v2`;
- merged to `main` as `5e79c3c36c635b2051681e510b3ab61fc348c627`;
- PR checks passed across CI, ForgeOS, Change Assurance anti-rework, repo navigation and Code Atlas hardening, including Windows/Linux/macOS portability lanes;
- focused/adversarial revalidation suite: 18 tests at merge time.

Post-merge E2E:

- run `33316050565` fed pre-v2 authority into v2 after the trust anchors changed;
- relevant drift was detected;
- full repository materialization, fresh universal preflight, task-exact Mesh, compose, evidence upload and final fail-closed gate all completed successfully.

Documentation synchronization authority:

- initial docs Mesh run `33316921023`, artifact `9733744471`, digest `sha256:1a9bd15280f3c38c4382c484aa61281e7b93ec7db3ed98dbd98dfabf6a374222`;
- `main` then moved because Sync Sentinel Ledger truth changed;
- revalidation run `33317174167` correctly classified the governance/Factory Ledger delta as relevant and executed a full fresh Mesh against `dec4ef395778be09cfe4b9ac2bc527efb80a9b0d`;
- refreshed evidence artifact `9733821589`, digest `sha256:53413da237fe498d9c809036d7567ec5c34a1807f9cdc9d51288fb82bd1cccd5`.

These records prove the bounded behavior described here. They do not prove production certification, arbitrary-repository universality, hosted multi-tenant security, legal/privacy compliance or unrelated product-runtime correctness.

## Canonical reading order

Before PRISMA technical work, read in this order when applicable:

1. `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md`
2. `PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER.json`
3. this runbook
4. `apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md`
5. task/surface/domain-specific contracts and authorities selected by the task-exact Mesh

The generated Mesh and current repository evidence decide task authority. This runbook explains how to operate the machinery; it does not grant permission by itself.
