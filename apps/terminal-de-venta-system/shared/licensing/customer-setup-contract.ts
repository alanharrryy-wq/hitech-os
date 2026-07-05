export const CUSTOMER_SETUP_SCHEMA_VERSION = "1.0.0";
export const PRISMA_CUSTOMER_SETUP_NAME = "Prisma Customer Setup";
export const PRISMA_SETUP_PASS_NAME = "Setup Pass";
export const PRISMA_TRIPLE_DEVICE_STARTER = "PRISMA_TRIPLE_DEVICE_STARTER";
export const PRISMA_TRIPLE_DEVICE_STARTER_PLAN = "TABLET_PC_MOBILE_MANAGED";

export type CustomerSetupSurface = "tablet" | "pc" | "mobile";
export type CustomerSetupStatus = "active" | "expired" | "revoked" | "draft" | "source_ready";
export type DeviceClaimStatus = "claimed" | "already_claimed" | "slot_full" | "replacement_required" | "source_ready";

export type CustomerSetupErrorCode =
  | "SETUP_CODE_REQUIRED"
  | "SETUP_NOT_FOUND"
  | "SETUP_EXPIRED"
  | "SETUP_REVOKED"
  | "DEVICE_SLOT_FULL"
  | "DEVICE_ALREADY_CLAIMED"
  | "DEVICE_REPLACEMENT_REQUIRED"
  | "SURFACE_NOT_ALLOWED"
  | "CUSTOMER_SETUP_UPSTREAM_FAILED";

export type CustomerSetupSlot = {
  surface: CustomerSetupSurface;
  label: string;
  allowed: number;
  claimed: number;
};

export type CustomerSetupPass = {
  schemaVersion: typeof CUSTOMER_SETUP_SCHEMA_VERSION;
  setupId: string;
  setupCode: string;
  setupUrl: string;
  qrPayload: string;
  customerId: string;
  tenantId: string;
  tenantSlug: string;
  businessId: string;
  businessName: string;
  packageCode: typeof PRISMA_TRIPLE_DEVICE_STARTER | string;
  planCode: typeof PRISMA_TRIPLE_DEVICE_STARTER_PLAN | string;
  status: CustomerSetupStatus;
  expiresAt: string | null;
  slots: CustomerSetupSlot[];
  customerMessage: string;
  nextStep: string;
  secretsExposed: false;
};

export type DeviceClaimRequest = {
  setupCode: string;
  surface: CustomerSetupSurface;
  deviceId: string;
  deviceName?: string;
  installationFingerprint?: string;
  appVersion?: string;
  operatorLabel?: string;
};

export type DeviceClaimResponse = {
  ok: boolean;
  status: DeviceClaimStatus;
  resultCode: "DEVICE_CLAIM_ACCEPTED" | CustomerSetupErrorCode | "CUSTOMER_SETUP_SOURCE_READY";
  customerMessage: string;
  nextStep: string;
  customer: {
    customerId: string;
    displayName: string;
  };
  business: {
    businessId: string;
    displayName: string;
  };
  license: {
    licenseId: string;
    planCode: string;
    state: "active" | "pending" | "source_ready";
  };
  device: {
    deviceId: string;
    surface: CustomerSetupSurface;
    slotLabel: string;
  };
  slots: CustomerSetupSlot[];
  localLicensePayload: {
    signed: false;
    source: "customer-setup-source-ready" | "customer-setup-scaffold";
  };
  secretsExposed: false;
};

export const CUSTOMER_SETUP_SLOT_LABELS: Record<CustomerSetupSurface, string> = {
  tablet: "Tablet POS Slot",
  pc: "PC Admin Slot",
  mobile: "Mobile Companion Slot"
};

export const CUSTOMER_SETUP_ERROR_COPY: Record<CustomerSetupErrorCode, { customerMessage: string; nextStep: string }> = {
  SETUP_CODE_REQUIRED: {
    customerMessage: "Falta el codigo de configuracion.",
    nextStep: "Pega el codigo o abre el Setup Link que te enviaron."
  },
  SETUP_NOT_FOUND: {
    customerMessage: "No encontramos este setup.",
    nextStep: "Revisa el Setup Code o pide un link nuevo a soporte."
  },
  SETUP_EXPIRED: {
    customerMessage: "Este Setup Link expiro.",
    nextStep: "Pide a soporte reenviar un setup nuevo."
  },
  SETUP_REVOKED: {
    customerMessage: "Este setup fue cancelado.",
    nextStep: "Contacta soporte para revisar la cuenta."
  },
  DEVICE_SLOT_FULL: {
    customerMessage: "Ya se uso el cupo para este tipo de dispositivo.",
    nextStep: "Solicita reemplazo autorizado o un cupo adicional."
  },
  DEVICE_ALREADY_CLAIMED: {
    customerMessage: "Este dispositivo ya esta activado.",
    nextStep: "Continua usando la app o revisa soporte si cambiaste de equipo."
  },
  DEVICE_REPLACEMENT_REQUIRED: {
    customerMessage: "Hay otro dispositivo en ese cupo.",
    nextStep: "Solicita reemplazo autorizado antes de reclamar este equipo."
  },
  SURFACE_NOT_ALLOWED: {
    customerMessage: "Este paquete no incluye esta app.",
    nextStep: "Revisa tu plan o contacta soporte."
  },
  CUSTOMER_SETUP_UPSTREAM_FAILED: {
    customerMessage: "No pudimos validar el setup.",
    nextStep: "Reintenta o contacta soporte con evidencia sanitizada."
  }
};

export const PRISMA_TRIPLE_DEVICE_STARTER_SLOTS: readonly CustomerSetupSlot[] = [
  { surface: "tablet", label: CUSTOMER_SETUP_SLOT_LABELS.tablet, allowed: 1, claimed: 0 },
  { surface: "pc", label: CUSTOMER_SETUP_SLOT_LABELS.pc, allowed: 1, claimed: 0 },
  { surface: "mobile", label: CUSTOMER_SETUP_SLOT_LABELS.mobile, allowed: 1, claimed: 0 }
];

export const DEFAULT_CUSTOMER_SETUP_PASS: CustomerSetupPass = {
  schemaVersion: CUSTOMER_SETUP_SCHEMA_VERSION,
  setupId: "setup_prisma_triple_device_starter",
  setupCode: "PRISMA-SETUP-STARTER",
  setupUrl: "https://app.hitechrts.com/setup/PRISMA-SETUP-STARTER",
  qrPayload: "prisma://setup/PRISMA-SETUP-STARTER",
  customerId: "cust_prisma_original_customer",
  tenantId: "tenant_prisma_original_customer",
  tenantSlug: "prisma-original-customer",
  businessId: "biz_prisma_original_customer",
  businessName: "Prisma Original Customer",
  packageCode: PRISMA_TRIPLE_DEVICE_STARTER,
  planCode: PRISMA_TRIPLE_DEVICE_STARTER_PLAN,
  status: "source_ready",
  expiresAt: null,
  slots: PRISMA_TRIPLE_DEVICE_STARTER_SLOTS.map((slot) => ({ ...slot })),
  customerMessage: "Prisma Customer Setup esta listo en fuente; requiere deploy autorizado del Cloud License Gateway para uso live.",
  nextStep: "Usa Setup Link, Setup Code o Setup QR cuando el gateway este desplegado.",
  secretsExposed: false
};

export function normalizeSetupCode(value: unknown): string {
  return String(value ?? "").trim().toUpperCase();
}

export function isCustomerSetupSurface(value: unknown): value is CustomerSetupSurface {
  return value === "tablet" || value === "pc" || value === "mobile";
}

export function customerSetupError(code: CustomerSetupErrorCode): DeviceClaimResponse {
  const copy = CUSTOMER_SETUP_ERROR_COPY[code];
  return {
    ok: false,
    status: code === "DEVICE_SLOT_FULL" ? "slot_full" : code === "DEVICE_ALREADY_CLAIMED" ? "already_claimed" : code === "DEVICE_REPLACEMENT_REQUIRED" ? "replacement_required" : "source_ready",
    resultCode: code,
    customerMessage: copy.customerMessage,
    nextStep: copy.nextStep,
    customer: { customerId: DEFAULT_CUSTOMER_SETUP_PASS.customerId, displayName: DEFAULT_CUSTOMER_SETUP_PASS.businessName },
    business: { businessId: DEFAULT_CUSTOMER_SETUP_PASS.businessId, displayName: DEFAULT_CUSTOMER_SETUP_PASS.businessName },
    license: { licenseId: "lic_prisma_customer_setup_pending", planCode: DEFAULT_CUSTOMER_SETUP_PASS.planCode, state: "pending" },
    device: { deviceId: "unknown", surface: "tablet", slotLabel: CUSTOMER_SETUP_SLOT_LABELS.tablet },
    slots: DEFAULT_CUSTOMER_SETUP_PASS.slots.map((slot) => ({ ...slot })),
    localLicensePayload: { signed: false, source: "customer-setup-source-ready" },
    secretsExposed: false
  };
}

export function buildSourceReadyClaimResponse(request: DeviceClaimRequest): DeviceClaimResponse {
  const surface = isCustomerSetupSurface(request.surface) ? request.surface : "tablet";
  return {
    ok: true,
    status: "source_ready",
    resultCode: "CUSTOMER_SETUP_SOURCE_READY",
    customerMessage: `Este dispositivo esta listo para reclamar ${CUSTOMER_SETUP_SLOT_LABELS[surface]} cuando Prisma Customer Setup este desplegado.`,
    nextStep: "Conserva el Setup Code y reintenta cuando soporte confirme el deploy del Cloud License Gateway.",
    customer: { customerId: DEFAULT_CUSTOMER_SETUP_PASS.customerId, displayName: DEFAULT_CUSTOMER_SETUP_PASS.businessName },
    business: { businessId: DEFAULT_CUSTOMER_SETUP_PASS.businessId, displayName: DEFAULT_CUSTOMER_SETUP_PASS.businessName },
    license: { licenseId: "lic_prisma_customer_setup_pending", planCode: DEFAULT_CUSTOMER_SETUP_PASS.planCode, state: "source_ready" },
    device: {
      deviceId: request.deviceId || `${surface}-device-pending`,
      surface,
      slotLabel: CUSTOMER_SETUP_SLOT_LABELS[surface]
    },
    slots: DEFAULT_CUSTOMER_SETUP_PASS.slots.map((slot) => slot.surface === surface ? { ...slot, claimed: Math.min(slot.allowed, Math.max(slot.claimed, 0)) } : { ...slot }),
    localLicensePayload: { signed: false, source: "customer-setup-source-ready" },
    secretsExposed: false
  };
}

export function buildCustomerSetupPass(overrides: Partial<CustomerSetupPass> = {}): CustomerSetupPass {
  const setupCode = normalizeSetupCode(overrides.setupCode ?? DEFAULT_CUSTOMER_SETUP_PASS.setupCode);
  return {
    ...DEFAULT_CUSTOMER_SETUP_PASS,
    ...overrides,
    setupCode,
    setupUrl: overrides.setupUrl ?? `https://app.hitechrts.com/setup/${encodeURIComponent(setupCode)}`,
    qrPayload: overrides.qrPayload ?? `prisma://setup/${encodeURIComponent(setupCode)}`,
    slots: (overrides.slots ?? DEFAULT_CUSTOMER_SETUP_PASS.slots).map((slot) => ({ ...slot })),
    secretsExposed: false
  };
}
