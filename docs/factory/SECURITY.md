# Factory Security Guardrails

## Security Model

- Workers produce scoped bundles only.
- Z integrates/audits only; no product logic generation.
- Z write operations are restricted to `tools/codex/runs/<RUN_ID>/`.
- Feature flags remain OFF by default.

## Path Safety

- Absolute paths are rejected in FILES_CHANGED.
- Traversal (`..`) is rejected.
- UNC and drive-path tricks are rejected.
- `.git` and `.env` paths are protected by default.
- Symlink/junction escape checks are best-effort and block on detection.

## Concurrency Safety

- Per-run lock: `tools/codex/runs/<RUN_ID>/locks/run.lock`
- Per-worker lock: `tools/codex/runs/<RUN_ID>/locks/<WORKER>.lock`
- Concurrent run attempts with the same RUN_ID are BLOCKED.

## Ledger Integrity

- Ledger file is append-only JSONL:
  - `tools/codex/runs/factory_ledger.jsonl`
- Signature file:
  - `tools/codex/runs/factory_ledger.sha256`
- Corrupted lines fail parsing in strict mode and are treated as corruption.

## Attestation Integrity

- Run-level attestations:
  - `tools/codex/runs/<RUN_ID>/attestations/bundles.sha256`
  - `tools/codex/runs/<RUN_ID>/attestations/report.sha256`
  - `tools/codex/runs/<RUN_ID>/attestations/ledger.sha256`
- Entries are deterministically sorted by relative path.

## Secret and Scope Guarding

- Integrator scope checks include protected paths.
- Secret scanning is configurable and defaults enabled in runtime config.
- Executable artifact and shell execution remain disabled unless explicitly enabled.

## Operational Security Commands

```powershell
python -m tools.codex.factory doctor
python -m tools.codex.factory contracts-check
python -m tools.codex.factory ledger --raw-events --limit 100
python -m tools.codex.factory ledger-replay --run-id <RUN_ID>
```

## Incident Handling

1. Freeze run id and collect all run artifacts.
2. Verify ledger signature and attestations.
3. Replay ledger and identify first BLOCKED/FAIL event.
4. Fix root cause and rerun integration with same bundle inputs.
