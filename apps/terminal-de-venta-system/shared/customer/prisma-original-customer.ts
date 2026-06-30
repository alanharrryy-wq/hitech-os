export const PRISMA_ORIGINAL_CUSTOMER = {
  displayName: "Prisma Original Customer",
  customerId: "cust_prisma_original_customer",
  tenantId: "tenant_prisma_original_customer",
  licenseId: "lic_prisma_original_customer_001",
  planLabel: "Business",
  businessId: "biz_78b3c840796a4a4dad",
  storeId: "store_00728649f3804a9e82",
  storeName: "Sucursal principal",
  tabletTerminalId: "term_49103c7382d84663a3",
  tabletTerminalName: "Tablet Caja 1",
  secondaryTabletTerminalId: "term_064de66650df46e0b2",
  pcDeviceId: "pc_prisma_original_customer_001",
  tabletDeviceId: "tablet_prisma_original_customer_001",
  mobileDeviceId: "mobile_prisma_original_customer_001"
} as const;

export const PRISMA_LEGACY_LOCAL_IDS = {
  businessIds: new Set(["biz_tablet_standalone", "biz_demo", "demo-prisma-store"]),
  terminalIds: new Set(["terminal_tablet_local_01", "tablet-terminal-001"])
} as const;

export function normalizePrismaOriginalBusinessId(value: unknown): string {
  const incoming = typeof value === "string" ? value.trim() : "";
  if (!incoming || PRISMA_LEGACY_LOCAL_IDS.businessIds.has(incoming)) return PRISMA_ORIGINAL_CUSTOMER.businessId;
  return incoming;
}

export function normalizePrismaOriginalTerminalId(value: unknown): string {
  const incoming = typeof value === "string" ? value.trim() : "";
  if (!incoming || PRISMA_LEGACY_LOCAL_IDS.terminalIds.has(incoming)) return PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId;
  return incoming;
}

export function prismaOriginalCustomerAccountSummary() {
  return {
    customerName: PRISMA_ORIGINAL_CUSTOMER.displayName,
    customerId: PRISMA_ORIGINAL_CUSTOMER.customerId,
    tenantId: PRISMA_ORIGINAL_CUSTOMER.tenantId,
    businessId: PRISMA_ORIGINAL_CUSTOMER.businessId,
    licenseId: PRISMA_ORIGINAL_CUSTOMER.licenseId,
    planLabel: PRISMA_ORIGINAL_CUSTOMER.planLabel,
    devices: {
      pc: PRISMA_ORIGINAL_CUSTOMER.pcDeviceId,
      tablet: PRISMA_ORIGINAL_CUSTOMER.tabletDeviceId,
      mobile: PRISMA_ORIGINAL_CUSTOMER.mobileDeviceId,
      terminal: PRISMA_ORIGINAL_CUSTOMER.tabletTerminalId
    }
  } as const;
}
