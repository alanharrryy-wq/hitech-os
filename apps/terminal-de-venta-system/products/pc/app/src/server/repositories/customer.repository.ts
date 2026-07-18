import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";

export type CustomerContactInput = {
  label: string;
  channel: "phone" | "email" | "other";
  value: string;
  isPrimary?: boolean;
};

export type CustomerFiscalProfileInput = {
  legalName: string;
  rfc?: string | null;
  taxRegime?: string | null;
  postalCode?: string | null;
  usageCode?: string | null;
  invoicingEmail?: string | null;
  isPrimary?: boolean;
};

export type CustomerWriteInput = {
  displayName: string;
  phone?: string | null;
  email?: string | null;
  segment?: string | null;
  isActive?: boolean;
  contacts?: CustomerContactInput[];
  fiscalProfile?: CustomerFiscalProfileInput | null;
  expectedVersion?: number | null;
};

type CustomerRow = {
  id: string;
  businessId: string;
  displayName: string;
  phone: string | null;
  email: string | null;
  fiscalDataJson: string | null;
  segment: string | null;
  creditCents: number;
  isActive: boolean | number;
  version: number;
  sourceSurface: string;
  tombstoneAt: Date | string | null;
  createdAt: Date | string;
  updatedAt: Date | string;
};

type ContactRow = {
  id: string;
  label: string;
  channel: "phone" | "email" | "other";
  value: string;
  isPrimary: boolean | number;
};

type FiscalProfileRow = {
  id: string;
  legalName: string;
  rfc: string | null;
  taxRegime: string | null;
  postalCode: string | null;
  usageCode: string | null;
  invoicingEmail: string | null;
  isPrimary: boolean | number;
  version: number;
};

type SegmentRow = {
  id: string;
  name: string;
  color: string | null;
};

type HistoryRow = {
  ticketCount: number | bigint;
  totalCents: number | bigint | null;
  lastSaleAt: Date | string | null;
};

export type CustomerRecord = {
  id: string;
  businessId: string;
  displayName: string;
  phone: string | null;
  email: string | null;
  segment: string | null;
  creditCents: number;
  isActive: boolean;
  version: number;
  sourceSurface: string;
  tombstoneAt: string | null;
  createdAt: string;
  updatedAt: string;
};

export type CustomerDetail = CustomerRecord & {
  contacts: ContactRow[];
  fiscalProfiles: FiscalProfileRow[];
  segments: SegmentRow[];
  history: {
    ticketCount: number;
    totalCents: number;
    lastSaleAt: string | null;
  };
};

export class CustomerDuplicateError extends Error {
  readonly duplicates: Array<Pick<CustomerRecord, "id" | "displayName" | "phone" | "email">>;

  constructor(duplicates: Array<Pick<CustomerRecord, "id" | "displayName" | "phone" | "email">>) {
    super("CUSTOMER_DUPLICATE");
    this.name = "CustomerDuplicateError";
    this.duplicates = duplicates;
  }
}

function asNumber(value: number | bigint | null | undefined) {
  return typeof value === "bigint" ? Number(value) : Number(value ?? 0);
}

function asIso(value: Date | string | null) {
  if (!value) return null;
  const date = value instanceof Date ? value : new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function toCustomerRecord(row: CustomerRow): CustomerRecord {
  return {
    id: row.id,
    businessId: row.businessId,
    displayName: row.displayName,
    phone: row.phone,
    email: row.email,
    segment: row.segment,
    creditCents: asNumber(row.creditCents),
    isActive: row.isActive === true || row.isActive === 1,
    version: asNumber(row.version),
    sourceSurface: row.sourceSurface,
    tombstoneAt: asIso(row.tombstoneAt),
    createdAt: asIso(row.createdAt) ?? new Date(0).toISOString(),
    updatedAt: asIso(row.updatedAt) ?? new Date(0).toISOString()
  };
}

function fiscalSnapshot(input: CustomerFiscalProfileInput | null | undefined) {
  if (!input) return null;
  return JSON.stringify({
    legalName: input.legalName,
    rfc: input.rfc ?? null,
    taxRegime: input.taxRegime ?? null,
    postalCode: input.postalCode ?? null,
    usageCode: input.usageCode ?? null,
    invoicingEmail: input.invoicingEmail ?? null
  });
}

export class CustomerRepository {
  private async findDuplicates(businessId: string, input: Pick<CustomerWriteInput, "displayName" | "phone" | "email">, excludeCustomerId?: string) {
    const rows = await prisma.$queryRaw<CustomerRow[]>`
      SELECT "id", "businessId", "displayName", "phone", "email", "fiscalDataJson", "segment", "creditCents", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt"
      FROM "Customer"
      WHERE "businessId" = ${businessId} AND "isActive" = true AND (${excludeCustomerId ?? ""} = '' OR "id" <> ${excludeCustomerId ?? ""})
        AND (
          LOWER("displayName") = LOWER(${input.displayName})
          OR (${input.phone ?? ""} <> '' AND "phone" = ${input.phone ?? ""})
          OR (${input.email ?? ""} <> '' AND LOWER(COALESCE("email", '')) = LOWER(${input.email ?? ""}))
        )
      ORDER BY "updatedAt" DESC
      LIMIT 8
    `;
    return rows.map((row) => {
      const customer = toCustomerRecord(row);
      return { id: customer.id, displayName: customer.displayName, phone: customer.phone, email: customer.email };
    });
  }

  private async recordAudit(tx: any, input: { businessId: string; topic: string; customer: Pick<CustomerRecord, "id" | "displayName" | "version" | "isActive">; before?: Record<string, unknown> | null; metadata?: Record<string, unknown> }) {
    await tx.auditEvent.create({
      data: {
        id: randomUUID(),
        businessId: input.businessId,
        actorId: null,
        topic: input.topic,
        entityType: "Customer",
        entityId: input.customer.id,
        summary: `Customer ${input.customer.displayName} ${input.topic}.`,
        beforeJson: input.before ? JSON.stringify(input.before) : null,
        afterJson: JSON.stringify({ id: input.customer.id, displayName: input.customer.displayName, version: input.customer.version, isActive: input.customer.isActive }),
        metadataJson: JSON.stringify({ source: "pc", privacy: "no_fiscal_or_credit", ...(input.metadata ?? {}) })
      }
    });
  }

  async list(input: { businessId: string; query?: string; includeInactive?: boolean; limit?: number }): Promise<CustomerRecord[]> {
    const businessId = input.businessId;
    const query = input.query?.trim().slice(0, 120) ?? "";
    const limit = Math.max(1, Math.min(Math.trunc(input.limit ?? 80), 200));
    const activeOnly = input.includeInactive !== true;
    const rows = query
      ? await prisma.$queryRaw<CustomerRow[]>`
          SELECT "id", "businessId", "displayName", "phone", "email", "fiscalDataJson", "segment", "creditCents", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt"
          FROM "Customer"
          WHERE "businessId" = ${businessId}
            AND (${activeOnly ? 0 : 1} = 1 OR "isActive" = true)
            AND ("displayName" LIKE ${`%${query}%`} OR "phone" LIKE ${`%${query}%`} OR "email" LIKE ${`%${query}%`})
          ORDER BY "displayName" ASC, "id" ASC
          LIMIT ${limit}
        `
      : await prisma.$queryRaw<CustomerRow[]>`
          SELECT "id", "businessId", "displayName", "phone", "email", "fiscalDataJson", "segment", "creditCents", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt"
          FROM "Customer"
          WHERE "businessId" = ${businessId}
            AND (${activeOnly ? 0 : 1} = 1 OR "isActive" = true)
          ORDER BY "displayName" ASC, "id" ASC
          LIMIT ${limit}
        `;

    return rows.map(toCustomerRecord);
  }

  async getById(businessId: string, customerId: string): Promise<CustomerDetail | null> {
    const [rows, contacts, fiscalProfiles, segments, history] = await Promise.all([
      prisma.$queryRaw<CustomerRow[]>`
        SELECT "id", "businessId", "displayName", "phone", "email", "fiscalDataJson", "segment", "creditCents", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt"
        FROM "Customer"
        WHERE "businessId" = ${businessId} AND "id" = ${customerId}
        LIMIT 1
      `,
      prisma.$queryRaw<ContactRow[]>`
        SELECT "id", "label", "channel", "value", "isPrimary"
        FROM "CustomerContact"
        WHERE "businessId" = ${businessId} AND "customerId" = ${customerId}
        ORDER BY "isPrimary" DESC, "label" ASC, "id" ASC
      `,
      prisma.$queryRaw<FiscalProfileRow[]>`
        SELECT "id", "legalName", "rfc", "taxRegime", "postalCode", "usageCode", "invoicingEmail", "isPrimary", "version"
        FROM "CustomerFiscalProfile"
        WHERE "businessId" = ${businessId} AND "customerId" = ${customerId}
        ORDER BY "isPrimary" DESC, "updatedAt" DESC, "id" ASC
      `,
      prisma.$queryRaw<SegmentRow[]>`
        SELECT "CustomerSegment"."id", "CustomerSegment"."name", "CustomerSegment"."color"
        FROM "CustomerSegmentMembership"
        INNER JOIN "CustomerSegment" ON "CustomerSegment"."id" = "CustomerSegmentMembership"."segmentId"
          AND "CustomerSegment"."businessId" = "CustomerSegmentMembership"."businessId"
        WHERE "CustomerSegmentMembership"."businessId" = ${businessId}
          AND "CustomerSegmentMembership"."customerId" = ${customerId}
        ORDER BY "CustomerSegment"."name" ASC
      `,
      prisma.$queryRaw<HistoryRow[]>`
        SELECT COUNT(*) AS "ticketCount", COALESCE(SUM("totalCents"), 0) AS "totalCents", MAX("createdAt") AS "lastSaleAt"
        FROM "Sale"
        WHERE "businessId" = ${businessId} AND "customerId" = ${customerId}
      `
    ]);

    const customer = rows[0];
    if (!customer) return null;
    const historyRow = history[0];
    return {
      ...toCustomerRecord(customer),
      contacts: contacts.map((contact) => ({ ...contact, isPrimary: contact.isPrimary === true || contact.isPrimary === 1 })),
      fiscalProfiles: fiscalProfiles.map((profile) => ({ ...profile, isPrimary: profile.isPrimary === true || profile.isPrimary === 1 })),
      segments,
      history: {
        ticketCount: asNumber(historyRow?.ticketCount),
        totalCents: asNumber(historyRow?.totalCents),
        lastSaleAt: asIso(historyRow?.lastSaleAt ?? null)
      }
    };
  }

  async create(businessId: string, input: CustomerWriteInput): Promise<CustomerDetail> {
    const customerId = randomUUID();
    const now = new Date();
    const contacts = input.contacts ?? [];
    const fiscalDataJson = fiscalSnapshot(input.fiscalProfile);
    const duplicates = await this.findDuplicates(businessId, input);
    if (duplicates.length) throw new CustomerDuplicateError(duplicates);

    await prisma.$transaction(async (tx: any) => {
      await tx.$executeRaw`
        INSERT INTO "Customer" ("id", "businessId", "displayName", "phone", "email", "fiscalDataJson", "segment", "creditCents", "isActive", "version", "sourceSurface", "tombstoneAt", "createdAt", "updatedAt")
        VALUES (${customerId}, ${businessId}, ${input.displayName}, ${input.phone ?? null}, ${input.email ?? null}, ${fiscalDataJson}, ${input.segment ?? null}, 0, ${input.isActive !== false}, 1, 'pc', ${input.isActive === false ? now : null}, ${now}, ${now})
      `;

      for (const contact of contacts) {
        await tx.$executeRaw`
          INSERT INTO "CustomerContact" ("id", "businessId", "customerId", "label", "channel", "value", "isPrimary", "createdAt", "updatedAt")
          VALUES (${randomUUID()}, ${businessId}, ${customerId}, ${contact.label}, ${contact.channel}, ${contact.value}, ${contact.isPrimary === true}, ${now}, ${now})
        `;
      }

      if (input.fiscalProfile) {
        const fiscal = input.fiscalProfile;
        await tx.$executeRaw`
          INSERT INTO "CustomerFiscalProfile" ("id", "businessId", "customerId", "legalName", "rfc", "taxRegime", "postalCode", "usageCode", "invoicingEmail", "isPrimary", "version", "createdAt", "updatedAt")
          VALUES (${randomUUID()}, ${businessId}, ${customerId}, ${fiscal.legalName}, ${fiscal.rfc ?? null}, ${fiscal.taxRegime ?? null}, ${fiscal.postalCode ?? null}, ${fiscal.usageCode ?? null}, ${fiscal.invoicingEmail ?? null}, ${fiscal.isPrimary !== false}, 1, ${now}, ${now})
        `;
      }

      await this.recordAudit(tx, {
        businessId,
        topic: "customer.created",
        customer: { id: customerId, displayName: input.displayName, version: 1, isActive: input.isActive !== false },
        metadata: { contactCount: contacts.length, fiscalProfileProvided: Boolean(input.fiscalProfile) }
      });
    });

    const created = await this.getById(businessId, customerId);
    if (!created) throw new Error("CUSTOMER_CREATE_NOT_VISIBLE");
    return created;
  }

  async update(businessId: string, customerId: string, input: CustomerWriteInput): Promise<CustomerDetail | null> {
    const current = await this.getById(businessId, customerId);
    if (!current) return null;
    if (input.expectedVersion !== null && input.expectedVersion !== undefined && input.expectedVersion !== current.version) {
      throw new Error("CUSTOMER_VERSION_CONFLICT");
    }

    const now = new Date();
    const next = {
      displayName: input.displayName || current.displayName,
      phone: input.phone === undefined ? current.phone : input.phone,
      email: input.email === undefined ? current.email : input.email,
      segment: input.segment === undefined ? current.segment : input.segment,
      isActive: input.isActive === undefined ? current.isActive : input.isActive,
      fiscalDataJson: input.fiscalProfile === undefined ? null : fiscalSnapshot(input.fiscalProfile)
    };
    const duplicates = await this.findDuplicates(businessId, next, customerId);
    if (duplicates.length) throw new CustomerDuplicateError(duplicates);

    await prisma.$transaction(async (tx: any) => {
      await tx.$executeRaw`
        UPDATE "Customer"
        SET "displayName" = ${next.displayName}, "phone" = ${next.phone}, "email" = ${next.email}, "segment" = ${next.segment},
          "isActive" = ${next.isActive}, "fiscalDataJson" = COALESCE(${next.fiscalDataJson}, "fiscalDataJson"), "tombstoneAt" = ${next.isActive ? null : now},
          "version" = "version" + 1, "updatedAt" = ${now}
        WHERE "businessId" = ${businessId} AND "id" = ${customerId}
      `;

      if (input.fiscalProfile) {
        const fiscal = input.fiscalProfile;
        await tx.$executeRaw`
          UPDATE "CustomerFiscalProfile"
          SET "isPrimary" = false, "updatedAt" = ${now}
          WHERE "businessId" = ${businessId} AND "customerId" = ${customerId} AND "isPrimary" = true
        `;
        await tx.$executeRaw`
          INSERT INTO "CustomerFiscalProfile" ("id", "businessId", "customerId", "legalName", "rfc", "taxRegime", "postalCode", "usageCode", "invoicingEmail", "isPrimary", "version", "createdAt", "updatedAt")
          VALUES (${randomUUID()}, ${businessId}, ${customerId}, ${fiscal.legalName}, ${fiscal.rfc ?? null}, ${fiscal.taxRegime ?? null}, ${fiscal.postalCode ?? null}, ${fiscal.usageCode ?? null}, ${fiscal.invoicingEmail ?? null}, true, 1, ${now}, ${now})
        `;
      }

      await this.recordAudit(tx, {
        businessId,
        topic: next.isActive ? "customer.updated" : "customer.deactivated",
        customer: { id: customerId, displayName: next.displayName, version: current.version + 1, isActive: next.isActive },
        before: { id: current.id, displayName: current.displayName, version: current.version, isActive: current.isActive },
        metadata: { fiscalProfileProvided: Boolean(input.fiscalProfile) }
      });
    });

    return this.getById(businessId, customerId);
  }

  async attachSale(businessId: string, customerId: string, saleId: string): Promise<boolean> {
    const customer = await this.getById(businessId, customerId);
    return prisma.$transaction(async (tx: any) => {
      const changed = await tx.$executeRaw`
        UPDATE "Sale"
        SET "customerId" = ${customerId}
        WHERE "businessId" = ${businessId} AND "id" = ${saleId}
          AND ("customerId" IS NULL OR "customerId" = ${customerId})
      `;
      if (Number(changed) <= 0) return false;
      if (customer) {
        await this.recordAudit(tx, {
          businessId,
          topic: "customer.sale_attached",
          customer,
          metadata: { saleId }
        });
      }
      return true;
    });
  }
}
