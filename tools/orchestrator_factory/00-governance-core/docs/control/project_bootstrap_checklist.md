
# Project Bootstrap Checklist

Use this checklist to start a new project without skipping the hard parts.

## Install gate
- framework root is present
- `ops/projects/` exists
- `ops/runs/` exists
- tactical tools are present
- canonical tree is clean of runtime junk
- `python tools/execution_framework/smoke_framework_checks.py` passes

## Before any package chat opens
- raw idea captured
- project type identified: greenfield, migration, refactor, debugging campaign, modernization, or mixed
- repo reality described
- constraints captured
- success shape written in plain language
- obvious non-goals written down

## Homologation gate
- `project_id` chosen
- `ops/projects/<project_id>/` created
- default six-package topology confirmed or override recorded
- runtime path ownership draft created
- canonical source register drafted
- contract register drafted
- dictionary extensions approved if needed
- first `run_id` chosen or proposed
- first run objective written

## Governance freeze gate
- naming conventions confirmed
- path ownership matrix confirmed
- dependency graph confirmed
- change budgets confirmed
- review model confirmed
- merge and handoff protocol confirmed
- prompt usage model confirmed
- inter-chat communication policy confirmed
- waiver and exception policy confirmed
- contract versioning policy confirmed

## First-run gate
- run folder initialized
- `rd-001` initialized
- active path policies updated for real runtime paths
- work packets generated
- prompts generated
- six package chats launched
- `python tools/execution_framework/check_framework_readiness.py --project-id <project_id> --run-id <run_id> --round-id rd-001` reviewed

## Integration gate
- bundle validation complete
- overlap report complete
- acceptance report complete
- integration order clear
- unresolved blockers either closed or escalated
- any active waiver is written and approved

## Closeout gate
- decision records updated
- residual risk documented
- next round or run closeout decision recorded
- downstream consumers notified
