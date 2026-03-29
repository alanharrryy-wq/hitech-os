# PHASE 0 TRUTH CAPTURE

## Status

PASS

## Objective

Freeze evidence and classify legacy assets by target owner and destination before implementation work starts.

## Inputs used

- `F:/repos/hitech-os/docs/forgeos-foundation/00_PLATFORM_CONSTITUTION.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/01_FORGEOS_MASTER_BLUEPRINT.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/02_KERNEL_BOUNDARIES.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/05_CONTRACTS_CATALOG.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/06_HOST_INTEGRATION_SPEC.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/09_RECONSTRUCTION_ORDER.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/10_ACCEPTANCE_GATES.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/11_CODEX_EXECUTION_INSTRUCTIONS.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/12_ASSUMPTIONS_AND_DECISION_LOG.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/appendix/legacy_to_target_mapping.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/appendix/legacy_pathologies_catalog.md`
- `F:/repos/hitech-os/docs/forgeos-foundation/matrices/*.md`

## Legacy subsystem classification

| Legacy area | Target owner | Target layer | Destination |
| --- | --- | --- | --- |
| `main.py` + `main_window.py` composition | Forge Kernel | Kernel | REBUILD |
| `event_bus.py` + `command_dispatcher.py` | Forge Kernel | Kernel | REBUILD_AS_CONTRACT_RUNTIME |
| `service_container.py` global locator | None | N/A | DELETE |
| Host shell (`layout`, `dock`, workspace shell) | Forge Kernel Host Shell | Kernel | REBUILD |
| Preferences/policy runtime | Forge Commons `config_policy` | Commons | EXTRACT_AND_PROMOTE |
| Diagnostics and health surfaces | Forge Commons `diagnostics` | Commons | EXTRACT_AND_PROMOTE |
| Process supervision runtime (generic slice) | Forge Commons `process_execution` | Commons | SPLIT_AND_PROMOTE |
| Run/history ledger (generic slice) | Forge Commons `history_runs` | Commons | SPLIT_AND_PROMOTE |
| Repo analysis domain | Product `repo_analyzer` | Product | EXTRACT |
| Cloudflare Guardian domain | Product `cloudflare_guardian` | Product | EXTRACT |
| Orchestrator Bridge domain | Product `orchestrator_bridge` | Product | EXTRACT |
| Dev/demo plugins and legacy loaders | None | N/A | QUARANTINE_OR_DELETE |
| Local residues (`__pycache__`, `.pytest_cache`, ad-hoc json) | None | N/A | DELETE |

## Pathologies frozen as constraints

- Hypertrophic composition root (`main_window.py`).
- Host contamination with product semantics.
- String-based eventing and command routing.
- Incomplete plugin manager lifecycle and shutdown.
- Fragmented persistence authority.
- Hidden coupling through service locator and host scraping.

## Assumptions adopted for execution

Taken from `12_ASSUMPTIONS_AND_DECISION_LOG.md`:

- A-01 through A-08 are accepted as strong defaults for bootstrap.
- No binary backward compatibility is assumed for legacy plugin architecture.
- Initial product wave is fixed: `repo_analyzer`, `cloudflare_guardian`, `orchestrator_bridge`.

## Lifecycle authority baseline

- Kernel governs package lifecycle (`discovered -> registered -> prepared -> active -> suspended -> faulted -> disposing -> disposed`).
- Commons capability owners govern their runtime internals under kernel lifecycle contracts.
- Each product must declare teardown for views, subscriptions, tasks, local stores, and external processes.

Reference: `F:/repos/hitech-os/forgeos/governance/matrices/lifecycle_matrix.md`.

## State authority baseline

State authority is locked to owner-by-slice.

Mandatory rule:

- Host/kernel stores are neutral and never contain product domain state.

Reference: `F:/repos/hitech-os/forgeos/governance/matrices/state_authority_matrix.md`.

## Contract seed baseline

Initial contract IDs and version seed were defined in:

- `F:/repos/hitech-os/forgeos/governance/contracts/INITIAL_CONTRACT_SET.md`

## Done criteria check

| Criterion | Result | Evidence |
| --- | --- | --- |
| Every legacy subsystem has a destination | PASS | Classification table above + `legacy_to_target_mapping.md` |
| Pathologies captured as hard constraints | PASS | Section "Pathologies frozen as constraints" |
| Ownership/state/lifecycle authority defined | PASS | Governance matrices copied and referenced |
| Contract-first sequence prepared | PASS | `INITIAL_CONTRACT_SET.md` + `RECONSTRUCTION_STATUS.md` |

## Exit decision

Phase 0 is closed. Phase 1 (`kernel definition`) may start.
