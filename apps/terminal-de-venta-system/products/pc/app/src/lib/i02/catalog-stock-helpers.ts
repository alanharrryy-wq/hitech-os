import { barcodeHealthRows, catalogCategorySummary, criticalStockRows } from "./catalog-stock-data";

export function getCatalogStockSnapshot() {
  const categorias = catalogCategorySummary.length;
  const skusActivos = catalogCategorySummary.reduce((acc, row) => acc + row.activos, 0);
  const filasCriticas = criticalStockRows.filter((row) => row.estado === "critico").length;
  const promedioBarcodes = Number((barcodeHealthRows.reduce((acc, row) => acc + row.promedio, 0) / barcodeHealthRows.length).toFixed(2));

  return {
    categorias,
    skusActivos,
    filasCriticas,
    promedioBarcodes
  };
}
