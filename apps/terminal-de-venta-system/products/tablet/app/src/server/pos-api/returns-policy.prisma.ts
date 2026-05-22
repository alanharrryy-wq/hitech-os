import { prisma } from "../prisma/client";

export type ReturnableQuantityInput = { businessId: string; saleId: string };

export async function getReturnableLineQuantities(input: ReturnableQuantityInput) {
  const returnedLines = await prisma.saleReturnLine.findMany({
    where: {
      businessId: input.businessId,
      saleId: input.saleId,
      saleReturn: { status: { not: "CANCELLED" } },
    },
    select: { saleLineId: true, qty: true },
  });

  const returnedByLine = new Map<string, number>();
  for (const line of returnedLines) {
    if (!line.saleLineId) continue;
    returnedByLine.set(line.saleLineId, (returnedByLine.get(line.saleLineId) ?? 0) + line.qty);
  }

  return Object.fromEntries(returnedByLine.entries());
}
