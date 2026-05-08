<!-- agent-workbench-rescue-managed -->
# Evidence Policy

## Rules

- Evidence belongs under `docs/dev/agent-workbench/agents/<agent>/evidence/`.
- Evidence should not be overwritten.
- Prefer timestamped filenames for new evidence.
- Reports must list evidence reviewed.
- User-delivered PDFs are considered delivered evidence but must be converted to Markdown before review.
- Do not commit bulky PDFs unless explicitly approved.

## CAPATCH Evidence

CAPATCH may appear only as historical evidence, legacy context, or risk reference. It must not be recommended for merge, relaunch, or dependency use.
