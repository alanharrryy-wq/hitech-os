import { existsSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import type { PrismaClient as PrismaClientType } from "../../../.generated/prisma-client";

const globalForPrisma = globalThis as { prisma?: PrismaClientType; prismaDatabaseUrl?: string };

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

function toPrismaFileUrl(dbPath: string) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

function resolvePcAppRoot() {
  const terminalRoot = process.env.TV_SYSTEM_ROOT
    ? path.resolve(process.env.TV_SYSTEM_ROOT)
    : findTerminalRoot(process.cwd()) ?? path.resolve(process.cwd(), "..", "..", "..");
  return path.join(terminalRoot, "products", "pc", "app");
}

function normalizeCanonicalDatabaseUrl(databaseUrl: string) {
  if (!databaseUrl.startsWith("file:")) return databaseUrl;

  const filePath = databaseUrl.slice("file:".length);
  if (!filePath.startsWith(".") && path.isAbsolute(filePath)) {
    mkdirSync(path.dirname(filePath), { recursive: true });
    return toPrismaFileUrl(filePath);
  }

  const absolutePath = path.resolve(resolvePcAppRoot(), "prisma", filePath);
  mkdirSync(path.dirname(absolutePath), { recursive: true });
  return toPrismaFileUrl(absolutePath);
}

function canonicalDatabaseUrl() {
  if (process.env.DATABASE_URL) return normalizeCanonicalDatabaseUrl(process.env.DATABASE_URL);
  const dbPath = path.join(resolvePcAppRoot(), "data", "canonical.db");
  mkdirSync(path.dirname(dbPath), { recursive: true });
  const url = toPrismaFileUrl(dbPath);
  process.env.DATABASE_URL = url;
  return url;
}

const databaseUrl = canonicalDatabaseUrl();
const requireGeneratedPrisma = createRequire(import.meta.url);
const { PrismaClient } = requireGeneratedPrisma("../../../.generated/prisma-client") as typeof import("../../../.generated/prisma-client");
const existingPrisma = globalForPrisma.prisma && globalForPrisma.prismaDatabaseUrl === databaseUrl
  ? globalForPrisma.prisma
  : undefined;

export const prisma =
  existingPrisma ??
  new PrismaClient({
    datasources: {
      db: {
        url: databaseUrl
      }
    }
  });

if (!existingPrisma) {
  globalForPrisma.prisma = prisma;
  globalForPrisma.prismaDatabaseUrl = databaseUrl;
}
