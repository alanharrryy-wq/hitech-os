# Mobile Snapshot Quality

Status: active

Mobile supervises. It must consume snapshot/read models and must not become the transactional source of truth.

Quality checks:

- meta.generatedAt exists.
- source/runtimeMode are explicit.
- freshness/source status exists.
- action inbox shape is present or reported missing.
- health radar dimensions are present or reported missing.
- alerts/data quality are present or reported missing.
- no direct DB access is needed.

Verification:

```powershell
pnpm -C products/mobile/app verify:mobile-snapshot-quality
```

The verifier can inspect source contracts by default, a JSON fixture with --fixture, or a local URL with --url.
