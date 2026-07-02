import fs from "node:fs";

export type LicensePublicKey = {
  keyId: string;
  alg: "Ed25519";
  publicKeyPem: string;
  label: string;
};

export const PRISMA_LICENSE_PUBLIC_KEYS: LicensePublicKey[] = [
  {
    keyId: "prisma_dev_2026_02cd",
    alg: "Ed25519",
    label: "PRISMA DEV 02CD Ed25519 key. Replace for production.",
    publicKeyPem: "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA6O5Ql5/3UKOFfaMVZlhPw9+REGHkdNKjHXnW48eRzeg=\n-----END PUBLIC KEY-----\n"
  }
];

const DEFAULT_EXTERNAL_PUBLIC_KEY_FILES = [
  process.env.PRISMA_LICENSE_PUBLIC_KEY_REGISTRY,
  "F:/PRISMA_CTX/LICENSING/issuers/adlant4-local/public-key.json",
  "F:/PRISMA_CTX/LICENSING/public-keys.json"
].filter((value): value is string => Boolean(value));

function isLicensePublicKey(value: unknown): value is LicensePublicKey {
  const record = value as Partial<LicensePublicKey> | null;
  return Boolean(
    record &&
      typeof record === "object" &&
      typeof record.keyId === "string" &&
      record.alg === "Ed25519" &&
      typeof record.publicKeyPem === "string" &&
      typeof record.label === "string"
  );
}

function readExternalPublicKeys(): LicensePublicKey[] {
  const keys: LicensePublicKey[] = [];
  for (const file of DEFAULT_EXTERNAL_PUBLIC_KEY_FILES) {
    try {
      if (!fs.existsSync(file)) continue;
      const parsed = JSON.parse(fs.readFileSync(file, "utf8")) as unknown;
      const candidates = Array.isArray(parsed) ? parsed : [parsed];
      for (const candidate of candidates) {
        if (isLicensePublicKey(candidate)) keys.push(candidate);
      }
    } catch {
      // Public key registry read errors are ignored here; verifiers report missing keys explicitly.
    }
  }
  return keys;
}

export function getLicensePublicKeys(): LicensePublicKey[] {
  const byId = new Map<string, LicensePublicKey>();
  for (const key of [...PRISMA_LICENSE_PUBLIC_KEYS, ...readExternalPublicKeys()]) {
    byId.set(`${key.alg}:${key.keyId}`, key);
  }
  return [...byId.values()];
}

export function findLicensePublicKey(keyId: string, alg: string): LicensePublicKey | null {
  return getLicensePublicKeys().find((key) => key.keyId === keyId && key.alg === alg) ?? null;
}
