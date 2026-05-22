import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import type { PrismaRuntimeMode, PrismaRuntimeProfile, PrismaRuntimeRole, PrismaVertical, RuntimeContextPaths } from "./runtime-context-types";

const PROFILE_TO_MODE: Record<PrismaRuntimeProfile, PrismaRuntimeMode> = {
  dev: "dev",
  standalone: "customer",
  pro: "customer",
  pc_backoffice: "customer",
  managed: "customer",
  degraded_managed: "customer"
};

const VERTICAL_SEGMENT: Record<PrismaVertical, string> = {
  commerce: "Commerce",
  industrial: "Industrial",
  field: "Field",
  control: "Control"
};

export function findTerminalSystemRoot(start = process.cwd()): string {
  let current = path.resolve(start);
  for (let i = 0; i < 14; i += 1) {
    if (fs.existsSync(path.join(current, "products")) && fs.existsSync(path.join(current, "shared"))) return current;
    if (fs.existsSync(path.join(current, "terminal_de_venta.cmd"))) return current;
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  return path.resolve(start);
}

export function defaultProgramDataRoot(): string {
  if (os.platform() === "win32") return process.env.ProgramData || "C:\\ProgramData";
  return "/var/lib";
}

export function normalizeVertical(value: unknown): PrismaVertical {
  const normalized = typeof value === "string" ? value.toLowerCase() : "";
  if (normalized === "industrial" || normalized === "field" || normalized === "control") return normalized;
  return "commerce";
}

export function verticalSegment(vertical: PrismaVertical): string {
  return VERTICAL_SEGMENT[vertical];
}

export function normalizeRole(value: unknown, fallback: PrismaRuntimeRole = "shared"): PrismaRuntimeRole {
  const normalized = typeof value === "string" ? value.toLowerCase() : "";
  if (normalized === "tablet" || normalized === "pc" || normalized === "mobile" || normalized === "control" || normalized === "shared") return normalized;
  return fallback;
}

export function normalizeRuntimeProfile(value: unknown): PrismaRuntimeProfile {
  const normalized = typeof value === "string" ? value.toLowerCase() : "";
  if (normalized === "standalone" || normalized === "pro" || normalized === "pc_backoffice" || normalized === "managed" || normalized === "degraded_managed") return normalized;
  return "dev";
}

export function normalizeRuntimeMode(value: unknown, profile?: PrismaRuntimeProfile): PrismaRuntimeMode {
  const normalized = typeof value === "string" ? value.toLowerCase() : "";
  if (normalized === "customer" || normalized === "test" || normalized === "release" || normalized === "dev") return normalized;
  if (normalized === "standalone" || normalized === "pro" || normalized === "pc_backoffice" || normalized === "managed" || normalized === "degraded_managed") return PROFILE_TO_MODE[normalized];
  return profile ? PROFILE_TO_MODE[profile] : "dev";
}

export function isAbsolutePath(value: string): boolean {
  return path.isAbsolute(value);
}

export function isPathInside(parent: string, child: string): boolean {
  const relative = path.relative(path.resolve(parent), path.resolve(child));
  return Boolean(relative) && !relative.startsWith("..") && !path.isAbsolute(relative);
}

export function buildCustomerPaths(options: {
  programDataRoot?: string | null;
  vertical?: PrismaVertical;
  businessId?: string | null;
}): RuntimeContextPaths {
  const vertical = options.vertical ?? "commerce";
  const businessId = options.businessId || "unassigned-business";
  const runtimeRoot = path.join(options.programDataRoot || defaultProgramDataRoot(), "PRISMA", verticalSegment(vertical));
  const configRoot = path.join(runtimeRoot, "Config");
  const businessRoot = path.join(runtimeRoot, "Businesses", businessId);
  return {
    runtimeRoot,
    configRoot,
    businessRoot,
    tabletDataRoot: path.join(businessRoot, "Tablet", "Data"),
    pcDataRoot: path.join(businessRoot, "PC", "Data"),
    syncRoot: path.join(businessRoot, "Sync"),
    supportRoot: path.join(businessRoot, "Support"),
    updatesRoot: path.join(runtimeRoot, "Updates"),
    rollbackRoot: path.join(runtimeRoot, "Rollback"),
    logsRoot: path.join(businessRoot, "Logs"),
    exportsRoot: path.join(businessRoot, "Exports"),
    backupsRoot: path.join(businessRoot, "Backups"),
    licenseFile: path.join(configRoot, "license.json"),
    deviceIdentityFile: path.join(configRoot, "device-identity.json")
  };
}

export function buildLegacyProgramDataPaths(programDataRoot?: string | null, businessId?: string | null): RuntimeContextPaths {
  const root = path.join(programDataRoot || defaultProgramDataRoot(), "PRISMA");
  const configRoot = path.join(root, "config");
  const businessRoot = path.join(root, "businesses", businessId || "unassigned-business");
  return {
    runtimeRoot: root,
    configRoot,
    businessRoot,
    tabletDataRoot: path.join(businessRoot, "tablet", "data"),
    pcDataRoot: path.join(businessRoot, "pc", "data"),
    syncRoot: path.join(businessRoot, "sync"),
    supportRoot: path.join(businessRoot, "support"),
    updatesRoot: path.join(root, "updates"),
    rollbackRoot: path.join(root, "rollback"),
    logsRoot: path.join(businessRoot, "logs"),
    exportsRoot: path.join(businessRoot, "exports"),
    backupsRoot: path.join(businessRoot, "backups"),
    licenseFile: path.join(configRoot, "license.json"),
    deviceIdentityFile: path.join(configRoot, "device-identity.json")
  };
}

export function buildDevPaths(systemRoot = findTerminalSystemRoot(), businessId = "dev-prisma-store"): RuntimeContextPaths {
  const runtimeRoot = path.join(systemRoot, "local-runtime");
  const configRoot = path.join(runtimeRoot, "config");
  const businessRoot = path.join(runtimeRoot, "businesses", businessId);
  return {
    runtimeRoot,
    configRoot,
    businessRoot,
    tabletDataRoot: path.join(businessRoot, "tablet", "data"),
    pcDataRoot: path.join(businessRoot, "pc", "data"),
    syncRoot: path.join(businessRoot, "sync"),
    supportRoot: path.join(businessRoot, "support"),
    updatesRoot: path.join(runtimeRoot, "updates"),
    rollbackRoot: path.join(runtimeRoot, "rollback"),
    logsRoot: path.join(businessRoot, "logs"),
    exportsRoot: path.join(businessRoot, "exports"),
    backupsRoot: path.join(businessRoot, "backups"),
    licenseFile: path.join(runtimeRoot, "license", "license.signed.dev.json"),
    deviceIdentityFile: path.join(configRoot, "device-identity.dev.json")
  };
}
