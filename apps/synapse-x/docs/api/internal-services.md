# Internal Services API

## Suggested Service Surface
- scan_sources()
- detect_changes()
- ingest_file(path)
- normalize_record(raw)
- store_record(record)
- rebuild_timeline(session_id)
- search_sessions(query, filters)
- get_metrics()
- repair_system()

## Notes
This is an internal boundary, not necessarily a public API.
