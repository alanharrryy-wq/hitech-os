#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { reportPaths, terminalRoot, writeJson, writeText } from "../scripts/prisma-codex-utils.mjs";

const VALID_MODES = new Set(["dev", "customer", "test", "release"]);
const VALID_VERTICALS = new Set(["commerce", "industrial", "field", "control"]);
const VALID_ROLES = new Set(["tablet", "pc", "mobile", "control", "shared"]);

function argValue(args, name, fallback = null) {
  const index = args.indexOf(name);
  if (index >= 0 && args[index + 1]) return args[index + 1];
  const prefix = `${name}=`;
  const hit = args.find((item) => item.startsWith(prefix));
  return hit ? hit.slice(prefix.length) : fallback;
}

function hasFlag(args, name) {
  return args.includes(name);
}

function titleCase(value) {
  return value.slice(0, 1).toUpperCase() + value.slice(1).toLowerCase();
}

function defaultProgramDataRoot() {
  return process.env.ProgramData || "C:\\ProgramData";
}

function isPathInside(parent, child) {
  const relative = path.relative(path.resolve(parent), path.resolve(child));
  return Boolean(relative) && !relative.startsWith("..") && !path.isAbsolute(relative);
}

function nowIso() {
  return new Date().toISOString();
}

function buildPaths({ runtimeRoot, businessId }) {
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

function readJsonFile(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function resolvePackageFile(packageRoot, packageRelPath) {
  const resolved = path.resolve(packageRoot, String(packageRelPath || ""));
  if (!isPathInside(packageRoot, resolved) && path.resolve(packageRoot) !== resolved) {
    throw new Error(`Activation package file points outside package root: ${packageRelPath}`);
  }
  return resolved;
}

function loadActivationPackage(packageRoot, role) {
  const root = path.resolve(packageRoot);
  const manifestPath = path.join(root, "activation-package.json");
  if (!fs.existsSync(manifestPath)) throw new Error(`Activation package manifest missing: ${manifestPath}`);
  const manifest = readJsonFile(manifestPath);
  const roleSpec = manifest?.roles?.[role];
  if (!roleSpec) throw new Error(`Activation package does not include role ${role}: ${manifestPath}`);
  const licenseSource = resolvePackageFile(root, roleSpec.license);
  const receiptSource = resolvePackageFile(root, roleSpec.receipt);
  const identitySource = resolvePackageFile(root, roleSpec.deviceIdentity);
  const runtimeTemplate = resolvePackageFile(root, roleSpec.runtimeConfig);
  for (const file of [licenseSource, receiptSource, identitySource, runtimeTemplate]) {
    if (!fs.existsSync(file)) throw new Error(`Activation package file missing: ${file}`);
  }
  const identity = readJsonFile(identitySource);
  return {
    root,
    manifestPath,
    manifest,
    roleSpec,
    licenseSource,
    receiptSource,
    identitySource,
    runtimeTemplate,
    identity
  };
}

function parseArgs() {
  const args = process.argv.slice(2);
  const mode = argValue(args, "--runtime-mode", "customer");
  const vertical = argValue(args, "--vertical", "commerce");
  const role = argValue(args, "--role", "tablet");
  const activationPackageRoot = argValue(args, "--activation-package");
  const activationPackage = activationPackageRoot ? loadActivationPackage(activationPackageRoot, role) : null;
  const packageIdentity = activationPackage?.identity && typeof activationPackage.identity === "object" ? activationPackage.identity : {};
  const packageCustomer = activationPackage?.manifest?.customer && typeof activationPackage.manifest.customer === "object" ? activationPackage.manifest.customer : {};
  const businessId = argValue(args, "--business-id", packageIdentity.businessId || packageCustomer.businessId || "biz_78b3c840796a4a4dad");
  const storeId = argValue(args, "--store-id", packageIdentity.storeId || packageCustomer.storeId || "store_00728649f3804a9e82");
  const terminalId = argValue(args, "--terminal-id", packageIdentity.terminalId || (role === "tablet" ? "term_49103c7382d84663a3" : `${role}_prisma_original_customer_terminal_001`));
  const deviceId = argValue(args, "--device-id", packageIdentity.deviceId || `${role}_prisma_original_customer_001`);
  const packageType = argValue(args, "--package-type", packageCustomer.plan || (role === "pc" ? "PC_BACKOFFICE" : "TABLET_SOLO"));
  const clientId = argValue(args, "--client-id", packageCustomer.customerId || "cust_prisma_original_customer");
  const explicitRoot = argValue(args, "--runtime-root");
  const rootBase = explicitRoot || path.join(defaultProgramDataRoot(), "PRISMA", titleCase(vertical));
  const licenseSource = activationPackage?.licenseSource || argValue(args, "--license-file");
  const pcOrigin = argValue(args, "--pc-origin", packageType === "TABLET_PC_MANAGED" ? "http://127.0.0.1:3130" : null);
  const pcIngestPath = argValue(args, "--pc-ingest-path", "/api/backoffice/sync/ingest");
  const pcHealthPath = argValue(args, "--pc-health-path", "/api/health");
  const apply = hasFlag(args, "--apply");
  const dryRun = hasFlag(args, "--dry-run") || !apply;

  if (!VALID_MODES.has(mode)) throw new Error(`Invalid runtime mode: ${mode}`);
  if (!VALID_VERTICALS.has(vertical)) throw new Error(`Invalid vertical: ${vertical}`);
  if (!VALID_ROLES.has(role)) throw new Error(`Invalid role: ${role}`);

  return {
    mode,
    vertical,
    role,
    businessId,
    storeId,
    terminalId,
    deviceId,
    packageType,
    clientId,
    runtimeRoot: path.resolve(rootBase),
    licenseSource: licenseSource ? path.resolve(licenseSource) : null,
    activationPackage,
    pcOrigin,
    pcIngestPath,
    pcHealthPath,
    dryRun,
    apply
  };
}

function ensureDir(dir, dryRun, actions) {
  actions.push({ action: "ensure_dir", path: dir });
  if (!dryRun) fs.mkdirSync(dir, { recursive: true });
}

function writeJsonFile(filePath, payload, dryRun, actions) {
  actions.push({ action: "write_json", path: filePath });
  if (!dryRun) {
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
    fs.writeFileSync(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
  }
}

function copyLicense(source, target, dryRun, actions) {
  actions.push({ action: "copy_license", source, path: target });
  if (!dryRun) {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(source, target);
  }
}

function copyJsonArtifact(action, source, target, dryRun, actions) {
  actions.push({ action, source, path: target });
  if (!dryRun) {
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(source, target);
  }
}

function main() {
  const options = parseArgs();
  const actions = [];
  const paths = buildPaths(options);
  const issues = [];
  const activationReceiptTarget = options.activationPackage ? path.join(paths.configRoot, "activation-receipt.json") : null;

  if ((options.mode === "customer" || options.mode === "release") && isPathInside(terminalRoot, options.runtimeRoot)) {
    issues.push({ code: "RUNTIME_ROOT_POINTS_TO_REPO", message: "Customer/release runtime root must not point inside the repo.", path: options.runtimeRoot });
  }
  if (options.licenseSource && !fs.existsSync(options.licenseSource)) {
    issues.push({ code: "LICENSE_SOURCE_MISSING", message: "Provided license file does not exist.", path: options.licenseSource });
  }

  const runtimeConfig = {
    schemaVersion: "1.0.0",
    runtimeMode: options.mode,
    runtimeProfile: options.mode === "dev" ? "dev" : options.role === "pc" ? "pc_backoffice" : "standalone",
    vertical: options.vertical,
    role: options.role,
    runtimeRoot: paths.runtimeRoot,
    configRoot: paths.configRoot,
    clientId: options.clientId,
    businessId: options.businessId,
    storeId: options.storeId,
    terminalId: options.terminalId,
    deviceId: options.deviceId,
    packageType: options.packageType,
    paths,
    license: {
      file: paths.licenseFile,
      mode: "local_signed_with_optional_refresh"
    },
    activation: options.activationPackage ? {
      mode: options.activationPackage.manifest.mode,
      packageId: options.activationPackage.manifest.packageId,
      source: "licflow2_activation_package",
      manifestFile: options.activationPackage.manifestPath,
      receiptFile: activationReceiptTarget,
      hostedCloud: false
    } : undefined,
    sync: {
      enabled: options.packageType === "TABLET_PC_MANAGED",
      mode: options.packageType === "TABLET_PC_MANAGED" ? "local_network_optional" : "none",
      pcOrigin: options.packageType === "TABLET_PC_MANAGED" ? options.pcOrigin : undefined,
      ingestPath: options.packageType === "TABLET_PC_MANAGED" ? options.pcIngestPath : undefined,
      healthPath: options.packageType === "TABLET_PC_MANAGED" ? options.pcHealthPath : undefined,
      automaticDispatch: false,
      ackStrict: true,
      batchSize: 10,
      maxAttempts: 8
    },
    features: {},
    support: {
      diagnosticsEnabled: true,
      requiresConsent: true,
      activationMode: options.activationPackage?.manifest?.mode,
      activationPackageId: options.activationPackage?.manifest?.packageId,
      activationReceipt: activationReceiptTarget ?? undefined
    },
    updates: {
      channel: "stable",
      allowDuringOpenSale: false
    }
  };

  const identity = {
    schemaVersion: "1.0.0",
    deviceId: options.deviceId,
    terminalId: options.terminalId,
    businessId: options.businessId,
    storeId: options.storeId,
    vertical: options.vertical,
    role: options.role,
    createdAt: nowIso()
  };

  const dirs = [
    paths.configRoot,
    paths.tabletDataRoot,
    path.join(path.dirname(paths.tabletDataRoot), "Outbox"),
    path.join(path.dirname(paths.tabletDataRoot), "Diagnostics"),
    paths.pcDataRoot,
    paths.syncRoot,
    paths.supportRoot,
    path.join(paths.supportRoot, "Bundles"),
    paths.updatesRoot,
    paths.rollbackRoot,
    paths.logsRoot,
    paths.exportsRoot,
    paths.backupsRoot
  ];

  for (const dir of dirs) ensureDir(dir, options.dryRun, actions);
  writeJsonFile(path.join(paths.configRoot, "runtime.json"), runtimeConfig, options.dryRun, actions);
  if (options.activationPackage?.identitySource) {
    copyJsonArtifact("copy_device_identity", options.activationPackage.identitySource, paths.deviceIdentityFile, options.dryRun, actions);
  } else {
    writeJsonFile(paths.deviceIdentityFile, identity, options.dryRun, actions);
  }
  if (options.licenseSource) copyLicense(options.licenseSource, paths.licenseFile, options.dryRun, actions);
  if (options.activationPackage?.receiptSource && activationReceiptTarget) {
    copyJsonArtifact("copy_activation_receipt", options.activationPackage.receiptSource, activationReceiptTarget, options.dryRun, actions);
  }
  writeJsonFile(path.join(paths.configRoot, "provisioning-evidence.json"), {
    generatedAt: nowIso(),
    dryRun: options.dryRun,
    runtimeRoot: options.runtimeRoot,
    businessId: options.businessId,
    storeId: options.storeId,
    terminalId: options.terminalId,
    deviceId: options.deviceId,
    activationPackage: options.activationPackage ? {
      packageId: options.activationPackage.manifest.packageId,
      mode: options.activationPackage.manifest.mode,
      manifestPath: options.activationPackage.manifestPath,
      role: options.role
    } : null,
    actions
  }, options.dryRun, actions);

  const overall = issues.length ? "FAIL" : "PASS";
  const report = { generatedAt: nowIso(), overall, dryRun: options.dryRun, options, paths, issues, actions };
  const reportFiles = reportPaths("PRISMA_TABLET_PROVISIONING");
  writeJson(reportFiles.json, report);
  writeText(reportFiles.md, [
    "# PRISMA Tablet Provisioning",
    "",
    `Overall: ${overall}`,
    `Dry run: ${options.dryRun}`,
    `Runtime root: ${options.runtimeRoot}`,
    "",
    "## Issues",
    "",
    ...(issues.length ? issues.map((issue) => `- ${issue.code}: ${issue.message} ${issue.path ?? ""}`) : ["- None"]),
    "",
    "## Actions",
    "",
    ...actions.map((action) => `- ${action.action}: ${action.path}`)
  ].join("\n") + "\n");

  console.log(`${overall} provisioning report: ${reportFiles.md}`);
  if (issues.length) process.exit(1);
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
