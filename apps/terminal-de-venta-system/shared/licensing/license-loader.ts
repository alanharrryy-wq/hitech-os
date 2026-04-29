import fs from "node:fs";
import { validateLicenseDocument } from "./license-schema";
import { invalidLicenseStatus, missingLicenseStatus, normalizeLicenseDocument } from "./license-normalizer";
import { resolveLocalLicensePath } from "./license-paths";
import { isSignedLicenseEnvelope } from "./signed-license-types";
import { validateSignedLicenseEnvelope, verifySignedLicenseEnvelope } from "./license-signature";
import type { NormalizedLicenseStatus } from "./license-types";

function allowUnsignedDevLicense(source: string): boolean {
  if (process.env.PRISMA_LICENSE_ALLOW_UNSIGNED === "1") return true;
  if (process.env.PRISMA_LICENSE_REQUIRE_SIGNED_DEV === "1") return false;
  return source === "dev";
}

export function loadLocalLicense(): NormalizedLicenseStatus {
  const resolved = resolveLocalLicensePath();
  if (!resolved.exists) return missingLicenseStatus(resolved.path);

  let parsed: unknown;
  try {
    parsed = JSON.parse(fs.readFileSync(resolved.path, "utf8"));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return invalidLicenseStatus(resolved.path, [`LICENSE_INVALID_JSON: ${message}`]);
  }

  if (isSignedLicenseEnvelope(parsed)) {
    const validation = validateSignedLicenseEnvelope(parsed);
    if (!validation.ok) return invalidLicenseStatus(resolved.path, validation.issues);
    const signature = verifySignedLicenseEnvelope(validation.value);
    if (!signature.ok) return invalidLicenseStatus(resolved.path, signature.issues);
    return normalizeLicenseDocument(validation.value.payload, { source: resolved.source === "dev" ? "dev_file" : "local_file", path: resolved.path });
  }

  if (!allowUnsignedDevLicense(resolved.source)) {
    return invalidLicenseStatus(resolved.path, ["LICENSE_SIGNATURE_MISSING"]);
  }

  const validation = validateLicenseDocument(parsed);
  if (!validation.ok) return invalidLicenseStatus(resolved.path, validation.issues);
  const status = normalizeLicenseDocument(validation.value, { source: resolved.source === "dev" ? "dev_file" : "local_file", path: resolved.path });
  return { ...status, warnings: [...status.warnings, { code: "LICENSE_UNSIGNED_DEV", message: "Licencia sin firma aceptada solo para desarrollo/local." }] };
}
