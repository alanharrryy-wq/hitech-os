import fs from "node:fs";
import { resolveRuntimeContext, type RuntimeContext } from "../runtime";
import { validateLicenseDocument } from "./license-schema";
import { invalidLicenseStatus, missingLicenseStatus, normalizeLicenseDocument } from "./license-normalizer";
import { resolveLocalLicensePath } from "./license-paths";
import { isSignedLicenseEnvelope } from "./signed-license-types";
import { validateSignedLicenseEnvelope, verifySignedLicenseEnvelope } from "./license-signature";
import type { LicenseAssignmentState, LicenseDocument, NormalizedLicenseStatus } from "./license-types";

function allowUnsignedDevLicense(source: string, context: RuntimeContext): boolean {
  if (process.env.PRISMA_LICENSE_ALLOW_UNSIGNED === "1") return true;
  if (process.env.PRISMA_LICENSE_REQUIRE_SIGNED_DEV === "1") return false;
  return source === "dev" && context.runtimeMode === "dev";
}

function assignmentFromRuntimeContext(document: LicenseDocument, context: RuntimeContext): LicenseAssignmentState | null {
  if (document.assignmentState && document.assignmentState !== "assigned") return document.assignmentState;

  if (context.businessId && document.businessId && context.businessId !== document.businessId) return "wrong_business";

  const documentStore = document.storeId ?? document.branchId;
  if (context.storeId && documentStore && context.storeId !== documentStore) return "wrong_store";

  const documentDevice = document.deviceId ?? document.tabletId;
  if (context.deviceId && documentDevice && context.deviceId !== documentDevice) return "wrong_device";

  if (context.terminalId && document.terminalId && context.terminalId !== document.terminalId) return "wrong_terminal";

  return null;
}

export function loadLocalLicense(): NormalizedLicenseStatus {
  const context = resolveRuntimeContext();
  const resolved = resolveLocalLicensePath();
  if (!resolved.exists) return missingLicenseStatus(resolved.path, { customerMode: context.runtimeMode === "customer" || context.runtimeMode === "release" });

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
    return normalizeLicenseDocument(validation.value.payload, {
      source: resolved.source === "dev" ? "dev_file" : "local_file",
      path: resolved.path,
      assignmentState: assignmentFromRuntimeContext(validation.value.payload, context),
      warnings: context.warnings.map((issue) => ({ code: issue.code, message: issue.message }))
    });
  }

  if (!allowUnsignedDevLicense(resolved.source, context)) {
    return invalidLicenseStatus(resolved.path, ["LICENSE_SIGNATURE_MISSING"]);
  }

  const validation = validateLicenseDocument(parsed);
  if (!validation.ok) return invalidLicenseStatus(resolved.path, validation.issues);
  const status = normalizeLicenseDocument(validation.value, {
    source: resolved.source === "dev" ? "dev_file" : "local_file",
    path: resolved.path,
    assignmentState: assignmentFromRuntimeContext(validation.value, context),
    warnings: context.warnings.map((issue) => ({ code: issue.code, message: issue.message }))
  });
  return { ...status, warnings: [...status.warnings, { code: "LICENSE_UNSIGNED_DEV", message: "Licencia sin firma aceptada solo para desarrollo/local." }] };
}
