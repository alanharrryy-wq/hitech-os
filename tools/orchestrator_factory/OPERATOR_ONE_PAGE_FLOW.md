
# Operator One-Page Flow

Use this page when the clock is loud and you need the shortest safe path from framework install to first integrated round.

## 0. Install and health check
Run these from the framework root:

```bash
python tools/execution_framework/smoke_framework_checks.py
python tools/execution_framework/check_framework_readiness.py
```

Do not launch chats until install status is `ready`.

## 1. Bootstrap the project baseline
Create the project baseline skeleton:

```bash
python tools/execution_framework/init_project.py   --project-id prj-example   --project-name "Example Project"   --initiative-type greenfield   --objective "Deliver one bounded objective"
```

Then complete these files under `ops/projects/<project_id>/`:
- `idea_intake.md`
- `homologation_record.md`
- `canonical_source_register.md`
- `contract_register.md`
- `project_manifest.json`

Update `configs/execution_framework/path_policies.json` with real runtime paths for this project.

Check bootstrap readiness:

```bash
python tools/execution_framework/check_framework_readiness.py --project-id prj-example
```

## 2. Open the run
Create the run and first round:

```bash
python tools/execution_framework/init_run.py   --project-id prj-example   --objective "Deliver one bounded objective"

python tools/execution_framework/init_round.py   --run-id run-prj-example-YYYYMMDD-01   --round-id rd-001
```

## 3. Generate packets and prompts
```bash
python tools/execution_framework/generate_work_packets.py   --run-id run-prj-example-YYYYMMDD-01   --round-id rd-001

python tools/execution_framework/generate_prompt_packets.py   --run-id run-prj-example-YYYYMMDD-01   --round-id rd-001
```

## 4. Launch chats
- Chat 0: governance plus mission control
- Chats 1 to 6: the six package chats

Give each package chat:
- its package folder
- frozen governance docs
- the project baseline under `ops/projects/<project_id>/`
- its generated work packet and prompt

Workers do **not** communicate directly with each other. All cross-package communication flows through governance-issued artifacts.

## 5. Collect bundles
Package chats return one deterministic bundle each and place them under:

`ops/runs/<run_id>/rounds/<round_id>/incoming/`

Each bundle must contain:
- `bundle_manifest.json`
- `package_report.json`
- `notes/summary.md`
- `payload/**`

## 6. Validate and accept
```bash
python tools/execution_framework/compute_overlap_report.py   --run-id run-prj-example-YYYYMMDD-01   --round-id rd-001

python tools/execution_framework/emit_acceptance_report.py   --run-id run-prj-example-YYYYMMDD-01   --round-id rd-001

python tools/execution_framework/build_integration_ready_summary.py   --run-id run-prj-example-YYYYMMDD-01   --round-id rd-001
```

If a package is rejected, generate retry prompts from the acceptance report. Do not improvise new scope.

## 7. Integrate only what is accepted
Apply only accepted bundles, in dependency order, and only after overlap and acceptance are known.

## 8. If anything feels fuzzy, stop
Common stop conditions:
- path ownership still looks generic or placeholder-like
- a worker needs a direct backchannel to another worker
- a frozen contract changed without versioning and a decision record
- an exception is being requested verbally instead of through a waiver record
