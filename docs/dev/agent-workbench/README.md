<!-- agent-workbench-rescue-managed -->
# Agent Workbench

This folder is the repo-native coordination workspace for documentation-only parallel agent work in hitech-os.

## Source of Truth

`MASTER_STATUS_BOARD.md` is the operational source of truth. Agent-local files are evidence until reconciled by the Coordinator.

## Global Rules

- Do not modify product code from workbench branches.
- Do not merge directly into main.
- Do not force-push.
- Do not delete branches.
- Do not treat CAPATCH as active work.
- CAPATCH remains CLOSED / DO_NOT_MERGE and may only appear as legacy/evidence.
- Each agent must work only inside its assigned folder.
- Global workbench files are Coordinator-only.

## Core Documents

- MASTER_STATUS_BOARD.md
- PARALLEL_WORK_QUEUE.md
- HANDOFF_PROMPTS.md
- AGENT_REPORT_RECONCILIATION.md
- MERGE_READINESS_CHECKLIST.md
- COORDINATION_LOCK.md
- AGENT_SESSION_LEDGER.md
- EVIDENCE_POLICY.md
- STATE_TRANSITIONS.md

## Current Phase

Documentation, coordination, and reconciliation only. No product-code work is authorized.
