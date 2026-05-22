import path from "node:path";
import type { RuntimeContext, RuntimeIssue } from "./runtime-context-types";
import { isAbsolutePath, isPathInside } from "./runtime-paths";

const REQUIRED_CUSTOMER_FIELDS: Array<keyof Pick<RuntimeContext, "businessId" | "storeId" | "deviceId" | "terminalId">> = [
  "businessId",
  "storeId",
  "deviceId",
  "terminalId"
];

const REQUIRED_CUSTOMER_CODES: Record<(typeof REQUIRED_CUSTOMER_FIELDS)[number], string> = {
  businessId: "BUSINESS_ID_MISSING",
  storeId: "STORE_ID_MISSING",
  deviceId: "DEVICE_ID_MISSING",
  terminalId: "TERMINAL_ID_MISSING"
};

const PATH_KEYS: Array<keyof RuntimeContext["paths"]> = [
  "runtimeRoot",
  "configRoot",
  "businessRoot",
  "tabletDataRoot",
  "pcDataRoot",
  "syncRoot",
  "supportRoot",
  "updatesRoot",
  "rollbackRoot",
  "logsRoot",
  "exportsRoot",
  "backupsRoot",
  "licenseFile",
  "deviceIdentityFile"
];

export function validateRuntimeContext(context: RuntimeContext, options: { systemRoot: string }): RuntimeIssue[] {
  const issues: RuntimeIssue[] = [];
  const isCustomerLike = context.runtimeMode === "customer" || context.runtimeMode === "release";

  for (const key of PATH_KEYS) {
    const value = context.paths[key];
    if (!isAbsolutePath(value)) {
      issues.push({ code: "RELATIVE_PATH_NOT_ALLOWED", message: `${key} must be absolute in runtime context.`, path: value });
    }
  }

  if (isCustomerLike) {
    for (const key of REQUIRED_CUSTOMER_FIELDS) {
      if (!context[key]) {
        issues.push({ code: REQUIRED_CUSTOMER_CODES[key], message: `${String(key)} is required in customer/release runtime mode.` });
      }
    }

    for (const key of PATH_KEYS) {
      const value = context.paths[key];
      if (isPathInside(options.systemRoot, value) || path.resolve(value) === path.resolve(options.systemRoot)) {
        issues.push({ code: "RUNTIME_PATH_POINTS_TO_REPO", message: `${key} points inside the development repo in customer/release mode.`, path: value });
      }
    }

    if (context.provenance.licenseFile?.source === "dev_fallback") {
      issues.push({ code: "CUSTOMER_USES_DEV_LICENSE_FALLBACK", message: "Customer/release mode must not use repo dev license fallback.", path: context.licenseFile });
    }

    if (!context.deviceIdentity) {
      issues.push({ code: "DEVICE_IDENTITY_MISSING", message: "Customer/release mode requires stable local device identity.", path: context.deviceIdentityFile });
    }
  }

  return issues;
}
