import { PrismaClient } from "@prisma/client";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

declare global {
  var __tabletPrisma__: PrismaClient | undefined;
}

export function toPrismaFileUrl(dbPath: string) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

export function resolveTabletAppRoot() {
  if (process.env.TABLET_APP_ROOT) return path.resolve(process.env.TABLET_APP_ROOT);

  const moduleDir = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(moduleDir, "..", "..", "..");
}

export function localTabletDatabasePath() {
  if (process.env.TABLET_DATABASE_PATH) return path.resolve(process.env.TABLET_DATABASE_PATH);
  return path.join(resolveTabletAppRoot(), "data", "tablet-pos.db");
}

function normalizeTabletDatabaseUrl(databaseUrl: string) {
  if (!databaseUrl.startsWith("file:")) return databaseUrl;

  const filePath = databaseUrl.slice("file:".length);
  if (!filePath.startsWith(".") && path.isAbsolute(filePath)) {
    mkdirSync(path.dirname(filePath), { recursive: true });
    return toPrismaFileUrl(filePath);
  }

  const absolutePath = path.resolve(resolveTabletAppRoot(), filePath);
  mkdirSync(path.dirname(absolutePath), { recursive: true });
  return toPrismaFileUrl(absolutePath);
}

export function tabletDatabaseUrl() {
  if (process.env.TABLET_DATABASE_URL) return normalizeTabletDatabaseUrl(process.env.TABLET_DATABASE_URL);

  if (process.env.TABLET_DATABASE_PATH) {
    const dbPath = localTabletDatabasePath();
    mkdirSync(path.dirname(dbPath), { recursive: true });
    return toPrismaFileUrl(dbPath);
  }

  const dbPath = localTabletDatabasePath();
  mkdirSync(path.dirname(dbPath), { recursive: true });
  return toPrismaFileUrl(dbPath);
}

export function getTabletDatabaseInfo() {
  const dbPath = localTabletDatabasePath();
  return {
    appRoot: resolveTabletAppRoot(),
    databasePath: dbPath,
    databaseUrl: TABLET_DATABASE_URL,
    source: process.env.TABLET_DATABASE_URL ? "TABLET_DATABASE_URL" : process.env.TABLET_DATABASE_PATH ? "TABLET_DATABASE_PATH" : "tablet-local-default"
  };
}

export const TABLET_DATABASE_URL = tabletDatabaseUrl();

export const prisma =
  globalThis.__tabletPrisma__ ??
  new PrismaClient({
    datasources: {
      db: {
        url: TABLET_DATABASE_URL
      }
    }
  });

if (process.env.NODE_ENV !== "production") globalThis.__tabletPrisma__ = prisma;
