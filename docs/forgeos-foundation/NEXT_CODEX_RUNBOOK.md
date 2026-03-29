# NEXT_CODEX_RUNBOOK

## Purpose

Provide a deterministic start protocol for the next Codex run that will execute a clean ForgeOS reconstruction using the foundation bundle.

## Authoritative Reading Order

Read and obey in this exact order:

1. `README_START_HERE.md`
2. `00_PLATFORM_CONSTITUTION.md`
3. `01_FORGEOS_MASTER_BLUEPRINT.md`
4. `02_KERNEL_BOUNDARIES.md`
5. `05_CONTRACTS_CATALOG.md`
6. `06_HOST_INTEGRATION_SPEC.md`
7. `09_RECONSTRUCTION_ORDER.md`
8. `10_ACCEPTANCE_GATES.md`
9. `11_CODEX_EXECUTION_INSTRUCTIONS.md`

Use as support (not authority unless explicitly escalated):

- `03_SHARED_CAPABILITIES_CATALOG.md`
- `04_PRODUCT_SKELETON_TEMPLATE.md`
- `07_PACKAGING_AND_RELEASE_SPEC.md`
- `08_BOUNDARY_ENFORCEMENT_RULES.md`
- `12_ASSUMPTIONS_AND_DECISION_LOG.md`
- `matrices/*`
- `templates/*`
- `appendix/*`

## Non-Negotiable Execution Rules

- Treat legacy as evidence, never as implementation template.
- Implement contracts before product logic.
- Keep host free of product semantics and domain logic.
- Eliminate string-based command routing and eventing in target design.
- Keep lifecycle explicit and complete (init, activate, suspend, dispose).
- Enforce explicit state authority and persistence authority per boundary docs.
- Reject hidden coupling (service locator usage and host scraping patterns).

## Phase-By-Phase Protocol

Follow `09_RECONSTRUCTION_ORDER.md` exactly:

1. Phase 0: truth capture
2. Phase 1: kernel definition
3. Phase 2: contract system
4. Phase 3: shared capabilities definition
5. Phase 4: host shell rebuild
6. Phase 5: product skeleton establishment
7. Phase 6: product migrations (internal order is mandatory)
8. Phase 7: packaging hardening
9. Phase 8: visual/system polish

No phase transition is allowed without satisfying the relevant checks in `10_ACCEPTANCE_GATES.md`.

## First Run Checklist

Before writing implementation code:

1. Confirm all authoritative docs were read in order.
2. Produce an explicit assumptions list derived from `12_ASSUMPTIONS_AND_DECISION_LOG.md`.
3. Declare target ownership map (kernel, commons, products).
4. Declare contract IDs and versions that will be introduced first.
5. Declare lifecycle authority and teardown criteria for each product module.
6. Declare state authority matrix and persistence boundaries.

## Mandatory Evidence for Every Deliverable

Each execution step must publish:

- `STATUS`
- `FILES_CHANGED`
- `DIFF summary`
- `TEST_COMMAND` (if tests were run)
- `TEST_RESULT` (if tests were run)

## Stop Conditions

Stop and request operator input only when:

- A required authority document is missing or contradictory.
- A dependency addition is required and not approved.
- A gate in `10_ACCEPTANCE_GATES.md` fails.

Proceed with strong defaults in all other cases, as defined by `11_CODEX_EXECUTION_INSTRUCTIONS.md`.
