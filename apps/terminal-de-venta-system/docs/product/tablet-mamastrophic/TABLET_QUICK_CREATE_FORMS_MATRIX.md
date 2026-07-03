# TABLET QUICK CREATE FORMS MATRIX

| Flow | Owner | Implementation |
| --- | --- | --- |
| Nuevo producto | Catalog | `beginNewProduct()` resets the catalog drawer and focuses the product name field. Save still uses `/api/pos/products/create`. |
| Nueva venta | POS | Tile routes to `/pos` or the operational gate action. No sale API was changed. |
| Nueva devolucion | Returns | Tile routes to the contextual returns ticket list. Return creation remains in the existing ticket flow. |
| Abrir turno | Shift | Tile anchors to the existing open-turn form. API remains `/api/pos/shift/open`. |
| Cerrar turno | Shift | Tile anchors to the existing close-turn form. API remains `/api/pos/shift/close`. |
| Enviar pendientes | Sync | Tile invokes existing `dispatchNow(false)`. |
| Reintentar pendientes | Sync | Tile invokes existing `retryFailed()`. |
| Exportar respaldo | Offline/Export settings | Tiles open existing backup/export surfaces and endpoints. |
| Importar licencia | License | Deferred; Tablet client remains read-only. |
| Ajustar stock | Stock | Deferred; no confirmed local owner/API selected in this pass. |
| Nueva categoria | Catalog | Deferred; no confirmed local category API selected in this pass. |
