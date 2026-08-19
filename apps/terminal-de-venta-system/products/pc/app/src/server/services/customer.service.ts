import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";
import {
  CustomerRepository,
  type CustomerDetail,
  type CustomerWriteInput
} from "@/server/repositories/customer.repository";

const repository = new CustomerRepository();

export type CustomerWorkspace = {
  customers: Awaited<ReturnType<CustomerRepository["list"]>>;
  meta: {
    source: "canonical_prisma" | "unavailable";
    generatedAt: string;
    warnings: string[];
  };
};

function stringValue(value: unknown, max: number) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function nullableValue(value: unknown, max: number) {
  const normalized = stringValue(value, max);
  return normalized || null;
}

function boolValue(value: unknown) {
  return value === true || value === "true" || value === 1 || value === "1";
}

function optionalBoolean(value: unknown) {
  if (value === undefined || value === null || value === "") return undefined;
  return boolValue(value);
}

function readContacts(value: unknown) {
  if (!Array.isArray(value)) return [];
  const unique = new Set<string>();
  return value.slice(0, 6).flatMap((item) => {
    const raw = item as Record<string, unknown>;
    const channel = stringValue(raw.channel, 16).toLowerCase();
    const value = stringValue(raw.value, 180);
    const label = stringValue(raw.label, 48) || (channel === "email" ? "Correo" : channel === "phone" ? "Teléfono" : "Contacto");
    if (!value || (channel !== "phone" && channel !== "email" && channel !== "other")) return [];
    const key = `${channel}:${value.toLocaleLowerCase()}`;
    if (unique.has(key)) return [];
    unique.add(key);
    return [{ label, channel: channel as "phone" | "email" | "other", value, isPrimary: raw.isPrimary === true }];
  });
}

function readFiscalProfile(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return undefined;
  const raw = value as Record<string, unknown>;
  const legalName = stringValue(raw.legalName, 180);
  if (!legalName) return null;
  return {
    legalName,
    rfc: nullableValue(raw.rfc, 20),
    taxRegime: nullableValue(raw.taxRegime, 40),
    postalCode: nullableValue(raw.postalCode, 12),
    usageCode: nullableValue(raw.usageCode, 16),
    invoicingEmail: nullableValue(raw.invoicingEmail, 160),
    isPrimary: raw.isPrimary !== false
  };
}

export function readCustomerWriteInput(body: unknown, options: { partial?: boolean } = {}): CustomerWriteInput {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const displayName = stringValue(raw.displayName, 140);
  if (!options.partial && displayName.length < 2) throw new Error("CUSTOMER_NAME_REQUIRED");
  if (displayName && displayName.length < 2) throw new Error("CUSTOMER_NAME_REQUIRED");

  const email = raw.email === undefined ? undefined : nullableValue(raw.email, 160);
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) throw new Error("CUSTOMER_EMAIL_INVALID");
  const fiscalProfile = raw.fiscalProfile === undefined ? undefined : readFiscalProfile(raw.fiscalProfile);

  return {
    displayName,
    phone: raw.phone === undefined ? undefined : nullableValue(raw.phone, 40),
    email,
    segment: raw.segment === undefined ? undefined : nullableValue(raw.segment, 80),
    isActive: optionalBoolean(raw.isActive),
    contacts: raw.contacts === undefined ? undefined : readContacts(raw.contacts),
    fiscalProfile,
    expectedVersion: Number.isInteger(raw.expectedVersion) && Number(raw.expectedVersion) > 0 ? Number(raw.expectedVersion) : null
  };
}

export async function getCustomerWorkspace(input: { query?: string; includeInactive?: boolean; limit?: number } = {}): Promise<CustomerWorkspace> {
  try {
    const businessId = await resolvePcBusinessScope();
    const customers = await repository.list({ businessId, ...input });
    return {
      customers,
      meta: { source: "canonical_prisma", generatedAt: new Date().toISOString(), warnings: [] }
    };
  } catch {
    return {
      customers: [],
      meta: {
        source: "unavailable",
        generatedAt: new Date().toISOString(),
        warnings: ["No pudimos cargar Clientes en este momento. Intenta de nuevo. Si el problema continúa, contacta a soporte."]
      }
    };
  }
}

export async function getCustomerDetail(customerId: string): Promise<CustomerDetail | null> {
  const businessId = await resolvePcBusinessScope();
  return repository.getById(businessId, customerId);
}

export async function createCustomer(input: CustomerWriteInput) {
  const businessId = await resolvePcBusinessScope();
  return repository.create(businessId, input);
}

export async function updateCustomer(customerId: string, input: CustomerWriteInput) {
  const businessId = await resolvePcBusinessScope();
  return repository.update(businessId, customerId, input);
}

export async function attachCustomerToSale(customerId: string, saleId: string) {
  const businessId = await resolvePcBusinessScope();
  const customer = await repository.getById(businessId, customerId);
  if (!customer) throw new Error("CUSTOMER_NOT_FOUND");
  const attached = await repository.attachSale(businessId, customerId, saleId);
  if (!attached) throw new Error("SALE_NOT_FOUND_OR_ALREADY_ASSIGNED");
  return { customer, saleId };
}
