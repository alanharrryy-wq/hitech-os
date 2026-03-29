
# Install, Bootstrap, Run, and Round Separation

The framework stays safe only when these four layers do not blur together.

## 1. Framework installation
What it is:
- placing the framework in a repo or workspace
- verifying the reusable foundation exists
- verifying the tactical tools run

Where it lives:
- framework root
- `00-governance-core/`
- package folders
- `configs/`, `docs/`, `prompts/`, `schemas/`, `tools/`, `tests/`, `templates/`

What it must not contain:
- project-specific truth
- run-specific decisions
- round-specific packets

## 2. Project bootstrap and homologation
What it is:
- converting a raw initiative into a governed project baseline
- freezing the first credible project truth

Where it lives:
- `ops/projects/<project_id>/`

Typical artifacts:
- `project_manifest.json`
- `idea_intake.md`
- `homologation_record.md`
- `canonical_source_register.md`
- `contract_register.md`

## 3. Run execution
What it is:
- opening one bounded execution campaign for one bounded objective

Where it lives:
- `ops/runs/<run_id>/`

Typical artifacts:
- `run_manifest.json`
- decisions
- accepted evidence

## 4. Round execution
What it is:
- one tactical synchronization window inside a run

Where it lives:
- `ops/runs/<run_id>/rounds/<round_id>/`

Typical artifacts:
- `round_manifest.json`
- packets
- prompts
- incoming bundles
- validation reports
- acceptance report
- integration readiness summary

## Hard separation rules
- Templates are never canonical until instantiated in a project or run location.
- Project baseline files do not belong under `00-governance-core/`.
- Run evidence does not belong under `ops/projects/`.
- Worker bundles are never stored as if they were frozen constitutional truth.
