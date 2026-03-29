# Tactical Parallel Execution Subsystem

This document explains the generalized tactical subsystem donated primarily by Zip B and subordinated to the constitutional layer.

## Purpose

The tactical subsystem turns a governed execution model into repeatable operational mechanics.

It covers:
- rounds or phases
- work packets
- worker bundle format
- bundle validation
- overlap detection
- acceptance evaluation
- retry loops
- integration readiness
- governance-as-mission-control mechanics
- prompt choreography

## Tactical components

| Component | Primary file(s) |
|---|---|
| architecture overview | `docs/parallel_execution/00_architecture_overview.md` |
| tactical operating model | `docs/parallel_execution/01_operating_model.md` |
| round protocol | `docs/parallel_execution/02_round_protocol.md` |
| work packet model | `docs/parallel_execution/03_work_packet_model.md`, `schemas/execution_framework/work_packet.schema.json` |
| ownership model | `docs/parallel_execution/04_ownership_map_model.md`, `configs/execution_framework/path_policies.json` |
| acceptance rubric | `docs/parallel_execution/05_acceptance_rubric.md`, `schemas/execution_framework/acceptance_result.schema.json` |
| bundle contract | `docs/parallel_execution/06_bundle_contract.md`, `schemas/execution_framework/bundle_manifest.schema.json`, `schemas/execution_framework/package_report.schema.json` |
| failure and retry | `docs/parallel_execution/07_failure_retry_playbook.md`, `prompts/execution_framework/retry_prompt.md` |
| naming | `docs/parallel_execution/08_naming_conventions.md` |
| operator handoff | `docs/parallel_execution/09_operator_handoff.md`, `10_chat_operator_playbook.md` |
| first-round bootstrap | `docs/parallel_execution/11_run_round_01.md` |
| subsequent rounds | `docs/parallel_execution/12_run_round_n.md` |
| integration readiness | `docs/parallel_execution/13_integration_readiness.md`, `build_integration_ready_summary.py` |
| prompt choreography | `docs/parallel_execution/14_prompt_choreography.md`, prompt folder |
| repo-shape profiles | `docs/parallel_execution/15_repo_shape_profiles.md` |

## Core tooling

- `init_run.py`
- `init_round.py`
- `generate_work_packets.py`
- `generate_prompt_packets.py`
- `validate_worker_bundle.py`
- `compute_overlap_report.py`
- `emit_acceptance_report.py`
- `prepare_next_round_prompts.py`
- `package_round_artifacts.py`
- `dry_run_bundle.py`
- `apply_validated_bundle.py`
- `enforce_ownership.py`
- `smoke_framework_checks.py`

## Tactical rules

1. Tactical files cannot redefine package ownership.
2. Tactical prompts cannot widen scope beyond the current work packet.
3. Bundle validation happens before integration.
4. Overlap detection happens before acceptance.
5. Retry prompts must reference the last failed acceptance result, not improvise new scope.
6. Examples remain non-canonical until homologated into a project.

## Default operating pattern

The default pattern is:
- governance chat creates the run
- governance chat freezes the round
- six package chats execute package work packets
- each package returns one bundle
- governance validates, scores, accepts or rejects, and prepares the next round


## Additive pilot hardening

| Component | Primary file(s) |
|---|---|
| project baseline bootstrap | `tools/execution_framework/init_project.py`, `ops/projects/README.md` |
| readiness checker | `tools/execution_framework/check_framework_readiness.py`, `schemas/execution_framework/readiness_report.schema.json` |
| waiver support | `templates/execution_framework/run/waiver_record.template.md`, `schemas/execution_framework/waiver_record.schema.json` |
| pilot run playbook | `docs/parallel_execution/16_pilot_run_001_playbook.md` |
| canonical tree hygiene enforcement | `configs/execution_framework/canonical_tree_excludes.json`, `tools/execution_framework/smoke_framework_checks.py` |
