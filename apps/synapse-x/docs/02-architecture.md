# Architecture

## Modules
- Ingestion Engine
- Parser + Normalizer
- Storage Layer
- Indexing Layer
- Intelligence Layer
- UI Layer
- Watcher / Scheduler

## High-Level Flow
1. Scan configured sources
2. Detect changes
3. Parse based on source type
4. Normalize to canonical records
5. Store in SQLite / cache / raw
6. Reindex affected entities
7. Refresh metrics and UI state

## Design Principles
- SQLite is the source of truth
- Cache accelerates, but does not define truth
- Raw retention preserves traceability
- Repair operations must be reusable and explicit
- UI must stay decoupled from long-running ingestion jobs
