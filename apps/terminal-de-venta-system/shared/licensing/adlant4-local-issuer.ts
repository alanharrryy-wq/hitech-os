import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { PRISMA_ORIGINAL_CUSTOMER } from "../customer/prisma-original-customer";
import { canonicalJsonBuffer } from "./canonical-json";
import { verifySignedLicenseEnvelope } from "./license-signature";
import type { AuthorizedLicenseDevice, LicenseDocument } from "./license-types";
import type { LicensePublicKey } from "./license-public-keys";
import type { SignedLicenseEnvelope } from "./signed-license-types";

export const ADLANT4_LOCAL_KEY_ID = "adlant4_local_2026_0630";
export const ADLANT4_ISSUER_LABEL = "ADLANT4 local Ed25519 issuer";

export type Adlant4RuntimeRole = "pc" | "tablet" | "mobile";

export type Adlant4IssuerPaths = {
  issuerRoot: string;
  privateKeyPath: string;
  publicKeyPath: string;
  activationRoot: string;
  signedLicensePath: string;
  receiptPath: string;
  runtimeConfigs: Record<Adlant4RuntimeRole, string>;
  deviceIdentities: Record<Adlant4RuntimeRole, string>;
};

export type Adlant4BootstrapResult = {
  ok: true;
  keyId: string;
  licenseHash: string;
  signedLicensePath: string;
  receiptPath: string;
  publicKeyPath: string;
  privateKeyPath: string;
  runtimeConfigs: Record<Adlant4RuntimeRole, string>;
  deviceIdentities: Record<Adlant4RuntimeRole, string>;
  envelope: SignedLicenseEnvelope;
};

export type Adlant4RuntimeFilePayload = {
  identity: {
    schemaVersion: string;
    deviceId: string;
    terminalId: string;
    businessId: string;
    storeId: string;
    vertical: "commerce";
    role: Adlant4RuntimeRole;
    createdAt: string;
    updatedAt: string;
  };
  runtimeConfig: Record<string, unknown>;
};

export type Adlant4RuntimeFileOptions = {
  licensePath: string;
  deviceIdentityPath: string;
  receiptPath: string;
  issuedAt: string;
  activation?: Record<string, unknown> | null;
  support?: Record<string, unknown> | null;
};

function base64Url(buffer: Buffer): string {
  return buffer.toString("base64").replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function defaultIssuerRoot(): string {
  return path.resolve(process.env.PRISMA_ADLANT4_ISSUER_ROOT || "F:/PRISMA_CTX/LICENSING/issuers/adlant4-local");
}

function defaultActivationRoot(): string {
  return path.resolve(process.env.PRISMA_ADLANT4_ACTIVATION_ROOT || "F:/PRISMA_CTX/LICENSING/activations/prisma-original-customer");
}

function ensureOutsideRepo(target: string): void {
  const repoRoot = path.resolve(process.env.TV_SYSTEM_ROOT || path.join(process.cwd()));
  const resolved = path.resolve(target);
  const relative = path.relative(repoRoot, resolved);
  if (relative && !relative.startsWith("..") && !path.isAbsolute(relative)) {
    throw new Error(`ADLANT4 issuer path must stay outside the repo: ${resolved}`);
  }
}

export function resolveAdlant4IssuerPaths(): Adlant4IssuerPaths {
  const issuerRoot = defaultIssuerRoot();
  const activationRoot = defaultActivationRoot();
  ensureOutsideRepo(issuerRoot);
  ensureOutsideRepo(activationRoot);
  const runtimeRoot = path.join(activationRoot, "runtime");
  return {
    issuerRoot,
    privateKeyPath: path.join(issuerRoot, "private-key.pem"),
    publicKeyPath: path.join(issuerRoot, "public-key.json"),
    activationRoot,
    signedLicensePath: path.join(activationRoot, "license.signed.json"),
    receiptPath: path.join(activationRoot, "activation-receipt.json"),
    runtimeConfigs: {
      pc: path.join(runtimeRoot, "runtime.pc.json"),
      tablet: path.join(runtimeRoot, "runtime.tablet.json"),
      mobile: path.join(runtimeRoot, "runtime.mobile.json")
    },
    deviceIdentities: {
      pc: path.join(runtimeRoot, "device-identity.pc.json"),
      tablet: path.join(runtimeRoot, "device-identity.tablet.json"),
      mobile: path.join(runtimeRoot, "device-identity.mobile.json")
    }
  };
}

function writeJson(file: string, value: unknown): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function ensureKeyPair(paths: Adlant4IssuerPaths): LicensePublicKey {
  fs.mkdirSync(paths.issuerRoot, { recursive: true });
  let privateKeyPem: string;
  let publicKeyPem: string;

  if (fs.existsSync(paths.privateKeyPath)) {
    privateKeyPem = fs.readFileSync(paths.privateKeyPath, "utf8");
    publicKeyPem = crypto.createPublicKey(privateKeyPem).export({ type: "spki", format: "pem" }).toString();
  } else {
    const pair = crypto.generateKeyPairSync("ed25519");
    privateKeyPem = pair.privateKey.export({ type: "pkcs8", format: "pem" }).toString();
    publicKeyPem = pair.publicKey.export({ type: "spki", format: "pem" }).toString();
    fs.writeFileSync(paths.privateKeyPath, privateKeyPem, { encoding: "utf8", mode: 0o600 });
    try {
      fs.chmodSync(paths.privateKeyPath, 0o600);
    } catch {
      // chmod is best-effort on Windows.
    }
  }

  const publicKey: LicensePublicKey = {
    keyId: ADLANT4_LOCAL_KEY_ID,
    alg: "Ed25519",
    label: ADLANT4_ISSUER_LABEL,
    publicKeyPem
  };
  writeJson(paths.publicKeyPath, publicKey);
  return publicKey;
}

export function buildPrismaOriginalCustomerLicenseDocument(now = new Date()): LicenseDocument {
  const validUntil = new Date(now);
  validUntil.setUTCFullYear(validUntil.getUTCFullYear() + 1);
  const devices: AuthorizedLicenseDevice[] = [
    { deviceId: PRISMA_ORIGINAL_CUSTOMER.pcDeviceId, role: "pc", storeId: PRISMA_ORIGINAL_CUSTOMER.storeId },
    { deviceId: PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId, role: "tablet", storeId: PRISMA_ORIGINAL_CUSTOMER.storeId, terminalId: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId },
    { deviceId: PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId, role: "mobile", storeId: PRISMA_ORIGINAL_CUSTOMER.storeId }
  ];
  return {
    schemaVersion: "1.0.0",
    licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId,
    customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
    deviceId: PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId,
    tabletId: PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId,
    terminalId: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId,
    authorizedDevices: devices,
    assignmentState: "assigned",
    plan: "TABLET_PC_MANAGED",
    state: "active",
    validFrom: now.toISOString(),
    validUntil: validUntil.toISOString(),
    issuedAt: now.toISOString(),
    offlineGraceDays: 7,
    limits: {
      maxDevices: 4,
      maxBranches: 1,
      maxStores: 1
    },
    notes: ["ADLANT4 local signed license for Prisma Original Customer."]
  };
}

export function signLicenseDocument(document: LicenseDocument, privateKeyPem: string, keyId = ADLANT4_LOCAL_KEY_ID): SignedLicenseEnvelope {
  const signature = crypto.sign(null, canonicalJsonBuffer(document), privateKeyPem);
  return {
    payload: document,
    signature: base64Url(signature),
    alg: "Ed25519",
    keyId
  };
}

export function buildAdlant4RuntimeFilePayload(role: Adlant4RuntimeRole, options: Adlant4RuntimeFileOptions): Adlant4RuntimeFilePayload {
  const roleSpecs: Record<Adlant4RuntimeRole, { deviceId: string; terminalId: string | null }> = {
    pc: { deviceId: PRISMA_ORIGINAL_CUSTOMER.pcDeviceId, terminalId: null },
    tablet: { deviceId: PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId, terminalId: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId },
    mobile: { deviceId: PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId, terminalId: null }
  };
  const spec = roleSpecs[role];
  const identity = {
    schemaVersion: "1.0.0",
    deviceId: spec.deviceId,
    terminalId: spec.terminalId ?? `${role}_no_terminal`,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
    vertical: "commerce" as const,
    role,
    createdAt: options.issuedAt,
    updatedAt: options.issuedAt
  };
  const runtimeConfig: Record<string, unknown> = {
    schemaVersion: "1.0.0",
    runtimeMode: "customer",
    runtimeProfile: "managed",
    vertical: "commerce",
    role,
    clientId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
    terminalId: spec.terminalId ?? undefined,
    deviceId: spec.deviceId,
    packageType: "TABLET_PC_MANAGED",
    license: { file: options.licensePath, mode: "signed-local" },
    paths: {
      licenseFile: options.licensePath,
      deviceIdentityFile: options.deviceIdentityPath
    },
    support: {
      activationReceipt: options.receiptPath,
      issuer: ADLANT4_ISSUER_LABEL,
      ...(options.support ?? {})
    }
  };
  if (options.activation) runtimeConfig.activation = options.activation;
  return { identity, runtimeConfig };
}

function writeRuntimeFiles(paths: Adlant4IssuerPaths, licensePath: string, issuedAt: string): void {
  const roles: Adlant4RuntimeRole[] = ["pc", "tablet", "mobile"];
  for (const role of roles) {
    const payload = buildAdlant4RuntimeFilePayload(role, {
      licensePath,
      deviceIdentityPath: paths.deviceIdentities[role],
      receiptPath: paths.receiptPath,
      issuedAt
    });
    const identity = payload.identity;
    writeJson(paths.deviceIdentities[role], identity);
    writeJson(paths.runtimeConfigs[role], payload.runtimeConfig);
  }
}

export function bootstrapPrismaOriginalCustomerLicense(): Adlant4BootstrapResult {
  const paths = resolveAdlant4IssuerPaths();
  const publicKey = ensureKeyPair(paths);
  const issuedAt = new Date();
  const document = buildPrismaOriginalCustomerLicenseDocument(issuedAt);
  const privateKeyPem = fs.readFileSync(paths.privateKeyPath, "utf8");
  const envelope = signLicenseDocument(document, privateKeyPem, publicKey.keyId);
  const verification = verifySignedLicenseEnvelope(envelope);
  if (!verification.ok) {
    throw new Error(`ADLANT4_SIGNED_LICENSE_INVALID: ${verification.issues.join("; ")}`);
  }

  writeJson(paths.signedLicensePath, envelope);
  writeRuntimeFiles(paths, paths.signedLicensePath, issuedAt.toISOString());
  const licenseHash = crypto.createHash("sha256").update(fs.readFileSync(paths.signedLicensePath)).digest("hex");
  writeJson(paths.receiptPath, {
    receiptId: `adlant4_activation_${issuedAt.toISOString().replace(/[:.]/g, "-")}`,
    timestamp: issuedAt.toISOString(),
    action: "license.activated",
    source: "adlant4-local-issuer",
    customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    storeId: PRISMA_ORIGINAL_CUSTOMER.storeId,
    licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId,
    plan: "TABLET_PC_MANAGED",
    keyId: publicKey.keyId,
    alg: publicKey.alg,
    licenseHash,
    signedLicensePath: paths.signedLicensePath,
    publicKeyPath: paths.publicKeyPath,
    privateKeyPath: "<outside-repo-redacted>",
    devices: document.authorizedDevices,
    result: "activated",
    verifierNames: ["verify:licdesk:signing", "verify:adlant4:license-governor"],
    rollback: {
      removeFiles: [
        paths.signedLicensePath,
        paths.receiptPath,
        ...Object.values(paths.runtimeConfigs),
        ...Object.values(paths.deviceIdentities)
      ],
      keepPrivateKey: true,
      privateKeyLocation: "<outside-repo-redacted>"
    }
  });

  return {
    ok: true,
    keyId: publicKey.keyId,
    licenseHash,
    signedLicensePath: paths.signedLicensePath,
    receiptPath: paths.receiptPath,
    publicKeyPath: paths.publicKeyPath,
    privateKeyPath: paths.privateKeyPath,
    runtimeConfigs: paths.runtimeConfigs,
    deviceIdentities: paths.deviceIdentities,
    envelope
  };
}
