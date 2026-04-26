import { PrismaClient } from "@prisma/client";
import { mkdirSync } from "node:fs";
import path from "node:path";

const globalForPrisma = globalThis as { prisma?: PrismaClient };

function toPrismaFileUrl(dbPath: string) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

function canonicalDatabaseUrl() {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;
  const terminalRoot = path.resolve(process.cwd(), "..", "..", "..");
  const repoRoot = path.resolve(terminalRoot, "..", "..");
  const dbPath = path.join(repoRoot, "tools", "_local", "data", "terminal-de-venta-system", "canonical.db");
  mkdirSync(path.dirname(dbPath), { recursive: true });
  return toPrismaFileUrl(dbPath);
}

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    datasources: {
      db: {
        url: canonicalDatabaseUrl()
      }
    }
  });

if (!globalForPrisma.prisma) {
  globalForPrisma.prisma = prisma;
}
