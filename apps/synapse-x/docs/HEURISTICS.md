# Heuristics Guide

## Goal
Make the backend correlate messy operational artifacts into stable sessions, timestamps, errors and tool signals before any UI is added.

## Session Identity Priority
1. Explicit structured keys like `session_id`, `run_id`, `conversation_id`, `rollout_id`.
2. Textual patterns inside payload content.
3. Filename patterns such as `rollout-2026-04-05`.
4. Derived fallback from filename when nothing else is trustworthy.

Each record stores:
- `session_strategy`
- `session_confidence`
- `correlation_score` when a weak record is adopted by a stronger anchor

## Timestamp Priority
1. Explicit structured timestamp fields.
2. Per-item timestamps in list payloads.
3. Timestamps parsed from text body.
4. Time-only values combined with date extracted from filename.
5. File mtime as last resort.

## Error Heuristics
- captures explicit error-like fields from structured payloads
- scans rows and lines for failure vocabulary
- groups short traceback and stack continuation blocks
- infers `error_type` from exception class or exit code
- classifies severity into `fatal`, `error`, or `warning`
- deduplicates repeated error blocks using semantic signatures rather than raw text only
- avoids double-counting structured JSON payloads as if they were raw log lines

## Tool Heuristics
- normalizes aliases such as `python -m pytest` -> `pytest`
- extracts tools from structured fields like `tool`, `command`, `argv`
- scans text lines for known tool signatures
- keeps per-occurrence timestamps and raw references

## Cross-File Correlation
When a record has low-confidence session identity, the backend now tries to correlate it against:
- stronger records in the same ingest batch
- recent existing records already stored in SQLite

The correlation score uses:
- same or near date bucket
- temporal proximity window
- overlapping `error_types`
- overlapping `error_signatures`
- overlapping `tool_names`
- overlapping filename/stem tokens
- overlapping `signal_keywords`
- overlapping `topic_tokens`
- source family similarity
- summary signature similarity

If the score is strong enough:
- the ambiguous record adopts the best anchored session
- its events/errors/tools inherit that session ID
- metadata records correlation lineage and score

If no anchor exists but several ambiguous records clearly belong together:
- they are clustered
- a deterministic `cluster-*` session ID is generated from date + signal fingerprint

## Correlation Metadata
Each normalized record stores:
- `date_bucket`
- `time_bucket`
- `source_family`
- `stem_tokens`
- `signal_keywords`
- `topic_tokens`
- `error_types`
- `error_signatures`
- `tool_names`
- `summary_signature`
- `session_root`

## Session Intelligence
At session-detail time, the backend also computes:
- session confidence score and label
- error groups by semantic signature
- tool summary counts
- phase breakdown
- enriched timeline entries with `phase`, `severity`, `headline`, `count`

This keeps the eventual PySide6 layer thin: it should render and filter, not reinvent inference.


## Session Similarity and Root Cause Intelligence
At session-detail and metrics time, the backend now also computes:
- related sessions scored by overlap in error groups, tools, topics, phases and source families
- sequence patterns such as `build > test > failure` or `failure > repair`
- probable root causes ranked into categories like `ui_or_rendering`, `build_or_configuration`, `network_or_remote`, `parsing_or_data`, and `runtime_crash`

This gives the eventual UI enough structure to show:
- “you've seen this kind of crash before”
- “this session followed the usual build -> test -> fail arc”
- “most likely root cause is UI/rendering with RuntimeError evidence”

## Storage Integrity Improvement
Re-ingesting the same source no longer inflates `sessions.source_count`.
The storage layer now refreshes session rollups after replacing records from an existing source path, so session counts and first/last timestamps stay honest.
