import { prisma } from "../prisma/client";

export type GetSaleDetailInput = { businessId: string; saleIdOrFolio: string };

export async function getSaleDetail(input: GetSaleDetailInput) {
  const sale = await prisma.sale.findFirst({
    where: { businessId: input.businessId, OR: [{ id: input.saleIdOrFolio }, { folio: input.saleIdOrFolio }] },
    include: { lines: true },
  });
  if (!sale) return null;
  return {
    saleId: sale.id,
    folio: sale.folio,
    businessId: sale.businessId,
    terminalId: sale.terminalId,
    cashier: sale.cashier,
    status: sale.status,
    createdAt: sale.createdAt.toISOString(),
    completedAt: sale.completedAt?.toISOString() ?? null,
    subtotalCents: sale.subtotalCents,
    discountCents: sale.discountCents,
    totalCents: sale.totalCents,
    lines: sale.lines.map((line: any) => ({
      id: line.id,
      productId: line.productId,
      sku: line.sku,
      productName: line.productName,
      qty: line.qty,
      priceCents: line.priceCents,
      totalCents: line.totalCents,
    })),
  };
}
