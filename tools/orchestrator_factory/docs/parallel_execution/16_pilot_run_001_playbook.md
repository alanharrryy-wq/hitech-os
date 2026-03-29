
# Pilot Run-001 Playbook

Use this playbook for the first controlled real pilot.

## Pilot intent
The pilot proves that the framework can move from homologated project baseline to accepted bundles and one integrated round without chat chaos.

## Recommended pilot shape
Choose a bounded objective that touches two or three packages, not all six at maximum depth.

Good pilot examples:
- one auth-facing service contract plus one client integration
- one persistence change plus one service orchestration update plus one QA gate
- one bugfix campaign with explicit rollback and observability evidence

## Pre-pilot checklist
1. framework install readiness is `ready`
2. project bootstrap readiness is `ready`
3. runtime path policies are project-real, not starter placeholders
4. one bounded objective is written into the run manifest
5. one round only: `rd-001`
6. one bundle per package maximum

## Suggested command sequence
```bash
python tools/execution_framework/smoke_framework_checks.py
python tools/execution_framework/check_framework_readiness.py
python tools/execution_framework/init_project.py   --project-id <project_id>   --project-name "<project_name>"   --initiative-type <initiative_type>   --objective "<run_objective>"
python tools/execution_framework/check_framework_readiness.py --project-id <project_id>
python tools/execution_framework/init_run.py --project-id <project_id> --objective "<run_objective>"
python tools/execution_framework/init_round.py --run-id <run_id> --round-id rd-001
python tools/execution_framework/generate_work_packets.py --run-id <run_id> --round-id rd-001
python tools/execution_framework/generate_prompt_packets.py --run-id <run_id> --round-id rd-001
```

After worker bundles arrive:

```bash
python tools/execution_framework/compute_overlap_report.py --run-id <run_id> --round-id rd-001
python tools/execution_framework/emit_acceptance_report.py --run-id <run_id> --round-id rd-001
python tools/execution_framework/build_integration_ready_summary.py --run-id <run_id> --round-id rd-001
python tools/execution_framework/check_framework_readiness.py --project-id <project_id> --run-id <run_id> --round-id rd-001
```

## Pilot success criteria
- every package stayed inside ownership
- no direct worker-to-worker coordination was needed
- acceptance decisions were artifact-backed
- at least one accepted bundle was integrated in dependency order
- any rejection produced a precise retry prompt
- any exception used a waiver record

## Stop the pilot if
- path ownership is still being negotiated during execution
- a frozen contract changes without a version trail
- mission control starts issuing oral-history instructions instead of artifacts
