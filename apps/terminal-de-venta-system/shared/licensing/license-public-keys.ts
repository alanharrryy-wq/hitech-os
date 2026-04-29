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

export function findLicensePublicKey(keyId: string, alg: string): LicensePublicKey | null {
  return PRISMA_LICENSE_PUBLIC_KEYS.find((key) => key.keyId === keyId && key.alg === alg) ?? null;
}
