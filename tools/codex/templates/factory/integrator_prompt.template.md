# Integrator Prompt

Run ID: {{run_id}}
Consume A/B/C/D bundles and output FINAL_REPORT.txt.

Required behavior:
- Prompt is delivered at run start; wait for worker completion before integration.
- Watch status and ledger while waiting:
  - `python -m tools.codex.factory watch --run-id {{run_id}}`
  - `python -m tools.codex.factory ledger --run-id {{run_id}} --raw-events --limit 200`
- Start integration/report generation automatically after workers finish.
- Do not invent features; merge/repair/validate/report only.
