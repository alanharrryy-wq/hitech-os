import { existsSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import type { PrismaClient as PrismaClientType } from "../../../.generated/prisma-client";

const globalForPrisma = globalThis as { prisma?: PrismaClientType };

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
  const dbPath = path.join(terminalRoot, "products", "pc", "app", "data", "canonical.db");
  mkdirSync(path.dirname(dbPath), { recursive: true });
  const url = "file:../../../data/canonical.db";
  process.env.DATABASE_URL = url;
  return url;
}

const databaseUrl = canonicalDatabaseUrl();
const requireGeneratedPrisma = createRequire(import.meta.url);
const { PrismaClient } = requireGeneratedPrisma("../../../.generated/prisma-client") as typeof import("../../../.generated/prisma-client");

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    datasources: {
      db: {
        url: databaseUrl
      }
    }
  });

if (!globalForPrisma.prisma) {
  globalForPrisma.prisma = prisma;
}
