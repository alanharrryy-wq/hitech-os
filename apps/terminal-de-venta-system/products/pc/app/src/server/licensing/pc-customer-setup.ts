import {
  CUSTOMER_SETUP_SLOT_LABELS,
  buildCustomerSetupPass,
  buildSourceReadyClaimResponse,
  customerSetupError,
  normalizeSetupCode,
  type DeviceClaimRequest
} from "../../../../../../shared/licensing";

export const PC_CUSTOMER_SETUP_SURFACE = "pc" as const;
export const PC_CUSTOMER_SETUP_SLOT_LABEL = CUSTOMER_SETUP_SLOT_LABELS.pc;

export function resolvePcCustomerSetup(setupCode: string) {
  const normalized = normalizeSetupCode(setupCode);
  const code = normalized || "SETUP-CODE-REQUIRED";
  return buildCustomerSetupPass({
    setupCode: code,
    customerMessage: normalized ? "Esta PC puede reclamar el PC Admin Slot cuando Prisma Customer Setup este desplegado." : "Falta el codigo de configuracion.",
    nextStep: normalized ? "Conserva el Setup Code y revisa licencia/runtime sin exponer admin token." : "Pega el Setup Code o abre el Setup Link que te enviaron."
  });
}

export function claimPcCustomerSetup(input: Partial<DeviceClaimRequest>) {
  const setupCode = normalizeSetupCode(input.setupCode);
  if (!setupCode) return customerSetupError("SETUP_CODE_REQUIRED");
  return buildSourceReadyClaimResponse({
    setupCode,
    surface: PC_CUSTOMER_SETUP_SURFACE,
    deviceId: input.deviceId || "pc-admin-source-ready",
    deviceName: input.deviceName || "PC Admin",
    installationFingerprint: input.installationFingerprint,
    appVersion: input.appVersion,
    operatorLabel: input.operatorLabel
  });
}
