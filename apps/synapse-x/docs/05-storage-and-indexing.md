# Storage and Indexing

## Storage Strategy
- SQLite as system of record
- JSON cache for quick access
- RAW storage or references for source traceability

## Indexing Strategy
- standard indexes for session_id, timestamps and types
- FTS for text search over events, errors and relevant metadata

## Operational Notes
- full ingest can rebuild indexes
- repair can revalidate DB integrity and reindex text search
