# HITECH OS — KERNEL CONTEXT

## PROJECT_ID
- Repository: `hitech-os` (from root `package.json`).
- Canonical repo contract file present: `docs/CONTRACT.md`.
- Expected root files missing: `CONTRACT.md`, `STATE.md`, `NEXT.md`, `CHANGES.md`.
- Factory contract/changelog sources present: `docs/factory/CONTRACT.md`, `docs/factory/CHANGES.md`.

## BASELINE
- Baseline Tag: no git tag points at `HEAD`; factory version label is `2.0.0-block-b`.
- Baseline Commit: `eb6062f14893639690e13bd0333a1883aa64e0ca`.
- Factory Status: `PASS` (`STATUS.json`, block `B`).
- Determinism Verified: `PASS` (documented determinism integration checks and smoke determinism checks pass).
- Test Status: documented required factory test checks in `STATUS.json` are `PASS`.

## CURRENT_PHASE
`Block B Industrialization` for Multi-Codex Factory hardening, with prior `Block A Hardening` also recorded in `docs/factory/CHANGES.md`.

## SYSTEM_ARCHITECTURE_MODEL
- Repo type: deterministic PNPM monorepo (`apps/*`, `services/*`, `packages/*`, `tools/*`) with mixed TypeScript and Python services.
- Tooling stack: PNPM workspaces, Turborepo, Node scripts, Python factory tooling, JSON Schema contracts.
- Orchestration model: Python-first factory CLI (`python -m tools.codex.factory`) with staged execution and append-only ledger recording.
- Modularity principles: explicit contract boundaries, schema-validated artifacts, scoped worker ownership, feature flags default `false`, deterministic output ordering.

## FACTORY_MODEL
Describe the Multi-Codex Factory:
- A_core: `A_worker` primary domain-scoped bundle producer.
- B_tooling: `B_worker` secondary surface/UX-scoped bundle producer.
- C_features: `C_worker` tooling/infrastructure-scoped bundle producer.
- D_validation: `D_worker` validation/hardening-scoped bundle producer.
- Z_aggregator: `Z_integrator` merges, validates, and reports only; it does not create product features.

Include execution order and isolation model.
- Execution order: `preflight -> launch -> bundle-validate -> integrate -> summary` (`oneshot`).
- Isolation model: worker worktrees are under `tools/codex/worktrees/<RUN_ID>/<WORKER>`, lock files are under `tools/codex/runs/<RUN_ID>/locks/`, and Z writes are restricted to `tools/codex/runs/<RUN_ID>/`.

## INVARIANTS (NON-NEGOTIABLE)
- Run artifacts are constrained to `tools/codex/runs/<RUN_ID>/` with required worker/integrator artifact sets.
- Status semantics are enforced as `PASS`, `BLOCKED`, `FAIL` with exit codes `0`, `2`, `1` respectively.
- Worker and integrator status schemas require `PENDING|PASS|BLOCKED|WARN|FAIL` enums.
- Ledger is append-only JSONL at `tools/codex/runs/factory_ledger.jsonl` with signature file `tools/codex/runs/factory_ledger.sha256`.
- Ledger events must validate against `tools/codex/schemas/run_ledger_event.schema.json`.
- Run IDs follow `<kind>_<YYYYMMDD_HHMMSS>_<BASE_REF_HASH8>_<NNN>` and sequence from existing ledger entries.
- Overlap/scope/path validation blocks integration on conflicts, hidden overlaps, invalid paths, and scope violations.
- Path guarding rejects absolute/traversal/UNC/drive/colon path escapes and protects `.git`, `.env`, and `.github/workflows`.
- Feature flags default to `false` in contract/config surfaces.

## NO_GO_ZONES
- Any write by `Z_integrator` outside `tools/codex/runs/<RUN_ID>/`.
- Any worker writing into another worker bundle directory.
- Protected paths (`.git/**`, `.env*`, `.github/workflows/**`) and path traversal/absolute path targets.
- Files outside a worker's declared scope lock and denylist rules.
- Z-integrator behavior that invents product features instead of merge/validate/report.
- Dump/archive/back-up style artifacts under `src/**`.

## DETERMINISM_POLICY
- JSON artifacts are written with stable key ordering.
- File/path lists are sorted before output (overlaps, changes, attestations, reports).
- Time fields are UTC-based; run identity generation is deterministic from kind, timestamp token, base-ref hash, and ledger sequence.
- Ledger queries are deterministically ordered by `ts_utc`, then `event_type` (with stable tie-breakers).
- Determinism tests normalize run IDs/timestamps before comparing outputs.
- Feature flags remain off by default unless explicitly overridden.

## CURRENT_KNOWN_PACKAGES
- `hitech-os`
- `@hitech/web`
- `@hitech/demo-engine`
- `@hitech/core-api`
- `@hitech/ai-agent`
- `@hitech/contracts`
- `@hitech/ui-kit`
- `@hitech/tooling`
- `@hitech/health`
- `@hitech/scripts`
- `tools.codex.factory`

## HEALTH_STATUS
- Factory doctor currently reports `PASS` with `blocked=0` and `warnings=0`.
- `tools/health/src/check_repo_health.mjs` currently reports zero violations and zero schema drift findings.
- Root `STATUS.json` reports `PASS` for Block B required checks and factory validation commands.
- CI workflow exists at `.github/workflows/factory.yml` with Windows-primary and Ubuntu-experimental matrix execution for doctor, contracts, oneshot dry-run, tests, determinism check, and smoke.

## NEXT_IMMEDIATE_ACTION
- `NEXT.md` is missing at repo root.
- No NEXT source value is available from the required `NEXT.md` file.

## LONG_TERM_DIRECTION
- Maintain a deterministic, contract-first, local-first monorepo operating model as defined in `docs/CONTRACT.md`.
- Maintain Multi-Codex Factory execution with strict scope locking, schema validation, overlap/scope enforcement, append-only ledgering, and attestation evidence.
- Keep additive hardening workflow and operator/audit documentation under `docs/factory/` as the operational baseline.

## CONTEXT_USAGE_RULE
Any new ChatGPT or Codex instance must read this file before proposing or applying repository changes.
