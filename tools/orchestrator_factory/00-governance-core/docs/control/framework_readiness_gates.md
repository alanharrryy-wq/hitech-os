
# Framework Readiness Gates

These gates stop the operator from jumping from a copied framework into live execution without the missing middle.

## Gate model
Each gate returns one of:
- `ready`
- `ready_with_conditions`
- `not_ready`

A later gate never overrides a failed earlier gate.

## Gate 0: Install readiness
The framework is install-ready when:
- the expected directories exist
- the constitutional docs are present
- the tactical tools are present
- the nested starter zip exists
- canonical-tree junk is absent from the framework tree

Evidence:
- `python tools/execution_framework/smoke_framework_checks.py`
- `python tools/execution_framework/check_framework_readiness.py`

## Gate 1: Bootstrap readiness
The project is bootstrap-ready when:
- `ops/projects/<project_id>/` exists
- `project_manifest.json` exists
- `idea_intake.md` exists
- `homologation_record.md` exists
- `canonical_source_register.md` exists
- `contract_register.md` exists
- runtime path policies have been replaced with project-real paths
- package topology and success conditions are coherent enough to freeze

## Gate 2: Run-001 readiness
The first run is ready to launch when:
- the project baseline is frozen enough to execute
- `run_manifest.json` exists
- `rd-001` exists
- work packets exist for every active package
- prompts exist for every active package
- the governance chat owns mission control by default or delegation has been recorded
- inter-chat communication policy has been acknowledged

## Gate 3: Bundle acceptance readiness
A round is ready to accept bundles when:
- the incoming folder exists
- the reports folder exists
- the bundle contract is frozen for this run
- overlap detection is available
- acceptance reporting is available
- exception handling is defined through the waiver policy

## Gate 4: Integration readiness
A round is integration-ready when:
- accepted packages are known
- rejected packages are known
- apply order is known
- open conflicts are either closed or explicitly waived
- contract versions consumed by the round are visible
- residual risk and follow-up actions are recorded

## Gate discipline
- Do not skip a failed gate with operator confidence alone.
- `ready_with_conditions` still requires the conditions to be written and tracked.
- Emergency corrections still require a waiver record and a decision trail.
