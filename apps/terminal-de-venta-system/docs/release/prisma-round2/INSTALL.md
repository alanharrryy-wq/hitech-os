# Install

Product root:

`F:\repos\hitech-os\apps\terminal-de-venta-system`

Package manager:

`pnpm`

Recommended active-workspace install command:

```powershell
pnpm install --frozen-lockfile
```

Round 2.1 workspace decision:

`products/web/app` is preserved in place but kept outside `pnpm-workspace.yaml` until its `latest` dependency ranges are replaced with exact approved versions and a lockfile importer is intentionally generated.

Focused install for the Round 2 core apps:

```powershell
pnpm install --filter @hitech/tablet --filter @hitech/pc --filter @hitech/mobile --frozen-lockfile
```

Release policy:

- Do not use `--no-frozen-lockfile` for release validation.
- Do not promote `products/web/app` into the workspace until its versions and lockfile are deterministic.
- Do not delete or move `products/web/app`; it is an off-release lane, not trash.
