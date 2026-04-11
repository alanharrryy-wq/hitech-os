# Data Model

## Core Entities
- file
- session
- event
- error
- tool_usage
- ingest_run
- pattern
- metrics_snapshot

## Session
- session_id
- first_seen_at
- last_seen_at
- source_count
- status

## Event
- event_id
- session_id
- timestamp
- category
- message
- tool_name
- raw_ref

## Error
- error_id
- session_id
- timestamp
- error_type
- message
- severity
- raw_ref

## File Tracking
Track hash, size, mtime and last ingest status to support incremental execution.
