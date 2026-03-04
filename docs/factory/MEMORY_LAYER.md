# MEMORY_LAYER

## Purpose

`tools/codex/memory/` stores durable learning across runs to avoid repeating failures and to bias fallback tasks toward higher-value automation work.

## Files

- `RUN_HISTORY.json`
- `TECH_DEBT.json`
- `FAIL_PATTERNS.json`
- `SUCCESS_PATTERNS.json`

## Update Workflow

1. Initialize memory files once:
   - `python tools/codex/factory/memory_layer.py init`
2. Record each run closeout:
   - `python tools/codex/factory/memory_layer.py record-run --run-id <RUN_ID>`

## Data Rules

1. Files are JSON, append/update only, deterministic ordering.
2. `run_id` is the primary key for run history rows.
3. Pattern counters are cumulative and track evidence snippets.
4. Tech debt entries are created from blocked run blockers.
