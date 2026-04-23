export type StockSignalRow = {
  sku: string;
  onHand: number;
  hourlyVelocity: number;
  barcodeOk: boolean;
  isActive: boolean;
};

export function summarizeCoverage(row: StockSignalRow) {
  const hours = row.hourlyVelocity > 0 ? row.onHand / row.hourlyVelocity : 99;
  if (!row.isActive) return "inactivo";
  if (!row.barcodeOk) return "vigilar barcode";
  if (hours <= 1) return "quiebre inminente";
  if (hours <= 4) return "baja cobertura";
  return "estable";
}
