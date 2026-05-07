import { prisma } from "../prisma/client";

export type GetSaleDetailInput = { businessId: string; saleIdOrFolio: string };

function normalizeTicketNeedle(value: string) {
  return value.trim();
}

function ticketNeedleWhere(needle: string) {
  return [
    { id: needle },
    { folio: needle },
    { clientRequestId: needle },
  ];
}

function mapSaleDetail(sale: any) {
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

export async function getSaleDetail(input: GetSaleDetailInput) {
  const needle = normalizeTicketNeedle(input.saleIdOrFolio);
  if (!needle) return null;

  const or = ticketNeedleWhere(needle);

  const scopedSale = await prisma.sale.findFirst({
    where: { businessId: input.businessId, OR: or },
    include: { lines: true },
    orderBy: { createdAt: "desc" },
  });

  if (scopedSale) return mapSaleDetail(scopedSale);

  // PRISMA_TABLET_TICKET_DETAIL_NOT_FOUND_FIX_01:
  // Fallback local: algunos flujos visuales llegan con businessId omitido, cacheado o
  // diferente al usado al cerrar la venta. El ticket ya vive en la DB local, así que
  // intentamos recuperar por identificadores únicos visibles antes de mostrar 404.
  const localFallbackSale = await prisma.sale.findFirst({
    where: { OR: or },
    include: { lines: true },
    orderBy: { createdAt: "desc" },
  });

  if (!localFallbackSale) return null;
  return mapSaleDetail(localFallbackSale);
}
