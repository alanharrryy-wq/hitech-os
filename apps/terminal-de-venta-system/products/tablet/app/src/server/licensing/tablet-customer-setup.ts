import {
  CUSTOMER_SETUP_SLOT_LABELS,
  buildCustomerSetupPass,
  buildSourceReadyClaimResponse,
  customerSetupError,
  normalizeSetupCode,
  type DeviceClaimRequest
} from "../../../../../../shared/licensing";

export const TABLET_CUSTOMER_SETUP_SURFACE = "tablet" as const;
export const TABLET_CUSTOMER_SETUP_SLOT_LABEL = CUSTOMER_SETUP_SLOT_LABELS.tablet;

export function resolveTabletCustomerSetup(setupCode: string) {
  const normalized = normalizeSetupCode(setupCode);
  const code = normalized || "SETUP-CODE-REQUIRED";
  return buildCustomerSetupPass({
    setupCode: code,
    customerMessage: normalized ? "Esta Tablet puede reclamar el Tablet POS Slot cuando Prisma Customer Setup este desplegado." : "Falta el codigo de configuracion.",
    nextStep: normalized ? "Conserva el Setup Code y continua operando ventas locales si la licencia actual lo permite." : "Pega el Setup Code o abre el Setup Link que te enviaron."
  });
}

export function claimTabletCustomerSetup(input: Partial<DeviceClaimRequest>) {
  const setupCode = normalizeSetupCode(input.setupCode);
  if (!setupCode) return customerSetupError("SETUP_CODE_REQUIRED");
  return buildSourceReadyClaimResponse({
    setupCode,
    surface: TABLET_CUSTOMER_SETUP_SURFACE,
    deviceId: input.deviceId || "tablet-pos-source-ready",
    deviceName: input.deviceName || "Tablet POS",
    installationFingerprint: input.installationFingerprint,
    appVersion: input.appVersion,
    operatorLabel: input.operatorLabel
  });
}
