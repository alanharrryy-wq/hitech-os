# PC StockFicha visual pilot from Tablet Licenses

- Task: `PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1`
- Factory Ledger classification before application: `BUILD`
- Exact gate: `APPLY`
- Success classification: `DONE`
- Target: `/stock` → `StockFicha` → `PC-STOCK-FICHA-PANEL-01`
- Source visual authority: Tablet `/settings/license`, semantic translation only.
- Product files: `apps/terminal-de-venta-system/products/pc/app/components/inventory/inventory-workspace.tsx`, `apps/terminal-de-venta-system/products/pc/app/components/inventory/pc-inventory-master-detail.module.css`
- Tablet, Cobrar, RIFAT protected files, DB, Prisma, APIs and handlers: unchanged.
- Recipe: `REC.panel.operational.cloudglass`
- Binding: `BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1`
- Adapter: `ADP.PC.DENSE.CLOUDGLASS.V1`
- Neutral layer: `LYR.SURFACE.OPERATIONAL.DETAIL`
- Rollback: exact backup plus Git revert of the single PR.
- Anti-rework: do not rebuild this pilot after merge; advance by governed route expansion only.
