# Code Atlas Legal / Investor Readiness UI

The Legal panel is opened from the main Code Atlas window through the
**Legal / Inversionista** button.

## Execution model

- Code Atlas launches the installed legal backend through one `QProcess`.
- The backend launches one external evidence stage at a time.
- The active evidence stage may use controlled internal workers and shards.
- The UI remains responsive because evidence collection does not run on the Qt event thread.

## Profiles

- `plan`: authority and stage plan only.
- `static`: CTX legal baseline with source, asset and SQLite schema metadata.
- `full`: static baseline followed by redacted Mamastrophic runtime evidence.
- `runtime-only`: redacted Mamastrophic evidence only.

## Cooperative cancellation

The stop button writes a cancel marker. The current stage is allowed to finish,
then the backend packages the partial result and does not start another stage.
It does not kill ports, servers or unrelated processes.

## Output

Coordinator ZIPs are written to `F:\descargasf` as:

- `catlegal DDMM HHMMSS result.zip`
- `catlegal DDMM HHMMSS fail.zip`

Stage ZIPs remain separate and are referenced by hash. They are not nested in the coordinator ZIP.

## Boundaries

The panel collects and organizes evidence. It does not certify legal compliance,
IP ownership, open-source obligation resolution or production readiness.
