import { prisma } from "../prisma/client";

export type ReturnableQuantityInput = { businessId: string; saleId: string };

export async function getReturnableLineQuantities(input: ReturnableQuantityInput) {
  const returns = await prisma.saleReturn.findMany({
    where: { businessId: input.businessId, saleId: input.saleId, status: { not: "CANCELLED" } },
    include: { lines: true },
  });
  const returnedByLine = new Map<string, number>();
  for (const ret of returns as any[]) {
    for (const line of ret.lines ?? []) {
      returnedByLine.set(line.saleLineId, (returnedByLine.get(line.saleLineId) ?? 0) + line.qty);
    }
  }
  return Object.fromEntries(returnedByLine.entries());
}
