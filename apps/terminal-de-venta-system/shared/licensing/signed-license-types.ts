import type { LicenseDocument } from "./license-types";

export type SignedLicenseAlgorithm = "Ed25519";

export type SignedLicenseEnvelope = {
  payload: LicenseDocument;
  signature: string;
  alg: SignedLicenseAlgorithm;
  keyId: string;
};

export type SignedLicenseValidation =
  | { ok: true; value: SignedLicenseEnvelope }
  | { ok: false; issues: string[] };

export function isSignedLicenseEnvelope(value: unknown): value is SignedLicenseEnvelope {
  const record = value as Partial<SignedLicenseEnvelope> | null;
  return Boolean(
    record &&
      typeof record === "object" &&
      typeof record.signature === "string" &&
      typeof record.alg === "string" &&
      typeof record.keyId === "string" &&
      record.payload &&
      typeof record.payload === "object"
  );
}
