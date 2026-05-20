import type { DeviceIdentity, PrismaRuntimeRole, PrismaVertical, RuntimeIssue } from "./runtime-context-types";
import { normalizeRole, normalizeVertical } from "./runtime-paths";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

export function normalizeDeviceIdentity(value: unknown): { identity: DeviceIdentity | null; issues: RuntimeIssue[] } {
  const issues: RuntimeIssue[] = [];
  if (!isRecord(value)) return { identity: null, issues: [{ code: "DEVICE_IDENTITY_INVALID", message: "Device identity must be an object." }] };

  const schemaVersion = asString(value.schemaVersion) ?? "1.0.0";
  const deviceId = asString(value.deviceId);
  const terminalId = asString(value.terminalId);
  const businessId = asString(value.businessId);
  const storeId = asString(value.storeId ?? value.branchId);
  const createdAt = asString(value.createdAt) ?? new Date(0).toISOString();
  const vertical = normalizeVertical(value.vertical) as PrismaVertical;
  const role = normalizeRole(value.role, "tablet") as PrismaRuntimeRole;

  if (!deviceId) issues.push({ code: "DEVICE_ID_MISSING", message: "Device identity is missing deviceId." });
  if (!terminalId) issues.push({ code: "TERMINAL_ID_MISSING", message: "Device identity is missing terminalId." });
  if (!businessId) issues.push({ code: "BUSINESS_ID_MISSING", message: "Device identity is missing businessId." });
  if (!storeId) issues.push({ code: "STORE_ID_MISSING", message: "Device identity is missing storeId." });

  if (issues.length > 0 || !deviceId || !terminalId || !businessId || !storeId) return { identity: null, issues };

  return {
    identity: {
      schemaVersion,
      deviceId,
      terminalId,
      businessId,
      storeId,
      vertical,
      role,
      createdAt,
      updatedAt: asString(value.updatedAt) ?? undefined
    },
    issues: []
  };
}
