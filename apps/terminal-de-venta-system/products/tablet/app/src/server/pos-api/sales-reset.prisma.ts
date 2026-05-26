import { createHash, randomBytes, randomUUID } from "node:crypto";
import { prisma } from "../prisma/client";
import { DEFAULT_POS_API_BUSINESS_ID } from "./validators";

const SALE_OUTBOX_TOPICS = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "sale.return.created",
  "sale.refunded",
  "cash.session.opened",
  "cash.movement.recorded",
  "shift.opened",
  "shift.closed"
];

const SECURITY_TABLE = "TabletLocalSecuritySecret";
const ADMIN_PIN_KEY = "admin_pin";
const RESET_ANSWER_KEY = "reset_security_answer";
const SUPPORT_CONTACT = {
  phone: "56 2956 3031",
  email: "contacto@hitechrts.com"
};

export const RESET_SECURITY_QUESTIONS = [
  { id: "owner_keyword", label: "Palabra clave del propietario" },
  { id: "support_keyword", label: "Palabra acordada con soporte" },
  { id: "store_keyword", label: "Palabra privada de la tienda" }
] as const;

type SecurityQuestionId = (typeof RESET_SECURITY_QUESTIONS)[number]["id"];

export type SalesResetPreview = {
  businessId: string;
  scope: "sales_cash_outbox";
  counts: Record<string, number>;
  preserves: string[];
  securityQuestions: typeof RESET_SECURITY_QUESTIONS;
  security: {
    configured: boolean;
    configuredQuestionId: SecurityQuestionId | null;
    requiresInitialSetup: boolean;
    supportContact: typeof SUPPORT_CONTACT;
  };
  generatedAt: string;
};

type SecretRow = {
  businessId: string;
  secretKey: string;
  secretHash: string;
  salt: string;
  metadataJson: string | null;
  updatedAt: string;
};

function normalizeAnswer(value: string) {
  return value.trim().toLocaleLowerCase("es-MX");
}

function normalizePin(value: string) {
  return value.trim();
}

function assertOneWordAnswer(value: string) {
  const normalized = normalizeAnswer(value);
  if (!normalized || /\s/.test(normalized) || normalized.length < 2 || normalized.length > 48) {
    throw new Error("RESET_SECURITY_ANSWER_INVALID_FORMAT");
  }
  return normalized;
}

function assertSixDigitPin(value: string) {
  const normalized = normalizePin(value);
  if (!/^\d{6}$/.test(normalized)) throw new Error("RESET_ADMIN_PIN_INVALID_FORMAT");
  return normalized;
}

function assertQuestionId(value: string): SecurityQuestionId {
  const found = RESET_SECURITY_QUESTIONS.find((question) => question.id === value);
  if (!found) throw new Error("RESET_SECURITY_QUESTION_INVALID");
  return found.id;
}

function secretHash(input: { businessId: string; key: string; value: string; salt: string }) {
  return createHash("sha256")
    .update(`${input.businessId}:${input.key}:${input.salt}:${input.value}`)
    .digest("hex");
}

async function ensureSecurityTable(db: any = prisma) {
  await db.$executeRawUnsafe(`
    CREATE TABLE IF NOT EXISTS "${SECURITY_TABLE}" (
      "businessId" TEXT NOT NULL,
      "secretKey" TEXT NOT NULL,
      "secretHash" TEXT NOT NULL,
      "salt" TEXT NOT NULL,
      "metadataJson" TEXT,
      "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY ("businessId", "secretKey")
    )
  `);
}

async function ensureBusiness(tx: any, businessId: string) {
  await tx.business.upsert({
    where: { id: businessId },
    update: {},
    create: { id: businessId, name: "PRISMA Tablet Local", taxId: null, currency: "MXN" }
  });
}

async function readSecret(businessId: string, key: string): Promise<SecretRow | null> {
  await ensureSecurityTable();
  const rows = await (prisma as any).$queryRawUnsafe(
    `SELECT "businessId", "secretKey", "secretHash", "salt", "metadataJson", "updatedAt"
     FROM "${SECURITY_TABLE}"
     WHERE "businessId" = ? AND "secretKey" = ?
     LIMIT 1`,
    businessId,
    key
  );
  return Array.isArray(rows) && rows.length ? rows[0] as SecretRow : null;
}

function readQuestionFromSecret(row: SecretRow | null): SecurityQuestionId | null {
  if (!row?.metadataJson) return null;
  try {
    const parsed = JSON.parse(row.metadataJson) as { questionId?: string };
    return parsed.questionId ? assertQuestionId(parsed.questionId) : null;
  } catch {
    return null;
  }
}

async function writeSecret(tx: any, input: { businessId: string; key: string; value: string; metadata?: Record<string, unknown> }) {
  const salt = randomBytes(16).toString("hex");
  const hash = secretHash({ businessId: input.businessId, key: input.key, value: input.value, salt });
  await tx.$executeRawUnsafe(
    `INSERT INTO "${SECURITY_TABLE}" ("businessId", "secretKey", "secretHash", "salt", "metadataJson", "updatedAt")
     VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
     ON CONFLICT("businessId", "secretKey") DO UPDATE SET
       "secretHash" = excluded."secretHash",
       "salt" = excluded."salt",
       "metadataJson" = excluded."metadataJson",
       "updatedAt" = CURRENT_TIMESTAMP`,
    input.businessId,
    input.key,
    hash,
    salt,
    input.metadata ? JSON.stringify(input.metadata) : null
  );
}

async function verifySecret(input: { businessId: string; key: string; value: string }) {
  const row = await readSecret(input.businessId, input.key);
  if (!row) throw new Error("RESET_SECURITY_NOT_CONFIGURED");
  const hash = secretHash({ businessId: input.businessId, key: input.key, value: input.value, salt: row.salt });
  return hash === row.secretHash;
}

async function countsForBusiness(businessId: string): Promise<Record<string, number>> {
  const db = prisma as any;
  const count = async (delegateName: string, where: Record<string, unknown>) => {
    const delegate = db[delegateName];
    if (!delegate?.count) return 0;
    return delegate.count({ where }).catch(() => 0);
  };
  const [sales, saleLines, tenders, returns, returnLines, cashSessions, cashMovements, cashAdjustments, saleOutboxEvents, saleStockMovements] = await Promise.all([
    count("sale", { businessId }),
    count("saleLine", { businessId }),
    count("salePaymentTender", { businessId }),
    count("saleReturn", { businessId }),
    count("saleReturnLine", { businessId }),
    count("cashSession", { businessId }),
    count("cashMovement", { businessId }),
    count("cashAdjustment", { businessId }),
    count("outboxEvent", { businessId, topic: { in: SALE_OUTBOX_TOPICS } }),
    count("stockMovement", { businessId, sourceType: "sale" })
  ]);

  return { sales, saleLines, tenders, returns, returnLines, cashSessions, cashMovements, cashAdjustments, saleOutboxEvents, saleStockMovements };
}

export async function previewSalesReset(businessId = DEFAULT_POS_API_BUSINESS_ID): Promise<SalesResetPreview> {
  const [pinSecret, answerSecret] = await Promise.all([
    readSecret(businessId, ADMIN_PIN_KEY),
    readSecret(businessId, RESET_ANSWER_KEY)
  ]);
  const configuredQuestionId = readQuestionFromSecret(answerSecret);
  const configured = Boolean(pinSecret && answerSecret && configuredQuestionId);
  return {
    businessId,
    scope: "sales_cash_outbox",
    counts: await countsForBusiness(businessId),
    preserves: [
      "licencia local y configuración de runtime",
      "catálogo local",
      "existencias y movimientos de inventario",
      "usuarios, roles y permisos",
      "eventos de auditoría de reset"
    ],
    securityQuestions: RESET_SECURITY_QUESTIONS,
    security: {
      configured,
      configuredQuestionId,
      requiresInitialSetup: !configured,
      supportContact: SUPPORT_CONTACT
    },
    generatedAt: new Date().toISOString()
  };
}

export async function configureSalesResetSecurity(input: {
  businessId?: string;
  questionId: string;
  securityAnswer: string;
  adminPin: string;
  operatorNote?: string | null;
}) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  const questionId = assertQuestionId(input.questionId);
  const securityAnswer = assertOneWordAnswer(input.securityAnswer);
  const adminPin = assertSixDigitPin(input.adminPin);
  await ensureSecurityTable();
  const configuredAt = new Date().toISOString();
  await (prisma as any).$transaction(async (tx: any) => {
    await ensureSecurityTable(tx);
    await ensureBusiness(tx, businessId);
    await writeSecret(tx, { businessId, key: ADMIN_PIN_KEY, value: adminPin, metadata: { type: "admin_pin", configuredAt } });
    await writeSecret(tx, {
      businessId,
      key: RESET_ANSWER_KEY,
      value: securityAnswer,
      metadata: { type: "security_question", questionId, configuredAt }
    });
    await tx.auditEvent.create({
      data: {
        id: `sales_reset_security_${randomUUID()}`,
        businessId,
        actorId: null,
        topic: "tablet.sales.reset.security.configured",
        entityType: "tablet_sales_db",
        entityId: businessId,
        summary: "Seguridad local de reset configurada con PIN admin y pregunta de seguridad.",
        beforeJson: null,
        afterJson: JSON.stringify({ questionId, configured: true }),
        metadataJson: JSON.stringify({
          operatorNote: input.operatorNote ?? null,
          supportContact: SUPPORT_CONTACT,
          secretsStoredAsHashes: true
        })
      }
    });
  });
  return { businessId, configured: true, questionId, configuredAt };
}

export async function performSalesReset(input: {
  businessId?: string;
  questionId: string;
  securityAnswer: string;
  adminPin: string;
  operatorNote?: string | null;
}) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  const questionId = assertQuestionId(input.questionId);
  const securityAnswer = assertOneWordAnswer(input.securityAnswer);
  const adminPin = assertSixDigitPin(input.adminPin);
  const answerSecret = await readSecret(businessId, RESET_ANSWER_KEY);
  const configuredQuestionId = readQuestionFromSecret(answerSecret);
  if (!configuredQuestionId) throw new Error("RESET_SECURITY_NOT_CONFIGURED");
  if (configuredQuestionId !== questionId) throw new Error("RESET_SECURITY_QUESTION_MISMATCH");
  if (!await verifySecret({ businessId, key: ADMIN_PIN_KEY, value: adminPin })) throw new Error("RESET_ADMIN_PIN_INVALID");
  if (!await verifySecret({ businessId, key: RESET_ANSWER_KEY, value: securityAnswer })) throw new Error("RESET_SECURITY_ANSWER_INVALID");

  const before = await countsForBusiness(businessId);
  const db = prisma as any;
  const deleteMany = async (tx: any, delegateName: string, where: Record<string, unknown>) => {
    const delegate = tx[delegateName];
    if (!delegate?.deleteMany) return { count: 0, skipped: true };
    return delegate.deleteMany({ where }).catch(() => ({ count: 0, skipped: true }));
  };
  const resetId = `sales_reset_${randomUUID()}`;
  const result = await db.$transaction(async (tx: any) => {
    await ensureSecurityTable(tx);
    await ensureBusiness(tx, businessId);
    await deleteMany(tx, "saleReturnLine", { businessId });
    await deleteMany(tx, "saleReturn", { businessId });
    await deleteMany(tx, "salePaymentTender", { businessId });
    await deleteMany(tx, "saleLine", { businessId });
    await deleteMany(tx, "cashAdjustment", { businessId });
    await deleteMany(tx, "cashMovement", { businessId });
    await deleteMany(tx, "sale", { businessId });
    await deleteMany(tx, "cashSession", { businessId });
    await deleteMany(tx, "outboxEvent", { businessId, topic: { in: SALE_OUTBOX_TOPICS } });
    await tx.auditEvent.create({
      data: {
        id: resetId,
        businessId,
        actorId: null,
        topic: "tablet.sales.reset",
        entityType: "tablet_sales_db",
        entityId: businessId,
        summary: "Reset seguro de ventas/caja/outbox de Tablet ejecutado con PIN admin y pregunta de seguridad.",
        beforeJson: JSON.stringify(before),
        afterJson: null,
        metadataJson: JSON.stringify({
          operatorNote: input.operatorNote ?? null,
          securityQuestionId: questionId,
          preserved: ["license", "runtime_config", "catalog", "inventory", "users", "roles"],
          stockMovementsPreserved: true
        })
      }
    });
    await tx.supportIncident.create({
      data: {
        id: `support_reset_${randomUUID()}`,
        businessId,
        openedById: null,
        assignedToId: null,
        title: "Alerta silenciosa de soporte: reset seguro ejecutado",
        status: "queued",
        severity: "high",
        source: "local_support_outbox",
        description: "Alerta local lista para enviarse a soporte cuando la Tablet tenga sincronización disponible.",
        evidenceJson: JSON.stringify({
          resetId,
          supportContact: SUPPORT_CONTACT,
          before,
          operatorNotePresent: Boolean(input.operatorNote),
          preserved: ["license", "runtime_config", "catalog", "inventory", "users", "roles"],
          secretsIncluded: false
        })
      }
    });
    return { resetId };
  });
  const after = await countsForBusiness(businessId);
  return { ...result, businessId, before, after, preservesLicenseConfig: true, preservesCatalogAndInventory: true };
}
