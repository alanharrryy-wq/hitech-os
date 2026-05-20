import fs from "node:fs";
import path from "node:path";
import { normalizeDeviceIdentity } from "./device-identity";
import type {
  DeviceIdentity,
  PrismaRuntimeMode,
  PrismaRuntimeProfile,
  PrismaRuntimeRole,
  PrismaVertical,
  RuntimeContext,
  RuntimeContextConfig,
  RuntimeContextPaths,
  RuntimeContextResolverOptions,
  RuntimeIssue,
  RuntimeProvenance
} from "./runtime-context-types";
import {
  buildCustomerPaths,
  buildDevPaths,
  buildLegacyProgramDataPaths,
  defaultProgramDataRoot,
  findTerminalSystemRoot,
  normalizeRole,
  normalizeRuntimeMode,
  normalizeRuntimeProfile,
  normalizeVertical
} from "./runtime-paths";
import { validateRuntimeContext } from "./runtime-context-validator";

function readJsonIfExists(filePath: string): { value: RuntimeContextConfig | null; issue: RuntimeIssue | null } {
  if (!fs.existsSync(filePath)) return { value: null, issue: null };
  try {
    return { value: JSON.parse(fs.readFileSync(filePath, "utf8")) as RuntimeContextConfig, issue: null };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { value: null, issue: { code: "RUNTIME_CONFIG_INVALID_JSON", message, path: filePath } };
  }
}

function readIdentityIfExists(filePath: string): { value: DeviceIdentity | null; issues: RuntimeIssue[] } {
  if (!fs.existsSync(filePath)) return { value: null, issues: [] };
  try {
    const parsed = JSON.parse(fs.readFileSync(filePath, "utf8")) as unknown;
    const normalized = normalizeDeviceIdentity(parsed);
    return { value: normalized.identity, issues: normalized.issues.map((issue) => ({ ...issue, path: filePath })) };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { value: null, issues: [{ code: "DEVICE_IDENTITY_INVALID_JSON", message, path: filePath }] };
  }
}

function provenance(source: RuntimeProvenance["source"], pathValue: string | null, detail: string): RuntimeProvenance {
  return { source, path: pathValue, detail };
}

function pickString(...values: unknown[]): string | null {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return null;
}

function withOverrides(base: RuntimeContextPaths, overrides?: Partial<RuntimeContextPaths>): RuntimeContextPaths {
  return {
    runtimeRoot: path.resolve(overrides?.runtimeRoot ?? base.runtimeRoot),
    configRoot: path.resolve(overrides?.configRoot ?? base.configRoot),
    businessRoot: path.resolve(overrides?.businessRoot ?? base.businessRoot),
    tabletDataRoot: path.resolve(overrides?.tabletDataRoot ?? base.tabletDataRoot),
    pcDataRoot: path.resolve(overrides?.pcDataRoot ?? base.pcDataRoot),
    syncRoot: path.resolve(overrides?.syncRoot ?? base.syncRoot),
    supportRoot: path.resolve(overrides?.supportRoot ?? base.supportRoot),
    updatesRoot: path.resolve(overrides?.updatesRoot ?? base.updatesRoot),
    rollbackRoot: path.resolve(overrides?.rollbackRoot ?? base.rollbackRoot),
    logsRoot: path.resolve(overrides?.logsRoot ?? base.logsRoot),
    exportsRoot: path.resolve(overrides?.exportsRoot ?? base.exportsRoot),
    backupsRoot: path.resolve(overrides?.backupsRoot ?? base.backupsRoot),
    licenseFile: path.resolve(overrides?.licenseFile ?? base.licenseFile),
    deviceIdentityFile: path.resolve(overrides?.deviceIdentityFile ?? base.deviceIdentityFile)
  };
}

function resolveConfigPath(options: RuntimeContextResolverOptions, vertical: PrismaVertical, programDataRoot: string): { path: string | null; source: RuntimeProvenance["source"]; warnings: RuntimeIssue[] } {
  const warnings: RuntimeIssue[] = [];
  const explicit = pickString(options.explicitRuntimeConfigPath, process.env.PRISMA_RUNTIME_CONFIG);
  if (explicit) return { path: path.resolve(explicit), source: options.explicitRuntimeConfigPath ? "explicit" : "env", warnings };

  const canonical = path.join(programDataRoot, "PRISMA", vertical === "commerce" ? "Commerce" : vertical[0].toUpperCase() + vertical.slice(1), "Config", "runtime.json");
  if (fs.existsSync(canonical)) return { path: canonical, source: "programdata", warnings };

  const legacy = path.join(programDataRoot, "PRISMA", "config", "runtime.json");
  if (fs.existsSync(legacy)) {
    warnings.push({ code: "LEGACY_RUNTIME_CONFIG_PATH", message: "Using legacy ProgramData runtime config path; migrate to vertical Config layout.", path: legacy });
    return { path: legacy, source: "legacy_programdata", warnings };
  }

  return { path: null, source: "default", warnings };
}

export function resolveRuntimeContext(options: RuntimeContextResolverOptions = {}): RuntimeContext {
  const systemRoot = findTerminalSystemRoot(options.systemRoot || process.env.TV_SYSTEM_ROOT || process.cwd());
  const programDataRoot = path.resolve(options.programDataRoot || process.env.PRISMA_PROGRAMDATA_ROOT || defaultProgramDataRoot());
  const initialVertical = normalizeVertical(options.vertical || process.env.PRISMA_VERTICAL || "commerce");
  const configPathResolution = resolveConfigPath(options, initialVertical, programDataRoot);
  const configRead = configPathResolution.path ? readJsonIfExists(configPathResolution.path) : { value: null, issue: null };
  const config = configRead.value;
  const warnings: RuntimeIssue[] = [...configPathResolution.warnings];
  const blockingIssues: RuntimeIssue[] = [];
  if (configRead.issue) blockingIssues.push(configRead.issue);

  const vertical = normalizeVertical(options.vertical || process.env.PRISMA_VERTICAL || config?.vertical || initialVertical);
  const profile = (options.runtimeProfile || config?.runtimeProfile || normalizeRuntimeProfile(options.runtimeMode || process.env.PRISMA_RUNTIME_MODE || config?.runtimeMode)) as PrismaRuntimeProfile;
  const runtimeMode = normalizeRuntimeMode(options.runtimeMode || process.env.PRISMA_RUNTIME_MODE || config?.runtimeMode, profile) as PrismaRuntimeMode;
  const role = normalizeRole(options.role || process.env.PRISMA_RUNTIME_ROLE || config?.role, "shared") as PrismaRuntimeRole;

  const identityFileOverride = pickString(options.deviceIdentityFile, process.env.PRISMA_DEVICE_IDENTITY_FILE, config?.paths?.deviceIdentityFile);
  const licenseFileOverride = pickString(options.licenseFile, process.env.PRISMA_LICENSE_PATH, process.env.PRISMA_LICENSE_FILE, config?.license?.file, config?.paths?.licenseFile);

  const seedBusinessId = pickString(config?.businessId, config?.clientId, "unassigned-business");
  const customerPaths = buildCustomerPaths({ programDataRoot, vertical, businessId: seedBusinessId });
  const legacyPaths = buildLegacyProgramDataPaths(programDataRoot, seedBusinessId);
  const devPaths = buildDevPaths(systemRoot, seedBusinessId ?? "dev-prisma-store");
  const basePaths = runtimeMode === "dev" || runtimeMode === "test" ? devPaths : configPathResolution.source === "legacy_programdata" ? legacyPaths : customerPaths;
  const paths = withOverrides(basePaths, {
    ...config?.paths,
    runtimeRoot: config?.runtimeRoot ?? config?.paths?.runtimeRoot ?? basePaths.runtimeRoot,
    configRoot: config?.configRoot ?? config?.paths?.configRoot ?? basePaths.configRoot,
    licenseFile: licenseFileOverride ?? (runtimeMode === "dev" ? devPaths.licenseFile : config?.paths?.licenseFile ?? basePaths.licenseFile),
    deviceIdentityFile: identityFileOverride ?? config?.paths?.deviceIdentityFile ?? basePaths.deviceIdentityFile
  });

  const identityRead = readIdentityIfExists(paths.deviceIdentityFile);
  warnings.push(...identityRead.issues);
  const identity = identityRead.value;

  const businessId = pickString(identity?.businessId, config?.businessId);
  const storeId = pickString(identity?.storeId, config?.storeId, config?.branchId);
  const terminalId = pickString(identity?.terminalId, config?.terminalId);
  const deviceId = pickString(identity?.deviceId, config?.deviceId, process.env.PRISMA_LICENSE_DEVICE_ID);
  const clientId = pickString(config?.clientId);

  const effectivePaths = withOverrides(paths, {
    businessRoot: paths.businessRoot.includes("unassigned-business") && businessId ? paths.businessRoot.replace("unassigned-business", businessId) : paths.businessRoot,
    tabletDataRoot: paths.tabletDataRoot.includes("unassigned-business") && businessId ? paths.tabletDataRoot.replace("unassigned-business", businessId) : paths.tabletDataRoot,
    pcDataRoot: paths.pcDataRoot.includes("unassigned-business") && businessId ? paths.pcDataRoot.replace("unassigned-business", businessId) : paths.pcDataRoot,
    syncRoot: paths.syncRoot.includes("unassigned-business") && businessId ? paths.syncRoot.replace("unassigned-business", businessId) : paths.syncRoot,
    supportRoot: paths.supportRoot.includes("unassigned-business") && businessId ? paths.supportRoot.replace("unassigned-business", businessId) : paths.supportRoot,
    logsRoot: paths.logsRoot.includes("unassigned-business") && businessId ? paths.logsRoot.replace("unassigned-business", businessId) : paths.logsRoot,
    exportsRoot: paths.exportsRoot.includes("unassigned-business") && businessId ? paths.exportsRoot.replace("unassigned-business", businessId) : paths.exportsRoot,
    backupsRoot: paths.backupsRoot.includes("unassigned-business") && businessId ? paths.backupsRoot.replace("unassigned-business", businessId) : paths.backupsRoot
  });

  const context: RuntimeContext = {
    schemaVersion: config?.schemaVersion ?? "1.0.0",
    runtimeMode,
    runtimeProfile: profile,
    vertical,
    role,
    runtimeRoot: effectivePaths.runtimeRoot,
    configRoot: effectivePaths.configRoot,
    licenseFile: effectivePaths.licenseFile,
    deviceIdentityFile: effectivePaths.deviceIdentityFile,
    businessId,
    storeId,
    terminalId,
    deviceId,
    clientId,
    packageType: config?.packageType ?? null,
    paths: effectivePaths,
    deviceIdentity: identity,
    config,
    configPath: configPathResolution.path,
    provenance: {
      runtimeConfig: provenance(configPathResolution.source, configPathResolution.path, configPathResolution.path ? "runtime.json resolved by precedence" : "no runtime.json found"),
      runtimeRoot: provenance(config ? "runtime_config" : runtimeMode === "dev" ? "dev_fallback" : "programdata", effectivePaths.runtimeRoot, "runtime root"),
      configRoot: provenance(config ? "runtime_config" : runtimeMode === "dev" ? "dev_fallback" : "programdata", effectivePaths.configRoot, "config root"),
      licenseFile: provenance(licenseFileOverride ? "explicit" : runtimeMode === "dev" ? "dev_fallback" : configPathResolution.source === "legacy_programdata" ? "legacy_programdata" : "programdata", effectivePaths.licenseFile, "license file"),
      deviceIdentityFile: provenance(identityFileOverride ? "explicit" : runtimeMode === "dev" ? "dev_fallback" : configPathResolution.source === "legacy_programdata" ? "legacy_programdata" : "programdata", effectivePaths.deviceIdentityFile, "device identity file"),
      deviceIdentity: provenance(identity ? "device_identity" : "default", identity ? effectivePaths.deviceIdentityFile : null, identity ? "stable device identity loaded" : "device identity missing")
    },
    warnings,
    blockingIssues
  };

  context.blockingIssues.push(...validateRuntimeContext(context, { systemRoot }));
  return context;
}
