import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";

export type PricingPolicySnapshot = {
  businessId: string | null;
  productCount: number;
  lastProductPriceUpdate: Date | null;
  priceLists: Array<{
    id: string;
    name: string;
    currency: string;
    isDefault: boolean;
    isActive: boolean;
    startsAt: Date;
    endsAt: Date | null;
    itemCount: number;
  }>;
  taxRates: Array<{
    id: string;
    name: string;
    rateBps: number;
    isDefault: boolean;
    isActive: boolean;
    updatedAt: Date;
  }>;
};

export async function getPricingPolicySnapshot(): Promise<PricingPolicySnapshot> {
  const businessId = await resolvePcBusinessScope();

  const [productCount, latestProduct, priceLists, taxRates] = await Promise.all([
    prisma.product.count({ where: { businessId } }),
    prisma.product.findFirst({
      where: { businessId },
      select: { updatedAt: true },
      orderBy: { updatedAt: "desc" }
    }),
    prisma.priceList.findMany({
      where: { businessId },
      select: {
        id: true,
        name: true,
        currency: true,
        isDefault: true,
        isActive: true,
        startsAt: true,
        endsAt: true,
        _count: { select: { items: true } }
      },
      orderBy: [{ isDefault: "desc" }, { name: "asc" }]
    }),
    prisma.taxRate.findMany({
      where: { businessId },
      select: {
        id: true,
        name: true,
        rateBps: true,
        isDefault: true,
        isActive: true,
        updatedAt: true
      },
      orderBy: [{ isDefault: "desc" }, { name: "asc" }]
    })
  ]);

  return {
    businessId,
    productCount,
    lastProductPriceUpdate: latestProduct?.updatedAt ?? null,
    priceLists: priceLists.map((list) => ({
      id: list.id,
      name: list.name,
      currency: list.currency,
      isDefault: list.isDefault,
      isActive: list.isActive,
      startsAt: list.startsAt,
      endsAt: list.endsAt,
      itemCount: list._count.items
    })),
    taxRates
  };
}
