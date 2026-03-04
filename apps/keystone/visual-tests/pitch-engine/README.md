# Pitch Engine Visual Smoke

Deterministic minimal smoke harness for Keystone pitch-engine validation.

## Run

```bash
node apps/keystone/visual-tests/pitch-engine/playwright_smoke.mjs --start-server
```

## Behavior

- Starts `@hitech/keystone` dev server when `--start-server` is passed.
- Attempts Playwright Chromium checks if `playwright` is available.
- Falls back to deterministic fetch-based checks when Playwright is unavailable.
- Verifies:
  - `/pitch?debug=1` renders expected pitch/debug surface.
  - `/dev/scene-studio?debug=1` is either available (Timeline) or gated (404).
  - `/dev/pitch-engine?debug=1` is either available (controls) or gated (404).
  - `/api/runs` responds with a contract-shaped payload.

No retries are used to hide flakes.
