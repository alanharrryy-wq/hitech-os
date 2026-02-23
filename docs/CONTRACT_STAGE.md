# CONTRACT
Version: 1.0.0
Status: Active
Last Updated: 2026-02-18
Scope: Entire monorepo (`hitech-os`)

## STAGE 0 — GLOBAL CONSTITUTION

### S0_ORIG — Constitutional Origin

#### 1. Purpose

This file defines non-negotiable constraints for this repository.

Every engineer, script, and automation must comply with this document.
If any local workflow conflicts with this contract, the contract wins.

### S0_DET — Determinism Law

#### 2. Design Axioms

1. Determinism over convenience.
2. Explicit contracts over implicit coupling.
3. Small modules with clear boundaries.
4. Feature flags default to OFF everywhere.
5. Source trees are code-only; never data dumps.
6. Local-first operation; network access is optional and never required for baseline checks.

### S0_PRI — Enforcement Priority

#### 3. Monorepo Boundary Law

The repository root contains:

- `apps/`: user-facing applications.
- `services/`: backend and automation services.
- `packages/`: reusable shared modules.
- `tools/`: operational tooling and guardrails.
- `docs/`: laws, maps, and execution memory.

Boundary rules:

1. `apps/*` may depend on `packages/*`.
2. `services/*` may depend on `packages/*`.
3. `services/*` may communicate with each other via HTTP only; no direct runtime imports across service roots.
4. `packages/*` must never import from `apps/*` or `services/*`.
5. `tools/*` can inspect repository files but must avoid app/service runtime coupling.

### S0_LEX — Blueprint as Law Doctrine

#### 4. Determinism Requirements

Determinism is mandatory for generated content and CI outputs.

Required behavior:

1. Stable file order before write.
2. Stable key order in JSON artifacts.
3. Stable line endings through `.gitattributes`.
4. No timestamp-driven IDs in generated schemas unless explicitly passed.
5. No random UUID generation in bootstrap examples.

Forbidden behavior:

1. Writing unordered maps directly to disk.
2. Embedding machine-specific absolute paths in generated artifacts.
3. Including transient metadata (PID, memory addresses, env snapshots) in committed outputs.

### S0_PROOF — Evidence Doctrine

#### 5. Feature Flags Policy

All feature flags default to `false` in:

1. `packages/contracts` defaults.
2. `services/core-api` runtime responses.
3. `apps/web` fallback UI config.

Rules:

1. Adding a new flag requires updates in contract schemas, API endpoint, and UI gate.
2. New flags must have explicit owner, rollout plan, and rollback condition documented in `docs/NOTEBOOK.md`.
3. Flags are not authorization controls; they only gate behavior paths.

### S0_NSP — No Silent Pass Rule

#### 6. Artifact and Dump Prohibition

No dump-like files are allowed under any `src/**` path.

This includes:

- archives (`.zip`, `.7z`, `.tar`, `.gz`, `.rar`)
- backups (`*.bak*`)
- suspicious names (`*DUMP*`, `*OUT*`)
- oversized text/image artifacts in source paths

Enforcement:

1. `tools/health` scans source trees.
2. Violations are deterministic and fail with non-zero exit code.
3. File path list is sorted before report output.

### S0_TRUST — Trusted Roots Definition

#### 7. Contracts and Schema Authority

`packages/contracts` is the canonical source for shared shape definitions.

Rules:

1. Zod schema definitions are primary for TypeScript modules.
2. Generated JSON Schema artifacts in `packages/contracts/schemas/generated` are committed and deterministic.
3. Python service models must align to schema shape, field names, and enum values.
4. Runtime services must validate external input against local model rules.

Change flow:

1. Update Zod schema.
2. Re-run schema generator.
3. Review generated diff.
4. Update `services/ai-agent` model mirror.
5. Update tests and docs.

## STAGE 1 — FOUNDATION

### S1_DEF — Stage Definition

#### 8. Service Contracts

##### 8.1 Core API (`services/core-api`)

Required endpoints:

1. `GET /health`
2. `GET /flags`
3. `POST /jobs`

Constraints:

1. `POST /jobs` accepts `JobRequest`.
2. Output must conform to `JobResult`.
3. Integration call to AI agent must fail safe and return deterministic queued fallback.

##### 8.2 AI Agent (`services/ai-agent`)

Required endpoints:

1. `GET /health`
2. `POST /jobs/run`

Constraints:

1. Input shape mirrors `JobRequest`.
2. Output shape mirrors `JobResult`.
3. Output must be deterministic for same input payload.

### S1_BLP — Blueprint Model (P1 scope)

#### 9. App Contract

##### 9.1 Web (`apps/web`)

Required behavior:

1. Has a Home surface.
2. Has a Health dashboard surface that queries `core-api /health`.
3. Uses `packages/ui-kit` primitives.
4. Respects feature flags with default OFF fallback.

### S1_INV — Repo Inventory Model

#### 10. Tooling Contract

`tools/health` must:

1. Run on Node with no external service dependencies.
2. Detect large files under `src/**` using a configurable max size.
3. Detect suspicious file patterns under `src/**`.
4. Print deterministic sorted report.
5. Exit `1` on violations, `0` otherwise.

`tools/scripts` must:

1. Provide local utility scripts used by root commands.
2. Avoid mutating state outside repository.

### S1_GATE — Functional Gates v1

#### 11. Testing and Smoke Standards

Minimum baseline checks:

1. Contracts schema generator check mode passes.
2. Health gate passes.
3. Core API smoke script can execute local request flow without external dependencies.

Test writing rules:

1. Prefer deterministic pure function tests first.
2. Keep network tests local loopback only.
3. Avoid clock-sensitive assertions unless time is injected.

### S1_POL — Policy Strictness (P1)

#### 12. Formatting and Linting

Node/TypeScript:

1. ESLint and Prettier configs are tracked in repo.
2. Script ordering in package manifests should be stable and logical.

Python:

1. `pyproject.toml` includes black/ruff stubs for local standardization.
2. Rules should be explicit; avoid global implicit ignores.

### S1_DEBT — Debt System v0

#### 13. Security and Secrets

Rules:

1. No secrets in committed files.
2. `.env` files are ignored by default.
3. Service defaults must be safe for local development.
4. No telemetry or external callbacks enabled by default.

### S1_IDX — INDEX_PRO Scope v0

#### 14. Dependency Rules

1. Keep dependencies minimal.
2. Pin explicit major/minor versions where possible.
3. Prefer built-in modules for scripts.
4. Avoid adding heavy framework dependencies to `packages/ui-kit`.

### S1_OUT — Output Minimum Contract

#### 15. Versioning and Compatibility

1. Contracts are backward-compatible unless major-version migration is documented.
2. Enum value removals require explicit migration notes.
3. Field renames require dual-read/dual-write period where practical.

### S1_FAIL — Failure Modes (P1 only)

#### 16. Pull Request Gate Checklist

Each change must prove:

1. Deterministic output maintained.
2. No prohibited artifacts in source trees.
3. Feature flags remain OFF by default unless explicitly approved.
4. Contract changes include generated schema updates.
5. Affected tests or smoke checks are updated.

### S1_PROM — Promotion Rules (P1)

#### 17. Incident Handling (Local)

If the repo health check fails:

1. Remove offending artifacts immediately.
2. Re-run `node tools/health/src/check_repo_health.mjs`.
3. Capture short root cause in `docs/NOTEBOOK.md` if recurring.

If schema drift appears between TypeScript and Python:

1. Freeze endpoint behavior to old compatible shape.
2. Regenerate schemas from `packages/contracts`.
3. Update Python models and tests.
4. Record compatibility notes in `docs/NOTEBOOK.md`.

## STAGE 2 — EXTRACTION & CORE

### S2_DEF — Stage Definition

#### 18. Enforcement Priority

Priority order for conflicts:

1. `docs/CONTRACT.md`
2. code-level tests and health scripts
3. README guidance
4. local preferences

Any exception requires documented rationale in `docs/NOTEBOOK.md` with date and owner.

### S2_MIG — Migration Rules

#### 19. Exceptions

No permanent exception exists at bootstrap.
Temporary exceptions must include:

1. exact scope
2. reason
3. expiration date
4. rollback plan

### S2_ANT — Anti-Garbage Enforcement

#### 20. Acceptance

By committing to this repository, contributors accept this contract.

Non-compliant changes are expected to be rejected until corrected.

### S2_NRG — Non-Regression Engine

### S2_ESC — Placeholder Escalation

### S2_SCOPE — Scope Overlap Enforcement

### S2_IMM — Contract Immutability Tier

### S2_PROM — Promotion Requirements

## STAGE 3 — INTELLIGENCE & AUTOMATION

### S3_DEF — Stage Definition

### S3_OBS — Observability Requirements

### S3_JOB — Job Governance Model

### S3_CAP — Capability Negotiation

### S3_AUTO — Deterministic Automation

### S3_EXC — Exception Tightening

### S3_PROM — Promotion Requirements

## STAGE 4 — OPERATING SYSTEM

### S4_DEF — Stage Definition

### S4_REL — Release Governance

### S4_SEC — Security Baseline

### S4_MOD — Module System Governance

### S4_AUD — Audit & Compliance

### S4_PROM — Promotion Requirements

## CROSS-STAGE SYSTEMS

### SYS_IDX — INDEX_PRO Full Schema

### SYS_BLP — Blueprint Schema

### SYS_GATE — Gate Schema

### SYS_DEBT — Debt Schema

### SYS_DOC — DocTree Schema

### SYS_RUN — Run-Level Schema

### SYS_LED — Ledger & Attestation Model

## RENDERING & OPERATOR UX

### UX_IDX — INDEX_PRO.md Contract

### UX_STA — STATUS Contract

### UX_NXT — NEXT Single Action Contract

### UX_TREE — Doc Unlock Tree Rendering

## EVOLUTION & VERSIONING

### EV_SCH — Schema Versioning

### EV_BLP — Blueprint Versioning

### EV_CON — Contract Change Flow

### EV_COMP — Backward Compatibility Rules


