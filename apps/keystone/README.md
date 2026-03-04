# Keystone App

## Scene Studio (dev-only)

Launch the Keystone dev server with Scene Studio enabled:

```powershell
pnpm run keystone:scene:studio
```

Open:

- `http://127.0.0.1:3100/dev/scene-studio?debug=1`

## Visual Proof Commands

Smoke (fast subset):

```powershell
pnpm run keystone:scene:visual:smoke
```

Full scene suite:

```powershell
pnpm run keystone:scene:visual
```

Intentional baseline update:

```powershell
pnpm run keystone:scene:visual:update
```

Regenerate report index:

```powershell
pnpm run keystone:scene:report
```

Proof gate for improvement claim:

```powershell
pnpm run keystone:scene:proof:gate -- --claim-id=<RUN_ID>
```
