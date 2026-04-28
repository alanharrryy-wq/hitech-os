import { PrismaClient } from "@prisma/client";
import { mkdirSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

declare global {
  var __tabletPrisma__: PrismaClient | undefined;
}

function toPrismaFileUrl(dbPath: string) {
  return `file:${dbPath.replace(/\\/g, "/")}`;
}

function resolveTabletAppRoot() {
  if (process.env.TABLET_APP_ROOT) return path.resolve(process.env.TABLET_APP_ROOT);

  const moduleDir = path.dirname(fileURLToPath(import.meta.url));
  return path.resolve(moduleDir, "..", "..", "..");
}

function localTabletDatabasePath() {
  if (process.env.TABLET_DATABASE_PATH) return path.resolve(process.env.TABLET_DATABASE_PATH);
  return path.join(resolveTabletAppRoot(), "data", "tablet-pos.db");
}

function tabletDatabaseUrl() {
  if (process.env.TABLET_DATABASE_URL) return process.env.TABLET_DATABASE_URL;

  if (process.env.TABLET_DATABASE_PATH) {
    const dbPath = localTabletDatabasePath();
    mkdirSync(path.dirname(dbPath), { recursive: true });
    return toPrismaFileUrl(dbPath);
  }

  if (process.env.TABLET_RUNTIME_MODE === "managed" && process.env.DATABASE_URL) {
    return process.env.DATABASE_URL;
  }

  const dbPath = localTabletDatabasePath();
  mkdirSync(path.dirname(dbPath), { recursive: true });
  return toPrismaFileUrl(dbPath);
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
