export function listDashboardKpiSources() {
  return [
    { key: "sales", owner: "sales", freshness: "turno actual" },
    { key: "returns", owner: "returns", freshness: "turno actual" },
    { key: "sync", owner: "sync", freshness: "ultima cola visible" },
    { key: "stock", owner: "stock", freshness: "senal operativa" }
  ];
}
