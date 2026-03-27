
# Documentation Layering

## Layer 0: Constitution
Location: `00-governance-core/`

Purpose:
- define rules
- define authority
- define how ambiguity becomes governed structure

## Layer 1: Project baseline
Location:
- `ops/projects/<project_id>/`

Typical artifacts:
- project manifest
- idea intake
- homologation record
- canonical source register
- contract register
- package topology overrides if any

Purpose:
- describe this specific project inside the constitutional model

## Layer 2: Package contracts
Location: package folders `01-...` through `06-...`

Purpose:
- package-local responsibilities
- deliverables
- dependencies
- handoff and acceptance rules

## Layer 3: Run control
Location:
- `ops/runs/<run_id>/run_manifest.json`
- `ops/runs/<run_id>/rounds/<round_id>/round_manifest.json`

Purpose:
- define what is active now

## Layer 4: Tactical packets and prompts
Location:
- generated work packets
- generated prompts

Purpose:
- operationalize frozen inputs for one round

## Layer 5: Outputs and evidence
Location:
- bundles
- validation reports
- overlap reports
- acceptance reports
- integration summaries

Purpose:
- prove what happened and whether it is safe to integrate

## Layer 6: Templates and examples
Location:
- `templates/`
- `examples/`

Purpose:
- accelerate future work

Rule:
Templates and examples never become canonical until instantiated, reviewed, and frozen in a higher layer.
