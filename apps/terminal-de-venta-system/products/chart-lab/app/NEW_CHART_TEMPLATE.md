# NEW_CHART_TEMPLATE.md

Use this when adding a new PRISMA Chart Lab visual.

The PRISMA Chart Lab runs locally at `http://localhost:3000`.

Future charts must be addable by creating:

1. one chart component,
2. one mock-data provider,
3. one registry entry,
4. optionally one visual recipe/theme file.

Adding a new chart must not require editing:

- the lab shell;
- navigation layout;
- product PC, Tablet, Mobile, Web, or Control apps;
- Cloudflare/deployment scripts.

## Exact steps

1. Pick a stable chart id.

Example:

```text
web.margin-risk-horizon
```

2. Create the component.

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\components\MarginRiskHorizon.tsx
```

3. Create the mock provider.

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\mocks\web.margin-risk-horizon.mock.ts
```

4. Add one registry entry.

```text
F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\src\prisma-charts\chart-lab-registry.tsx
```

5. Optional: add a visual recipe or token adjustment.

Use this only when the chart family needs a reusable visual standard. Keep one-off styling inside the component until the pattern proves reusable.

6. Validate.

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:typecheck
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:build
```

## Scaffold helper

Dry run:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app" scaffold:chart -- --id=web.example-chart --title="Example Chart" --surface=web
```

Write files:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app" scaffold:chart -- --id=web.example-chart --title="Example Chart" --surface=web --write
```

The scaffold helper creates component and mock files, then prints a registry stub. It does not edit the registry automatically, so the final registry change remains intentional.

## Existing proof

The registry includes `Example Future Chart` (`example.future-chart`) as a placeholder showing the extension pattern without changing the shell.
