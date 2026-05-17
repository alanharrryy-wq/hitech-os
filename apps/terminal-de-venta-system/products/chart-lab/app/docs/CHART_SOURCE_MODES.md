# Chart Source Modes

Status: active

Chart Lab must not imply live data unless a real adapter proves it.

Allowed sourceMode values:

- mock: deterministic design data, never operational proof.
- fixture: static validation data, not live.
- recorded-real: captured from a real source with timestamp and provenance.
- live-real: current source through an approved adapter/server/API, with freshness and confidence.

Every chart entry must declare sourceMode, sourceLabel, confidence, freshnessStatus, generatedAt and source. live-real requires adapterPath and must not point at shared mocks.

Verification:

```powershell
pnpm -C products/chart-lab/app verify:chart-source-modes
```
