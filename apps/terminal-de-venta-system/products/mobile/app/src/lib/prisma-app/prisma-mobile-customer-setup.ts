import {
  CUSTOMER_SETUP_SLOT_LABELS,
  buildCustomerSetupPass,
  buildSourceReadyClaimResponse,
  customerSetupError,
  normalizeSetupCode,
  type DeviceClaimRequest
} from "../../../../../../shared/licensing";

export const MOBILE_CUSTOMER_SETUP_SURFACE = "mobile" as const;
export const MOBILE_CUSTOMER_SETUP_SLOT_LABEL = CUSTOMER_SETUP_SLOT_LABELS.mobile;

export function resolveMobileCustomerSetup(setupCode: string) {
  const normalized = normalizeSetupCode(setupCode);
  const code = normalized || "SETUP-CODE-REQUIRED";
  return buildCustomerSetupPass({
    setupCode: code,
    customerMessage: normalized ? "Este Mobile puede reclamar el Mobile Companion Slot cuando Prisma Customer Setup este desplegado." : "Falta el codigo de configuracion.",
    nextStep: normalized ? "Instala la PWA y conserva el Setup Code para claim cuando soporte confirme el deploy." : "Pega el Setup Code o abre el Setup Link que te enviaron."
  });
}

export function claimMobileCustomerSetup(input: Partial<DeviceClaimRequest>) {
  const setupCode = normalizeSetupCode(input.setupCode);
  if (!setupCode) return customerSetupError("SETUP_CODE_REQUIRED");
  return buildSourceReadyClaimResponse({
    setupCode,
    surface: MOBILE_CUSTOMER_SETUP_SURFACE,
    deviceId: input.deviceId || "mobile-companion-source-ready",
    deviceName: input.deviceName || "Mobile Companion",
    installationFingerprint: input.installationFingerprint,
    appVersion: input.appVersion,
    operatorLabel: input.operatorLabel
  });
}
