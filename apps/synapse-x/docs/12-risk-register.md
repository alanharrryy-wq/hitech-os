# Risk Register

## Key Risks
- ambiguous session correlation
- inconsistent timestamps
- huge log files
- partially corrupted JSONL
- duplicate ingestion
- UI blocking on long-running jobs
- FTS drift after repair or full ingest

## Mitigations
- strict file tracking
- tolerant parsers
- explicit repair path
- async or decoupled job execution
- clear diagnostics
