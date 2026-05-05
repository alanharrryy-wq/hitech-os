import crypto from "node:crypto";
import { canonicalJsonBuffer } from "./canonical-json";
import { findLicensePublicKey } from "./license-public-keys";
import { isSignedLicenseEnvelope, type SignedLicenseEnvelope, type SignedLicenseValidation } from "./signed-license-types";
import { validateLicenseDocument } from "./license-schema";

function base64UrlToBuffer(value: string): Buffer {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "===".slice((normalized.length + 3) % 4);
  return Buffer.from(padded, "base64");
}

export function validateSignedLicenseEnvelope(value: unknown): SignedLicenseValidation {
  const issues: string[] = [];
  if (!isSignedLicenseEnvelope(value)) {
    return { ok: false, issues: ["LICENSE_SIGNED_ENVELOPE_INVALID"] };
  }

  if (value.alg !== "Ed25519") issues.push("LICENSE_UNSUPPORTED_ALG");
  if (!value.signature) issues.push("LICENSE_SIGNATURE_MISSING");
  if (!value.keyId) issues.push("LICENSE_KEY_ID_MISSING");

  const payloadValidation = validateLicenseDocument(value.payload);
  if (!payloadValidation.ok) {
    issues.push(...payloadValidation.issues);
    return { ok: false, issues };
  }

  if (issues.length > 0) return { ok: false, issues };
  return { ok: true, value: { ...value, payload: payloadValidation.value } };
}

export function verifySignedLicenseEnvelope(envelope: SignedLicenseEnvelope): { ok: true } | { ok: false; issues: string[] } {
  const validation = validateSignedLicenseEnvelope(envelope);
  if (!validation.ok) return validation;

  const key = findLicensePublicKey(validation.value.keyId, validation.value.alg);
  if (!key) return { ok: false, issues: ["LICENSE_UNKNOWN_KEY"] };

  try {
    const signature = base64UrlToBuffer(validation.value.signature);
    const ok = crypto.verify(null, canonicalJsonBuffer(validation.value.payload), key.publicKeyPem, signature);
    return ok ? { ok: true } : { ok: false, issues: ["LICENSE_SIGNATURE_INVALID"] };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { ok: false, issues: [`LICENSE_SIGNATURE_VERIFY_FAILED: ${message}`] };
  }
}

