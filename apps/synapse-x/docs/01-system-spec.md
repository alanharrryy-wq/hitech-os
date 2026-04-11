# System Specification

## Purpose
Build a local memory engine for sessions, logs and reports.

## Functional Requirements
- Detect new or modified files
- Support incremental ingestion
- Normalize records into a canonical schema
- Persist sessions, events, errors and tools
- Provide textual search and filters
- Reconstruct timelines
- Compute metrics
- Support repair and full ingest modes

## Non-Functional Requirements
- Local-first
- Idempotent operations
- Fault-tolerant ingestion
- Extensible parser system
- Traceability to raw sources

## Canonical Record
```json
{
  "session_id": "string",
  "timestamp": "ISO-8601",
  "type": "session | log | report",
  "source_path": "string",
  "source_hash": "string",
  "events": [],
  "errors": [],
  "tools": [],
  "metadata": {}
}
```

## Acceptance Criteria
- Ingestion does not reprocess unchanged files
- Search can find sessions and errors
- Timeline view is reconstructable
- Repair fixes indexes and failed state when possible
