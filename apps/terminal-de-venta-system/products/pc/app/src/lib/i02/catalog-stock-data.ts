export const catalogCategorySummary = [
  { categoria: "Bebidas", skus: 1000, activos: 1000, precioPromedio: 52.5, costoPromedio: 33.08 },
  { categoria: "Lácteos", skus: 1000, activos: 1000, precioPromedio: 52.5, costoPromedio: 33.08 },
  { categoria: "Limpieza", skus: 1000, activos: 1000, precioPromedio: 52.5, costoPromedio: 33.08 },
  { categoria: "Farmacia", skus: 1000, activos: 1000, precioPromedio: 52.5, costoPromedio: 33.08 },
  { categoria: "Snacks", skus: 1000, activos: 1000, precioPromedio: 52.5, costoPromedio: 33.08 }
] as const;

export const criticalStockRows = [
  { sku: "SKU-00000", producto: "Bebidas producto 0", ubicacion: "A-01", disponible: 0, diasCobertura: 0.0, estado: "critico" },
  { sku: "SKU-00000", producto: "Bebidas producto 0", ubicacion: "A-02", disponible: 0, diasCobertura: 0.0, estado: "critico" },
  { sku: "SKU-00000", producto: "Bebidas producto 0", ubicacion: "A-03", disponible: 0, diasCobertura: 0.0, estado: "critico" },
  { sku: "SKU-00000", producto: "Bebidas producto 0", ubicacion: "A-04", disponible: 0, diasCobertura: 0.0, estado: "critico" },
  { sku: "SKU-00005", producto: "Bebidas producto 5", ubicacion: "A-01", disponible: 1, diasCobertura: 1.4, estado: "riesgo" },
  { sku: "SKU-00011", producto: "Snacks producto 11", ubicacion: "A-02", disponible: 1, diasCobertura: 1.1, estado: "riesgo" },
  { sku: "SKU-00017", producto: "Lácteos producto 17", ubicacion: "A-03", disponible: 0, diasCobertura: 0.4, estado: "critico" },
  { sku: "SKU-00023", producto: "Farmacia producto 23", ubicacion: "A-04", disponible: 1, diasCobertura: 1.7, estado: "riesgo" }
] as const;

export const barcodeHealthRows = [
  { categoria: "Bebidas", productos: 1000, barcodes: 1250, promedio: 1.25, activos: 1000 },
  { categoria: "Snacks", productos: 1000, barcodes: 1250, promedio: 1.25, activos: 1000 },
  { categoria: "Lácteos", productos: 1000, barcodes: 1250, promedio: 1.25, activos: 1000 },
  { categoria: "Farmacia", productos: 1000, barcodes: 1250, promedio: 1.25, activos: 1000 },
  { categoria: "Limpieza", productos: 1000, barcodes: 1250, promedio: 1.25, activos: 1000 }
] as const;
