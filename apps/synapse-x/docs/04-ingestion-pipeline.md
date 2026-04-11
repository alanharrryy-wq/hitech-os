# Ingestion Pipeline

## Supported Inputs v1
- JSON
- JSONL
- text logs
- reports
- codex-like session artifacts

## Incremental Rules
Process only:
- new files
- changed files
- new appended lines for append-only sources

## Pipeline Stages
1. source scan
2. change detection
3. parser dispatch
4. normalization
5. persistence
6. indexing
7. metrics refresh

## Error Handling
Bad files must be isolated, logged and marked without breaking the whole run.
