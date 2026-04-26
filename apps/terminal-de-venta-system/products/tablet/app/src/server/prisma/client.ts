import { PrismaClient } from "@prisma/client";
import { mkdirSync } from "node:fs";
import path from "node:path";

declare global {
  var __tabletPrisma__: PrismaClient | undefined;
}

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
  globalThis.__tabletPrisma__ ??
  new PrismaClient({
    datasources: {
      db: {
        url: canonicalDatabaseUrl()
      }
    }
  });
if (process.env.NODE_ENV !== "production") globalThis.__tabletPrisma__ = prisma;
