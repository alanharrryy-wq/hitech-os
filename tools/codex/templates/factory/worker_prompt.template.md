# Worker Prompt

Run ID: {{run_id}}
Worker: {{worker_id}}
Scope lock: see SCOPE_LOCK.json

Required behavior:
- Start with clean-session protocol; ignore stale prior thread context if present.
- Complete assigned scope and then auto-closeout artifacts:
  - STATUS.json
  - SUMMARY.md
  - FILES_CHANGED.json
  - DIFF.patch
  - SUGGESTIONS.md
  - SCOPE_LOCK.json
  - HANDOFF_NOTE.json
  - LOGS/INDEX.json
  - CODEX_OUTPUT.txt
- If a required folder/path is missing, auto-repair it and continue.
- Write DONE marker when complete:
  - tools/codex/runs/{{run_id}}/{{worker_id}}/DONE.marker
