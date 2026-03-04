# Capability Contract (Pitch Engine)

## Capability

- Name: `director`
- Modes: `off | lite | full | debug`

The capability system resolves requested and applied modes with auditable provenance.

## Priority Resolution

Resolution order is strict:

1. `env`
2. `query`
3. `localStorage`
4. `defaults`

Expected director keys:

- env: `PITCH_CAP_DIRECTOR`
- query: `capDirector`
- localStorage: `pitch.capability.director`

## Requested vs Applied

Resolver output includes:

- `requested`
- `applied`
- `reasons[]`
- `auditTrail[]`

`auditTrail` contains one event per source with selection flag.

## Production Hard Gate

When `NODE_ENV=production`:

- `applied` is forced to `off`
- reason `production-hard-gate` is added

This is enforced regardless of requested source.

## Degrade Integration

Capability output is consumed by sequence degrade logic:

- `requested=full|debug` can degrade to `applied=lite` under `perf=low`.
- reduced-motion can also force `full|debug` to `lite`.

Reason codes remain explicit for auditing.

## Determinism

Given equal `env/query/localStorage/defaults/nodeEnv`, resolver output must be bit-for-bit stable:

- same selected source
- same requested/applied modes
- same reason ordering
- same audit trail ordering
