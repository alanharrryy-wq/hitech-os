import { randomUUID } from "node:crypto";
import { prisma } from "@/server/prisma/client";
import { resolvePcBusinessScope } from "@/server/services/pc-command-center.service";

type Product = { id: string; sku: string; name: string; isActive: boolean };
type GroupRow = { id: string; name: string; minSelections: number; maxSelections: number; status: "ACTIVE" | "INACTIVE"; sortOrder: number; version: number; updatedAt: Date | string };
type OptionRow = { id: string; modifierGroupId: string; name: string; priceDeltaCents: number; isDefault: number | boolean; status: "ACTIVE" | "INACTIVE"; sortOrder: number; version: number };
type LinkRow = { id: string; productId: string; modifierGroupId: string; required: number | boolean; status: "ACTIVE" | "INACTIVE"; sortOrder: number; version: number };

function text(value: unknown, max = 160) {
  return typeof value === "string" ? value.trim().slice(0, max) : "";
}

function integer(value: unknown, fallback = 0) {
  const parsed = Number(value);
  return Number.isInteger(parsed) ? parsed : fallback;
}

function bool(value: unknown) {
  return value === true || value === "true" || value === 1 || value === "1";
}

function iso(value: Date | string) {
  const parsed = value instanceof Date ? value : new Date(value);
  return Number.isNaN(parsed.getTime()) ? new Date(0).toISOString() : parsed.toISOString();
}

export type ModifierCatalogWorkspace = {
  groups: Array<GroupRow & { updatedAt: string; options: OptionRow[]; products: Array<LinkRow & { sku: string; productName: string }> }>;
  products: Product[];
  meta: { source: "canonical_prisma" | "unavailable"; warning: string | null; generatedAt: string };
};

async function listWorkspace(businessId: string): Promise<ModifierCatalogWorkspace> {
  const [products, groups, options, links] = await Promise.all([
    prisma.$queryRaw<Product[]>`SELECT "id", "sku", "name", "isActive" FROM "Product" WHERE "businessId" = ${businessId} AND "isActive" = true ORDER BY "name", "sku" LIMIT 300`,
    prisma.$queryRaw<GroupRow[]>`SELECT "id", "name", "minSelections", "maxSelections", "status", "sortOrder", "version", "updatedAt" FROM "ModifierGroup" WHERE "businessId" = ${businessId} ORDER BY "sortOrder", "name"`,
    prisma.$queryRaw<OptionRow[]>`SELECT "id", "modifierGroupId", "name", "priceDeltaCents", "isDefault", "status", "sortOrder", "version" FROM "ModifierOption" WHERE "businessId" = ${businessId} ORDER BY "sortOrder", "name"`,
    prisma.$queryRaw<Array<LinkRow & { sku: string; productName: string }>>`SELECT l."id", l."productId", l."modifierGroupId", l."required", l."status", l."sortOrder", l."version", p."sku", p."name" AS "productName" FROM "ProductModifierGroup" l JOIN "Product" p ON p."id" = l."productId" AND p."businessId" = l."businessId" WHERE l."businessId" = ${businessId} ORDER BY l."sortOrder", p."sku"`
  ]);
  return {
    groups: groups.map((group) => ({ ...group, updatedAt: iso(group.updatedAt), options: options.filter((option) => option.modifierGroupId === group.id), products: links.filter((link) => link.modifierGroupId === group.id) })),
    products,
    meta: { source: "canonical_prisma", warning: null, generatedAt: new Date().toISOString() }
  };
}

export async function getModifierCatalogWorkspace(): Promise<ModifierCatalogWorkspace> {
  try {
    return await listWorkspace(await resolvePcBusinessScope());
  } catch (error) {
    return { groups: [], products: [], meta: { source: "unavailable", warning: `No se pudo leer modificadores: ${error instanceof Error ? error.message : "migración pendiente"}`, generatedAt: new Date().toISOString() } };
  }
}

async function auditAndOutbox(tx: any, businessId: string, topic: string, entityType: string, entityId: string, payload: Record<string, unknown>) {
  const now = new Date();
  await tx.auditEvent.create({ data: { id: randomUUID(), businessId, actorId: null, topic, entityType, entityId, summary: `Configuración de modificador: ${topic}.`, afterJson: JSON.stringify(payload), metadataJson: JSON.stringify({ source: "pc", privacy: "catalog_configuration" }), createdAt: now } });
  await tx.outboxEvent.create({ data: { id: randomUUID(), businessId, topic, eventType: topic, aggregateId: entityId, idempotencyKey: `${topic}:${entityId}`, payloadJson: JSON.stringify({ businessId, entityId, occurredAt: now.toISOString() }), source: "pc", schemaVersion: "product-modifiers.v1", status: "pending", lifecycleStatus: "pending", attempts: 0, createdAt: now } });
}

export function readModifierCatalogCommand(body: unknown) {
  const raw = body && typeof body === "object" && !Array.isArray(body) ? body as Record<string, unknown> : {};
  const action = text(raw.action, 40);
  const idempotencyKey = text(raw.idempotencyKey, 160);
  if (!idempotencyKey) throw new Error("MODIFIER_IDEMPOTENCY_REQUIRED");
  if (action === "createGroup") {
    const name = text(raw.name);
    const minSelections = Math.max(0, integer(raw.minSelections));
    const maxSelections = Math.max(1, integer(raw.maxSelections, 1));
    if (name.length < 2 || maxSelections < minSelections) throw new Error("MODIFIER_GROUP_INVALID");
    return { action, name, minSelections, maxSelections, sortOrder: Math.max(0, integer(raw.sortOrder)), idempotencyKey } as const;
  }
  if (action === "createOption") {
    const modifierGroupId = text(raw.modifierGroupId);
    const name = text(raw.name);
    if (!modifierGroupId || name.length < 1) throw new Error("MODIFIER_OPTION_INVALID");
    return { action, modifierGroupId, name, priceDeltaCents: integer(raw.priceDeltaCents), isDefault: bool(raw.isDefault), sortOrder: Math.max(0, integer(raw.sortOrder)), idempotencyKey } as const;
  }
  if (action === "linkProduct") {
    const modifierGroupId = text(raw.modifierGroupId);
    const productId = text(raw.productId);
    if (!modifierGroupId || !productId) throw new Error("PRODUCT_MODIFIER_LINK_INVALID");
    return { action, modifierGroupId, productId, required: bool(raw.required), sortOrder: Math.max(0, integer(raw.sortOrder)), idempotencyKey } as const;
  }
  throw new Error("MODIFIER_ACTION_INVALID");
}

export async function executeModifierCatalogCommand(command: ReturnType<typeof readModifierCatalogCommand>) {
  const businessId = await resolvePcBusinessScope();
  const result = await prisma.$transaction(async (tx: any) => {
    const now = new Date();
    if (command.action === "createGroup") {
      const replay = await tx.$queryRaw`SELECT "id" FROM "ModifierGroup" WHERE "businessId" = ${businessId} AND "idempotencyKey" = ${command.idempotencyKey} LIMIT 1` as Array<{ id: string }>;
      const id = replay[0]?.id ?? randomUUID();
      if (!replay[0]) {
        await tx.$executeRaw`INSERT INTO "ModifierGroup" ("id", "businessId", "name", "minSelections", "maxSelections", "status", "sortOrder", "idempotencyKey", "version", "createdAt", "updatedAt") VALUES (${id}, ${businessId}, ${command.name}, ${command.minSelections}, ${command.maxSelections}, 'ACTIVE', ${command.sortOrder}, ${command.idempotencyKey}, 1, ${now}, ${now})`;
        await auditAndOutbox(tx, businessId, "product.modifier_group.created", "ModifierGroup", id, command);
      }
      return { id, replayed: Boolean(replay[0]) };
    }
    if (command.action === "createOption") {
      const groups = await tx.$queryRaw`SELECT "id" FROM "ModifierGroup" WHERE "businessId" = ${businessId} AND "id" = ${command.modifierGroupId} AND "status" = 'ACTIVE' LIMIT 1` as Array<{ id: string }>;
      if (!groups[0]) throw new Error("MODIFIER_GROUP_NOT_FOUND");
      const replay = await tx.$queryRaw`SELECT "id" FROM "ModifierOption" WHERE "businessId" = ${businessId} AND "idempotencyKey" = ${command.idempotencyKey} LIMIT 1` as Array<{ id: string }>;
      const id = replay[0]?.id ?? randomUUID();
      if (!replay[0]) {
        await tx.$executeRaw`INSERT INTO "ModifierOption" ("id", "businessId", "modifierGroupId", "name", "priceDeltaCents", "isDefault", "status", "sortOrder", "idempotencyKey", "version", "createdAt", "updatedAt") VALUES (${id}, ${businessId}, ${command.modifierGroupId}, ${command.name}, ${command.priceDeltaCents}, ${command.isDefault}, 'ACTIVE', ${command.sortOrder}, ${command.idempotencyKey}, 1, ${now}, ${now})`;
        await auditAndOutbox(tx, businessId, "product.modifier_option.created", "ModifierOption", id, command);
      }
      return { id, replayed: Boolean(replay[0]) };
    }
    const [products, groups] = await Promise.all([
      tx.product.findFirst({ where: { id: command.productId, businessId, isActive: true }, select: { id: true } }),
      tx.$queryRaw`SELECT "id" FROM "ModifierGroup" WHERE "businessId" = ${businessId} AND "id" = ${command.modifierGroupId} AND "status" = 'ACTIVE' LIMIT 1` as Promise<Array<{ id: string }>>
    ]);
    if (!products) throw new Error("PRODUCT_MODIFIER_PRODUCT_NOT_FOUND");
    if (!groups[0]) throw new Error("MODIFIER_GROUP_NOT_FOUND");
    const replay = await tx.$queryRaw`SELECT "id" FROM "ProductModifierGroup" WHERE "businessId" = ${businessId} AND "idempotencyKey" = ${command.idempotencyKey} LIMIT 1` as Array<{ id: string }>;
    const id = replay[0]?.id ?? randomUUID();
    if (!replay[0]) {
      await tx.$executeRaw`INSERT INTO "ProductModifierGroup" ("id", "businessId", "productId", "modifierGroupId", "required", "sortOrder", "status", "idempotencyKey", "version", "createdAt", "updatedAt") VALUES (${id}, ${businessId}, ${command.productId}, ${command.modifierGroupId}, ${command.required}, ${command.sortOrder}, 'ACTIVE', ${command.idempotencyKey}, 1, ${now}, ${now})`;
      await auditAndOutbox(tx, businessId, "product.modifier_group.linked", "ProductModifierGroup", id, command);
    }
    return { id, replayed: Boolean(replay[0]) };
  });
  const workspace = await getModifierCatalogWorkspace();
  return { ...result, workspace };
}
