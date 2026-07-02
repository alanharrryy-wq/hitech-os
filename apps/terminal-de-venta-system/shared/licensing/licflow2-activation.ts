import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { PRISMA_ORIGINAL_CUSTOMER } from "../customer/prisma-original-customer";
import {
  ADLANT4_ISSUER_LABEL,
  buildAdlant4RuntimeFilePayload,
  buildPrismaOriginalCustomerLicenseDocument,
  bootstrapPrismaOriginalCustomerLicense,
  resolveAdlant4IssuerPaths,
  signLicenseDocument,
  type Adlant4RuntimeRole
} from "./adlant4-local-issuer";
import { verifySignedLicenseEnvelope } from "./license-signature";
import type { LicenseActivationMetadata, LicenseActivationMode, LicenseDocument } from "./license-types";
import type { SignedLicenseEnvelope } from "./signed-license-types";

export const LICFLOW2_PACKAGE_SCHEMA_VERSION = "1.0.0";
export const LICFLOW2_ACTIVATION_MODES: readonly LicenseActivationMode[] = ["OFFLINE_PACKAGE", "ONLINE_ACTIVATION", "HYBRID"] as const;
export const LICFLOW2_SERVICE_CONTRACT_ENDPOINT = "POST /licenses/activate";

export type Licflow2ActivationRoleFiles = {
  runtimeConfig: string;
  deviceIdentity: string;
  license: string;
  receipt: string;
  installTargets: {
    runtimeConfig: string;
    deviceIdentity: string;
    license: string;
    receipt: string;
  };
};

export type Licflow2ActivationReceipt = {
  receiptId: string;
  timestamp: string;
  action: "licflow2.activation";
  source: "licflow2-local-adlant4";
  mode: LicenseActivationMode;
  customerId: string;
  businessId: string;
  storeId: string;
  licenseId: string;
  plan: "TABLET_PC_MANAGED";
  keyId: string;
  alg: "Ed25519";
  licenseHash: string;
  packageId: string;
  result: "activated";
  hostedCloud: false;
  serviceContract: {
    endpoint: string;
    implementation: "local_loopback_or_operator_service";
    hostedCloud: false;
  };
  privateKeyIncluded: false;
  dbFilesIncluded: false;
  devices: LicenseDocument["authorizedDevices"];
};

export type Licflow2ActivationPackageManifest = {
  schemaVersion: string;
  packageId: string;
  mode: LicenseActivationMode;
  createdAt: string;
  customer: {
    displayName: string;
    customerId: string;
    tenantId: string;
    businessId: string;
    storeId: string;
    licenseId: string;
    plan: "TABLET_PC_MANAGED";
  };
  license: {
    file: string;
    sha256: string;
    keyId: string;
    alg: "Ed25519";
  };
  receipt: {
    file: string;
    receiptId: string;
  };
  roles: Record<Adlant4RuntimeRole, Licflow2ActivationRoleFiles>;
  onlineActivationContract: {
    endpoint: string;
    hostedCloud: false;
    note: string;
  };
  security: {
    privateKeyIncluded: false;
    dbFilesIncluded: false;
    envFilesIncluded: false;
    secretsIncluded: false;
  };
  rollback: {
    removeInstalledFiles: string[];
    keepPrivateKey: true;
  };
};

export type Licflow2ActivationPackageResult = {
  ok: true;
  mode: LicenseActivationMode;
  packageId: string;
  packageRoot: string;
  manifestPath: string;
  signedLicensePath: string;
  receiptPath: string;
  licenseHash: string;
  envelope: SignedLicenseEnvelope;
  manifest: Licflow2ActivationPackageManifest;
  receipt: Licflow2ActivationReceipt;
};

export type Licflow2OnlineActivationRequest = {
  requestId: string;
  requestedAt: string;
  customerId: string;
  businessId: string;
  storeId: string;
  deviceId: string;
  role: Adlant4RuntimeRole;
  plan: "TABLET_PC_MANAGED";
};

export type Licflow2OnlineActivationEvidence = {
  ok: true;
  mode: "ONLINE_ACTIVATION";
  request: Licflow2OnlineActivationRequest;
  response: {
    ok: true;
    endpoint: string;
    hostedCloud: false;
    packageId: string;
    receiptId: string;
    licenseHash: string;
    signedLicensePath: string;
  };
  packageResult: Licflow2ActivationPackageResult;
};

export type Licflow2HybridActivationEvidence = {
  ok: true;
  mode: "HYBRID";
  packageResult: Licflow2ActivationPackageResult;
  refreshFallback: {
    attemptedAt: string;
    onlineEndpoint: string;
    simulatedResult: "REMOTE_UNAVAILABLE";
    localLicenseStillValid: true;
    operationalDecision: "allow_with_warning";
    supportAction: "keep local signed license, retry online refresh, export receipt evidence";
  };
};

function nowStamp(now: Date): string {
  return now.toISOString().replace(/[:.]/g, "-");
}

function modeSlug(mode: LicenseActivationMode): string {
  return mode.toLowerCase().replace(/_/g, "-");
}

function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function writeText(file: string, value: string): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, value, "utf8");
}

function sha256File(file: string): string {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function asPackagePath(value: string): string {
  return value.replace(/\\/g, "/");
}

function defaultOutputRoot(): string {
  return path.resolve(process.env.PRISMA_LICFLOW2_ROOT || "F:/PRISMA_CTX/LICENSING/licflow2/prisma-original-customer");
}

function ensureOutsideRepo(target: string): void {
  const repoRoot = path.resolve(process.env.TV_SYSTEM_ROOT || process.cwd());
  const resolved = path.resolve(target);
  const relative = path.relative(repoRoot, resolved);
  if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) {
    throw new Error(`LICFLOW2 output must stay outside the repo: ${resolved}`);
  }
}

function roleDeviceId(role: Adlant4RuntimeRole): string {
  if (role === "pc") return PRISMA_ORIGINAL_CUSTOMER.pcDeviceId;
  if (role === "mobile") return PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId;
  return PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId;
}

function activationChannel(mode: LicenseActivationMode): LicenseActivationMetadata["channel"] {
  if (mode === "OFFLINE_PACKAGE") return "local_package";
  if (mode === "ONLINE_ACTIVATION") return "local_loopback_contract";
  return "hybrid_package_with_refresh";
}

export function buildLicflow2ActivationMetadata(mode: LicenseActivationMode, receiptId: string, activatedAt: string): LicenseActivationMetadata {
  return {
    schemaVersion: LICFLOW2_PACKAGE_SCHEMA_VERSION,
    mode,
    status: "activated",
    channel: activationChannel(mode),
    receiptId,
    activatedAt,
    issuedBy: ADLANT4_ISSUER_LABEL,
    hostedCloud: false,
    supportCode: `LICFLOW2-${mode}`
  };
}

export function buildLicflow2LicenseDocument(mode: LicenseActivationMode, now = new Date(), receiptId?: string): LicenseDocument {
  const base = buildPrismaOriginalCustomerLicenseDocument(now);
  const activationReceiptId = receiptId ?? `licflow2_${modeSlug(mode)}_${nowStamp(now)}`;
  return {
    ...base,
    issuedAt: now.toISOString(),
    lastRefreshAt: mode === "OFFLINE_PACKAGE" ? base.lastRefreshAt : now.toISOString(),
    activation: buildLicflow2ActivationMetadata(mode, activationReceiptId, now.toISOString()),
    notes: [
      ...(base.notes ?? []),
      `LICFLOW2 activation mode ${mode}.`,
      "Hosted cloud activation is not claimed by this local contract."
    ]
  };
}

export function createLicflow2ActivationPackage(options: {
  mode: LicenseActivationMode;
  outputRoot?: string;
  now?: Date;
  packageId?: string;
}): Licflow2ActivationPackageResult {
  if (!LICFLOW2_ACTIVATION_MODES.includes(options.mode)) {
    throw new Error(`Unsupported LICFLOW2 activation mode: ${options.mode}`);
  }

  const now = options.now ?? new Date();
  const outputRoot = path.resolve(options.outputRoot ?? defaultOutputRoot());
  ensureOutsideRepo(outputRoot);
  fs.mkdirSync(outputRoot, { recursive: true });

  const packageId = options.packageId ?? `licflow2_${modeSlug(options.mode)}_${nowStamp(now)}`;
  const packageRoot = path.join(outputRoot, packageId);
  const signedLicensePath = path.join(packageRoot, "license.signed.json");
  const receiptPath = path.join(packageRoot, "activation-receipt.json");
  const manifestPath = path.join(packageRoot, "activation-package.json");
  const receiptId = `${packageId}_receipt`;

  const issuerPaths = resolveAdlant4IssuerPaths();
  bootstrapPrismaOriginalCustomerLicense();
  const privateKeyPem = fs.readFileSync(issuerPaths.privateKeyPath, "utf8");
  const document = buildLicflow2LicenseDocument(options.mode, now, receiptId);
  const envelope = signLicenseDocument(document, privateKeyPem);
  const verification = verifySignedLicenseEnvelope(envelope);
  if (!verification.ok) {
    throw new Error(`LICFLOW2_SIGNED_LICENSE_INVALID: ${verification.issues.join("; ")}`);
  }

  writeJson(signedLicensePath, envelope);
  const licenseHash = sha256File(signedLicensePath);

  const receipt: Licflow2ActivationReceipt = {
    receiptId,
    timestamp: now.toISOString(),
    action: "licflow2.activation",
    source: "licflow2-local-adlant4",
    mode: options.mode,
    customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
    licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId,
    plan: "TABLET_PC_MANAGED",
    keyId: envelope.keyId,
    alg: "Ed25519",
    licenseHash,
    packageId,
    result: "activated",
    hostedCloud: false,
    serviceContract: {
      endpoint: LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
      implementation: "local_loopback_or_operator_service",
      hostedCloud: false
    },
    privateKeyIncluded: false,
    dbFilesIncluded: false,
    devices: document.authorizedDevices
  };
  writeJson(receiptPath, receipt);

  const roles = {} as Record<Adlant4RuntimeRole, Licflow2ActivationRoleFiles>;
  for (const role of ["pc", "tablet", "mobile"] as Adlant4RuntimeRole[]) {
    const roleRoot = path.join(packageRoot, "roles", role);
    const runtimeRel = asPackagePath(path.join("roles", role, "runtime.json"));
    const identityRel = asPackagePath(path.join("roles", role, "device-identity.json"));
    const runtimePayload = buildAdlant4RuntimeFilePayload(role, {
      licensePath: "Config/license.json",
      deviceIdentityPath: "Config/device-identity.json",
      receiptPath: "Config/activation-receipt.json",
      issuedAt: now.toISOString(),
      activation: document.activation ?? null,
      support: {
        activationMode: options.mode,
        activationPackageId: packageId,
        activationPackageManifest: "activation-package.json",
        onlineActivationEndpoint: LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
        hostedCloud: false
      }
    });
    writeJson(path.join(roleRoot, "runtime.json"), runtimePayload.runtimeConfig);
    writeJson(path.join(roleRoot, "device-identity.json"), runtimePayload.identity);
    roles[role] = {
      runtimeConfig: runtimeRel,
      deviceIdentity: identityRel,
      license: "license.signed.json",
      receipt: "activation-receipt.json",
      installTargets: {
        runtimeConfig: "Config/runtime.json",
        deviceIdentity: "Config/device-identity.json",
        license: "Config/license.json",
        receipt: "Config/activation-receipt.json"
      }
    };
  }

  const manifest: Licflow2ActivationPackageManifest = {
    schemaVersion: LICFLOW2_PACKAGE_SCHEMA_VERSION,
    packageId,
    mode: options.mode,
    createdAt: now.toISOString(),
    customer: {
      displayName: PRISMA_ORIGINAL_CUSTOMER.displayName,
      customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
      tenantId: PRISMA_ORIGINAL_CUSTOMER.tenantId,
      businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
      storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
      licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId,
      plan: "TABLET_PC_MANAGED"
    },
    license: {
      file: "license.signed.json",
      sha256: licenseHash,
      keyId: envelope.keyId,
      alg: "Ed25519"
    },
    receipt: {
      file: "activation-receipt.json",
      receiptId
    },
    roles,
    onlineActivationContract: {
      endpoint: LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
      hostedCloud: false,
      note: "This is the PRISMA local service contract for online activation. It does not claim hosted cloud infrastructure."
    },
    security: {
      privateKeyIncluded: false,
      dbFilesIncluded: false,
      envFilesIncluded: false,
      secretsIncluded: false
    },
    rollback: {
      removeInstalledFiles: ["Config/runtime.json", "Config/device-identity.json", "Config/license.json", "Config/activation-receipt.json"],
      keepPrivateKey: true
    }
  };
  writeJson(manifestPath, manifest);
  writeText(path.join(packageRoot, "README.md"), [
    "# LICFLOW2 Activation Package",
    "",
    `Mode: ${options.mode}`,
    `Package: ${packageId}`,
    "",
    "Contains only signed license, role runtime templates, device identities, manifest, and receipt.",
    "Does not contain private keys, databases, .env files, or hosted-cloud credentials.",
    ""
  ].join("\n"));

  return {
    ok: true,
    mode: options.mode,
    packageId,
    packageRoot,
    manifestPath,
    signedLicensePath,
    receiptPath,
    licenseHash,
    envelope,
    manifest,
    receipt
  };
}

export function createLicflow2OnlineActivationEvidence(options: {
  outputRoot?: string;
  now?: Date;
  role?: Adlant4RuntimeRole;
} = {}): Licflow2OnlineActivationEvidence {
  const now = options.now ?? new Date();
  const role = options.role ?? "tablet";
  const packageResult = createLicflow2ActivationPackage({ mode: "ONLINE_ACTIVATION", outputRoot: options.outputRoot, now });
  const request: Licflow2OnlineActivationRequest = {
    requestId: `${packageResult.packageId}_request`,
    requestedAt: now.toISOString(),
    customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
    deviceId: roleDeviceId(role),
    role,
    plan: "TABLET_PC_MANAGED"
  };
  const evidence: Licflow2OnlineActivationEvidence = {
    ok: true,
    mode: "ONLINE_ACTIVATION",
    request,
    response: {
      ok: true,
      endpoint: LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
      hostedCloud: false,
      packageId: packageResult.packageId,
      receiptId: packageResult.receipt.receiptId,
      licenseHash: packageResult.licenseHash,
      signedLicensePath: packageResult.signedLicensePath
    },
    packageResult
  };
  writeJson(path.join(packageResult.packageRoot, "online-activation-request.json"), request);
  writeJson(path.join(packageResult.packageRoot, "online-activation-response.json"), evidence.response);
  return evidence;
}

export function createLicflow2HybridActivationEvidence(options: {
  outputRoot?: string;
  now?: Date;
} = {}): Licflow2HybridActivationEvidence {
  const now = options.now ?? new Date();
  const packageResult = createLicflow2ActivationPackage({ mode: "HYBRID", outputRoot: options.outputRoot, now });
  const refreshFallback: Licflow2HybridActivationEvidence["refreshFallback"] = {
    attemptedAt: now.toISOString(),
    onlineEndpoint: LICFLOW2_SERVICE_CONTRACT_ENDPOINT,
    simulatedResult: "REMOTE_UNAVAILABLE",
    localLicenseStillValid: true,
    operationalDecision: "allow_with_warning",
    supportAction: "keep local signed license, retry online refresh, export receipt evidence"
  };
  const evidence: Licflow2HybridActivationEvidence = {
    ok: true,
    mode: "HYBRID",
    packageResult,
    refreshFallback
  };
  writeJson(path.join(packageResult.packageRoot, "hybrid-refresh-fallback.json"), refreshFallback);
  return evidence;
}
