import { PrismaClient } from "@prisma/client";

declare global {
  var __tabletPrisma__: PrismaClient | undefined;
}

export const prisma = globalThis.__tabletPrisma__ ?? new PrismaClient();
if (process.env.NODE_ENV !== "production") globalThis.__tabletPrisma__ = prisma;
