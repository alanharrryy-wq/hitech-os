# REMOTE_CACHE_SETUP

Turbo remote cache integration is available but **OFF by default** for this repository.
Enable it explicitly in your CI pipeline when constitution/governance allows activation.

## Required Secret Names

- `TURBO_TOKEN`
- `TURBO_TEAM`
- Optional: `TURBO_API`

Only secret names are documented here. Never commit secret values.

## GitHub Actions Example (Optional)

```yaml
name: ci
on: [push, pull_request]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: pnpm install --frozen-lockfile
      - name: Optional Turbo remote cache env
        run: echo "Remote cache vars ready"
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ secrets.TURBO_TEAM }}
          TURBO_API: ${{ secrets.TURBO_API }}
      - run: python tools/hos/turbo/turbo_wrap.py --ci --profile stable -- run build
```

## Generic CI Example (Optional)

1. Provide secret env names `TURBO_TOKEN` and `TURBO_TEAM`.
2. Optionally provide `TURBO_API` for custom endpoint.
3. Run:

```powershell
python tools/hos/turbo/remote_cache_check.py --require
python tools/hos/turbo/turbo_wrap.py --ci --profile stable -- run build
```

## Local Usage (No hard-fail)

```powershell
python tools/hos/turbo/remote_cache_check.py
python tools/hos/turbo/turbo_wrap.py --profile balanced -- run lint
```

Local mode continues without remote cache variables and only emits warnings.
