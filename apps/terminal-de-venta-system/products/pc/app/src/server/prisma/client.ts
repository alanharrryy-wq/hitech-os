import { PrismaClient } from "@prisma/client";
import { existsSync, mkdirSync } from "node:fs";
import path from "node:path";

const globalForPrisma = globalThis as { prisma?: PrismaClient };

function toPrismaFileUrl(dbPath: string) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

function looksLikeTerminalRoot(candidate: string) {
  return (
    existsSync(path.join(candidate, "terminal_de_venta.cmd")) &&
    existsSync(path.join(candidate, "products", "pc", "app", "package.json"))
  );
}

function findTerminalRoot(start: string) {
  let current = path.resolve(start);
  for (;;) {
    if (looksLikeTerminalRoot(current)) return current;

    const nested = path.join(current, "apps", "terminal-de-venta-system");
    if (looksLikeTerminalRoot(nested)) return nested;

    const parent = path.dirname(current);
    if (parent === current) return null;
    current = parent;
  }
}

function canonicalDatabaseUrl() {
  if (process.env.DATABASE_URL) return process.env.DATABASE_URL;
  const terminalRoot = process.env.TV_SYSTEM_ROOT
    ? path.resolve(process.env.TV_SYSTEM_ROOT)
    : findTerminalRoot(process.cwd()) ?? path.resolve(process.cwd(), "..", "..", "..");
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
