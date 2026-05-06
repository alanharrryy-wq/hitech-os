import type { CanonicalSale, CanonicalSaleLine, CanonicalSalesToday, MobileDataPlaneConfig } from "./types";
import { asArray, asRecord, pickArray, readCents, readDateIso, readNonNegativeInt, readString, unwrapOkData } from "./extractors";

function normalizeLine(raw: unknown, index: number): CanonicalSaleLine {
  const record = asRecord(raw);
  const qty = Math.max(1, readNonNegativeInt(record, ["qty", "quantity", "units"], 1));
  const unitPriceCents = readCents(record, ["unitPriceCents", "priceCents", "unitPrice", "price"], 0);
  const totalCents = readCents(record, ["totalCents", "lineTotalCents", "total"], unitPriceCents * qty);
  return {
    productId: readString(record, ["productId", "id"], `product_${index}`),
    sku: readString(record, ["sku", "barcode", "code"], `SKU-${index + 1}`),
    name: readString(record, ["name", "productName", "title"], "Producto sin nombre"),
    qty,
    unitPriceCents,
    totalCents,
    category: readString(record, ["category", "family", "department"], "General")
  };
}

function normalizeSale(raw: unknown, index: number, config: MobileDataPlaneConfig): CanonicalSale {
  const record = asRecord(raw);
  const rawLines = asArray(record.lines ?? record.items ?? record.saleLines);
  const lines = rawLines.map(normalizeLine);
  const subtotalFromLines = lines.reduce((sum, line) => sum + line.totalCents, 0);
  const totalCents = readCents(record, ["totalCents", "amountCents", "netTotalCents", "total"], subtotalFromLines);
  const subtotalCents = readCents(record, ["subtotalCents", "grossTotalCents", "subtotal"], subtotalFromLines || totalCents);
  const discountCents = readCents(record, ["discountCents", "discount"], Math.max(0, subtotalCents - totalCents));
  return {
    id: readString(record, ["id", "saleId", "ticketId"], `sale_${index}`),
    ticketNumber: readString(record, ["ticketNumber", "folio", "ticket"], `T-${String(index + 1).padStart(4, "0")}`),
    createdAt: readDateIso(record, ["createdAt", "openedAt", "startedAt"], new Date().toISOString()),
    completedAt: readDateIso(record, ["completedAt", "closedAt", "createdAt"], new Date().toISOString()),
    totalCents,
    subtotalCents,
    discountCents,
    paymentMethod: readString(record, ["paymentMethod", "payment", "method"], "mixto"),
    operatorId: readString(record, ["operatorId", "cashierId", "userId"], "operador"),
    terminalId: readString(record, ["terminalId"], config.terminalId),
    lines
  };
}

function buildHourlyBuckets(sales: CanonicalSale[]) {
  const buckets = new Map<string, { hour: string; amountCents: number; tickets: number }>();
  for (const sale of sales) {
    const hour = String(new Date(sale.completedAt).getHours()).padStart(2, "0") + ":00";
    const current = buckets.get(hour) ?? { hour, amountCents: 0, tickets: 0 };
    current.amountCents += sale.totalCents;
    current.tickets += 1;
    buckets.set(hour, current);
  }
  return Array.from(buckets.values()).sort((a, b) => a.hour.localeCompare(b.hour));
}

function topCategory(sales: CanonicalSale[]): string {
  const totals = new Map<string, number>();
  for (const sale of sales) {
    for (const line of sale.lines) totals.set(line.category, (totals.get(line.category) ?? 0) + line.totalCents);
  }
  return Array.from(totals.entries()).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "Sin categoría dominante";
}

export function normalizeSalesToday(payload: unknown, config: MobileDataPlaneConfig): CanonicalSalesToday {
  const data = unwrapOkData(payload);
  const record = asRecord(data);
  const salesArray = pickArray(data, ["sales", "tickets", "items", "rows", "transactions"]);
  const sales = salesArray.map((item, index) => normalizeSale(item, index, config));
  const totalSalesCents = readCents(record, ["totalSalesCents", "netSalesCents", "totalCents", "amountCents"], sales.reduce((sum, sale) => sum + sale.totalCents, 0));
  const tickets = readNonNegativeInt(record, ["tickets", "ticketCount", "transactions"], sales.length);
  const averageTicketCents = tickets > 0 ? Math.round(totalSalesCents / tickets) : 0;
  return { sales, totalSalesCents, tickets, averageTicketCents, hourlyBuckets: buildHourlyBuckets(sales), topCategory: topCategory(sales), sourceLabel: "Tablet POS" };
}

export function emptySalesToday(): CanonicalSalesToday {
  return { sales: [], totalSalesCents: 0, tickets: 0, averageTicketCents: 0, hourlyBuckets: [], topCategory: "Sin ventas todavía", sourceLabel: "sin datos" };
}
