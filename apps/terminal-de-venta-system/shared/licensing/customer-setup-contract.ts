export const CUSTOMER_SETUP_SCHEMA_VERSION = "1.0.0";
export const PRISMA_CUSTOMER_SETUP_NAME = "Prisma Customer Setup";
export const PRISMA_SETUP_PASS_NAME = "Setup Pass";
export const PRISMA_TRIPLE_DEVICE_STARTER = "PRISMA_TRIPLE_DEVICE_STARTER";
export const PRISMA_TRIPLE_DEVICE_STARTER_PLAN = "TABLET_PC_MOBILE_MANAGED";

export type CustomerSetupSurface = "tablet" | "pc" | "mobile";
export type CustomerSetupStatus = "active" | "expired" | "revoked" | "draft" | "source_ready";
export type DeviceClaimStatus = "claimed" | "already_claimed" | "slot_full" | "replacement_required" | "replaced" | "source_ready";
export type DeviceClaimSlotStatus = "AVAILABLE" | "CLAIMED" | "EXPIRED" | "REVOKED";
export type CustomerLicenseCommercialStatus = "active" | "expiring" | "grace_period" | "suspended" | "revoked" | "renewed";
export type CustomerSetupPlanId = "TABLET_SOLO" | "TABLET_PRO" | "TABLET_PC_MANAGED" | typeof PRISMA_TRIPLE_DEVICE_STARTER_PLAN;
export type CustomerSetupMode = "setup_link_code_qr";
export type CustomerClaimMode = "auto_generated_claim_slots";

export type CustomerSetupErrorCode =
  | "SETUP_CODE_REQUIRED"
  | "SETUP_NOT_FOUND"
  | "SETUP_EXPIRED"
  | "SETUP_REVOKED"
  | "DEVICE_SLOT_FULL"
  | "DEVICE_ALREADY_CLAIMED"
  | "DEVICE_REPLACEMENT_REQUIRED"
  | "DEVICE_REPLACEMENT_DEVICE_IDS_REQUIRED"
  | "DEVICE_REPLACEMENT_NOT_ALLOWED"
  | "DEVICE_NOT_CLAIMED"
  | "DEVICE_ID_REQUIRED"
  | "SURFACE_NOT_ALLOWED"
  | "CUSTOMER_SETUP_UPSTREAM_FAILED"
  | "LICENSE_SUSPENDED"
  | "LICENSE_REVOKED"
  | "LICENSE_EXPIRED";

export type CustomerSetupSlot = {
  surface: CustomerSetupSurface;
  label: string;
  allowed: number;
  claimed: number;
  status?: DeviceClaimSlotStatus;
  claimCode?: string;
  expiresAt?: string | null;
};

export type PlanProvisioningDefinition = {
  planId: CustomerSetupPlanId;
  planName: string;
  maxTabletDevices: number;
  maxPcDevices: number;
  maxMobileDevices: number;
  maxTotalDevices: number;
  allowedSurfaces: CustomerSetupSurface[];
  features: string[];
  setupMode: CustomerSetupMode;
  claimMode: CustomerClaimMode;
  requiresManualApproval: boolean;
  expirationPolicy: string;
  gracePolicy: string;
  renewalPolicy: string;
};

export type DeviceClaimSlot = {
  slotId: string;
  setupBundleId: string;
  clientId: string;
  licenseId: string;
  planId: CustomerSetupPlanId | string;
  surface: CustomerSetupSurface;
  status: DeviceClaimSlotStatus;
  claimCode: string;
  deviceId: string | null;
  claimedAt: string | null;
  expiresAt: string;
  auditEventId: string | null;
};

export type PlanBasedProvisioningResult = {
  resultCode: "PLAN_BASED_CUSTOMER_ONBOARDING_READY";
  clientId: string;
  tenantId: string;
  businessId: string;
  licenseId: string;
  licenseAssignmentId: string;
  setupBundleId: string;
  setupCode: string;
  setupLink: string;
  setupQrPayload: string;
  plan: PlanProvisioningDefinition;
  deviceClaimSlots: DeviceClaimSlot[];
  operatorActionCount: 1;
  manualDeviceClaimRequired: false;
  auditEventId: string | null;
};

export type CustomerSetupPass = {
  schemaVersion: typeof CUSTOMER_SETUP_SCHEMA_VERSION;
  setupId: string;
  setupBundleId: string;
  setupCode: string;
  setupUrl: string;
  qrPayload: string;
  customerId: string;
  tenantId: string;
  tenantSlug: string;
  businessId: string;
  businessName: string;
  packageCode: typeof PRISMA_TRIPLE_DEVICE_STARTER | string;
  planId: CustomerSetupPlanId | string;
  planCode: typeof PRISMA_TRIPLE_DEVICE_STARTER_PLAN | string;
  licenseId: string;
  licenseAssignmentId: string;
  status: CustomerSetupStatus;
  expiresAt: string | null;
  slots: CustomerSetupSlot[];
  deviceClaimSlots: DeviceClaimSlot[];
  operatorActionCount: 1;
  manualDeviceClaimRequired: false;
  auditEventId: string | null;
  customerMessage: string;
  nextStep: string;
  secretsExposed: false;
};

export type CustomerPortalSnapshot = {
  ok: true;
  status: "CUSTOMER_PORTAL_READY";
  resultCode: "CUSTOMER_PORTAL_READY";
  tenant: {
    tenantSlug: string;
    businessName: string;
  };
  setup: {
    setupCode: string;
    setupLink: string;
    setupQr: string;
    status: CustomerSetupStatus;
    expiresAt: string | null;
  };
  slots: CustomerSetupSlot[];
  devices: Array<{
    deviceId: string;
    deviceName?: string;
    surface: CustomerSetupSurface;
    status: DeviceClaimStatus;
    claimedAt?: string;
    replacedAt?: string | null;
  }>;
  license: {
    licenseId: string;
    status: CustomerLicenseCommercialStatus | "expired" | "pending";
    planCode: string;
    validUntil: string | null;
  };
  magicLink: {
    href: string;
    scope: "setup-pass-only";
    admin: false;
  };
  support: {
    replacementRequestAvailable: boolean;
    nextStep: string;
  };
  secretsExposed: false;
};

export type CustomerLicenseRefreshResponse = {
  ok: boolean;
  status: "refreshed" | CustomerLicenseCommercialStatus | "expired";
  resultCode:
    | "LICENSE_REFRESHED"
    | "DEVICE_NOT_CLAIMED"
    | "LICENSE_SUSPENDED"
    | "LICENSE_REVOKED"
    | "LICENSE_EXPIRED"
    | CustomerSetupErrorCode;
  setupCode?: string;
  device?: {
    deviceId: string;
    surface: CustomerSetupSurface;
    status: DeviceClaimStatus;
    claimId: string;
  };
  license?: {
    licenseId: string;
    planCode: string;
    state: CustomerLicenseCommercialStatus | "expired" | "pending";
    validUntil: string | null;
    signed: false;
  };
  customerMessage: string;
  nextStep: string;
  secretsExposed: false;
};

export type DeviceReplacementRequest = {
  setupCode: string;
  surface: CustomerSetupSurface;
  oldDeviceId: string;
  newDeviceId: string;
  reason: string;
};

export type DeviceReplacementResponse = {
  ok: boolean;
  status: "REPLACEMENT_REQUESTED" | "DEVICE_REPLACEMENT_APPROVED" | "DEVICE_REPLACEMENT_NOT_ALLOWED";
  resultCode: "REPLACEMENT_REQUESTED" | "DEVICE_REPLACEMENT_APPROVED" | "DEVICE_REPLACEMENT_NOT_ALLOWED";
  replacementRequestId?: string;
  setupCode?: string;
  surface?: CustomerSetupSurface;
  oldDeviceId?: string;
  newDeviceId?: string;
  customerMessage?: string;
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
  DEVICE_REPLACEMENT_DEVICE_IDS_REQUIRED: {
    customerMessage: "Falta identificar el equipo anterior y el nuevo.",
    nextStep: "Reintenta desde la app o contacta soporte."
  },
  DEVICE_REPLACEMENT_NOT_ALLOWED: {
    customerMessage: "No encontramos un dispositivo activo para reemplazar en ese cupo.",
    nextStep: "Verifica el equipo anterior o contacta soporte."
  },
  DEVICE_NOT_CLAIMED: {
    customerMessage: "Este dispositivo no esta reclamado en este setup.",
    nextStep: "Reclama el dispositivo o contacta soporte."
  },
  DEVICE_ID_REQUIRED: {
    customerMessage: "Falta identificar este dispositivo.",
    nextStep: "Reintenta desde la app para generar el identificador local."
  },
  SURFACE_NOT_ALLOWED: {
    customerMessage: "Este paquete no incluye esta app.",
    nextStep: "Revisa tu plan o contacta soporte."
  },
  CUSTOMER_SETUP_UPSTREAM_FAILED: {
    customerMessage: "No pudimos validar el setup.",
    nextStep: "Reintenta o contacta soporte con evidencia sanitizada."
  },
  LICENSE_SUSPENDED: {
    customerMessage: "Licencia suspendida.",
    nextStep: "Contacta soporte para reactivar la cuenta."
  },
  LICENSE_REVOKED: {
    customerMessage: "Licencia revocada.",
    nextStep: "Contacta soporte para revisar la cuenta."
  },
  LICENSE_EXPIRED: {
    customerMessage: "Licencia vencida.",
    nextStep: "Renueva o contacta soporte para reactivar la cuenta."
  }
};

export const PRISMA_TRIPLE_DEVICE_STARTER_SLOTS: readonly CustomerSetupSlot[] = [
  { surface: "tablet", label: CUSTOMER_SETUP_SLOT_LABELS.tablet, allowed: 1, claimed: 0 },
  { surface: "pc", label: CUSTOMER_SETUP_SLOT_LABELS.pc, allowed: 1, claimed: 0 },
  { surface: "mobile", label: CUSTOMER_SETUP_SLOT_LABELS.mobile, allowed: 1, claimed: 0 }
];

export const PLAN_BASED_PROVISIONING_CATALOG: Record<CustomerSetupPlanId, PlanProvisioningDefinition> = {
  TABLET_SOLO: {
    planId: "TABLET_SOLO",
    planName: "Tablet Solo",
    maxTabletDevices: 1,
    maxPcDevices: 0,
    maxMobileDevices: 0,
    maxTotalDevices: 1,
    allowedSurfaces: ["tablet"],
    features: ["pos.local_sale", "catalog.local", "cash.local"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  },
  TABLET_PRO: {
    planId: "TABLET_PRO",
    planName: "Tablet Pro",
    maxTabletDevices: 2,
    maxPcDevices: 0,
    maxMobileDevices: 1,
    maxTotalDevices: 3,
    allowedSurfaces: ["tablet", "mobile"],
    features: ["pos.local_sale", "returns", "outbox.visible", "mobile.supervision"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  },
  TABLET_PC_MANAGED: {
    planId: "TABLET_PC_MANAGED",
    planName: "Tablet + PC Managed",
    maxTabletDevices: 2,
    maxPcDevices: 1,
    maxMobileDevices: 1,
    maxTotalDevices: 4,
    allowedSurfaces: ["tablet", "pc", "mobile"],
    features: ["pos.local_sale", "pc.backoffice", "sync.audit", "mobile.supervision"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  },
  TABLET_PC_MOBILE_MANAGED: {
    planId: PRISMA_TRIPLE_DEVICE_STARTER_PLAN,
    planName: "Tablet + PC + Mobile Managed",
    maxTabletDevices: 1,
    maxPcDevices: 1,
    maxMobileDevices: 1,
    maxTotalDevices: 3,
    allowedSurfaces: ["tablet", "pc", "mobile"],
    features: ["pos.local_sale", "pc.backoffice", "mobile.companion", "customer.setup"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  }
};

export function resolvePlanProvisioningDefinition(planId: string | undefined | null): PlanProvisioningDefinition {
  return PLAN_BASED_PROVISIONING_CATALOG[(planId || PRISMA_TRIPLE_DEVICE_STARTER_PLAN) as CustomerSetupPlanId] ?? PLAN_BASED_PROVISIONING_CATALOG[PRISMA_TRIPLE_DEVICE_STARTER_PLAN];
}

export function aggregateSlotsForPlan(plan: PlanProvisioningDefinition): CustomerSetupSlot[] {
  const surfaces: CustomerSetupSurface[] = ["tablet", "pc", "mobile"];
  return surfaces.map((surface) => ({
    surface,
    label: CUSTOMER_SETUP_SLOT_LABELS[surface],
    allowed: surface === "tablet" ? plan.maxTabletDevices : surface === "pc" ? plan.maxPcDevices : plan.maxMobileDevices,
    claimed: 0
  })).filter((slot) => slot.allowed > 0);
}

export function buildDeviceClaimSlotsForPlan(input: {
  setupBundleId: string;
  clientId: string;
  licenseId: string;
  plan: PlanProvisioningDefinition;
  expiresAt: string;
  setupCode: string;
  auditEventId?: string | null;
}): DeviceClaimSlot[] {
  const slots: DeviceClaimSlot[] = [];
  for (const surface of input.plan.allowedSurfaces) {
    const count = surface === "tablet" ? input.plan.maxTabletDevices : surface === "pc" ? input.plan.maxPcDevices : input.plan.maxMobileDevices;
    for (let index = 1; index <= count; index += 1) {
      slots.push({
        slotId: `${input.setupBundleId}_${surface}_${index}`,
        setupBundleId: input.setupBundleId,
        clientId: input.clientId,
        licenseId: input.licenseId,
        planId: input.plan.planId,
        surface,
        status: "AVAILABLE",
        claimCode: `${input.setupCode}-${surface.toUpperCase()}-${String(index).padStart(2, "0")}`,
        deviceId: null,
        claimedAt: null,
        expiresAt: input.expiresAt,
        auditEventId: input.auditEventId ?? null
      });
    }
  }
  return slots;
}

export const DEFAULT_CUSTOMER_SETUP_PASS: CustomerSetupPass = {
  schemaVersion: CUSTOMER_SETUP_SCHEMA_VERSION,
  setupId: "setup_prisma_triple_device_starter",
  setupBundleId: "bundle_prisma_triple_device_starter",
  setupCode: "PRISMA-SETUP-STARTER",
  setupUrl: "https://app.hitechrts.com/setup/PRISMA-SETUP-STARTER",
  qrPayload: "prisma://setup/PRISMA-SETUP-STARTER",
  customerId: "cust_prisma_original_customer",
  tenantId: "tenant_prisma_original_customer",
  tenantSlug: "prisma-original-customer",
  businessId: "biz_prisma_original_customer",
  businessName: "Prisma Original Customer",
  packageCode: PRISMA_TRIPLE_DEVICE_STARTER,
  planId: PRISMA_TRIPLE_DEVICE_STARTER_PLAN,
  planCode: PRISMA_TRIPLE_DEVICE_STARTER_PLAN,
  licenseId: "lic_prisma_triple_device_starter",
  licenseAssignmentId: "assign_prisma_triple_device_starter",
  status: "source_ready",
  expiresAt: null,
  slots: PRISMA_TRIPLE_DEVICE_STARTER_SLOTS.map((slot) => ({ ...slot })),
  deviceClaimSlots: buildDeviceClaimSlotsForPlan({
    setupBundleId: "bundle_prisma_triple_device_starter",
    clientId: "cust_prisma_original_customer",
    licenseId: "lic_prisma_triple_device_starter",
    plan: PLAN_BASED_PROVISIONING_CATALOG[PRISMA_TRIPLE_DEVICE_STARTER_PLAN],
    expiresAt: "2099-12-31T23:59:59.000Z",
    setupCode: "PRISMA-SETUP-STARTER",
    auditEventId: "audit_prisma_triple_device_starter"
  }),
  operatorActionCount: 1,
  manualDeviceClaimRequired: false,
  auditEventId: "audit_prisma_triple_device_starter",
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
  const plan = resolvePlanProvisioningDefinition(String(overrides.planId ?? overrides.planCode ?? DEFAULT_CUSTOMER_SETUP_PASS.planId));
  const setupBundleId = overrides.setupBundleId ?? overrides.setupId ?? DEFAULT_CUSTOMER_SETUP_PASS.setupBundleId;
  const licenseId = overrides.licenseId ?? DEFAULT_CUSTOMER_SETUP_PASS.licenseId;
  const expiresAt = overrides.expiresAt ?? DEFAULT_CUSTOMER_SETUP_PASS.expiresAt ?? "2099-12-31T23:59:59.000Z";
  return {
    ...DEFAULT_CUSTOMER_SETUP_PASS,
    ...overrides,
    setupBundleId,
    setupCode,
    setupUrl: overrides.setupUrl ?? `https://app.hitechrts.com/setup/${encodeURIComponent(setupCode)}`,
    qrPayload: overrides.qrPayload ?? `prisma://setup/${encodeURIComponent(setupCode)}`,
    planId: overrides.planId ?? plan.planId,
    planCode: overrides.planCode ?? plan.planId,
    licenseId,
    licenseAssignmentId: overrides.licenseAssignmentId ?? DEFAULT_CUSTOMER_SETUP_PASS.licenseAssignmentId,
    slots: (overrides.slots ?? aggregateSlotsForPlan(plan)).map((slot) => ({ ...slot })),
    deviceClaimSlots: (overrides.deviceClaimSlots ?? buildDeviceClaimSlotsForPlan({
      setupBundleId,
      clientId: overrides.customerId ?? DEFAULT_CUSTOMER_SETUP_PASS.customerId,
      licenseId,
      plan,
      expiresAt,
      setupCode,
      auditEventId: overrides.auditEventId ?? DEFAULT_CUSTOMER_SETUP_PASS.auditEventId
    })).map((slot) => ({ ...slot })),
    operatorActionCount: 1,
    manualDeviceClaimRequired: false,
    auditEventId: overrides.auditEventId ?? DEFAULT_CUSTOMER_SETUP_PASS.auditEventId,
    secretsExposed: false
  };
}
