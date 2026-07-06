# Surface To Data Matrix

| surface | route | component | loader | db | tables | status | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tablet POS | /pos,/api/pos/sales/complete,/api/pos/products/search,/api/pos/inventory/low-stock | PosScreen/Tablet POS loaders | getTabletRuntimeSnapshot,getTodaySalesSummary,searchProducts,getLowStockProducts | products/tablet/app/data/tablet-pos.db | Product,StockSnapshot,CashSession,Sale,SaleLine,SalePaymentTender,OutboxEvent | PASS | verify:data-surface:tablet |
| PC/Admin | /sales-control,/api/backoffice/sales-control | sales-control page and branch view | getPcSalesControl | products/pc/app/data/canonical.db | Sale,SaleLine,SalePaymentTender,Store,Terminal,Product | PASS | verify:data-surface:pc |
| Mobile | /api/mobile/snapshot | PrismaMobileDashboard | loadMobileDataPlaneState,readLocalDbSnapshot | products/tablet/app/data/tablet-pos.db | Sale,Product,StockSnapshot | PASS | verify:data-surface:mobile |
| Chart Lab | Chart Lab runtime readers | PrismaChartLabShell | chart-runtime-data,lifecycle_api counters | products/chart-lab/app/data/chart-runtime-governance.db | runtime_chart_payloads,runtime_metadata,runtime_sources | PASS | verify:data-surface:chart |
| Data Lifecycle | prisma-control-center lifecycle API | lifecycle_console.js | lifecycle_api.py | Data Lifecycle configured DB set | lifecycle_pins plus chart/runtime counters | PASS | verify:data-surface:lifecycle |
