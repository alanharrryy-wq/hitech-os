import { createHash, randomBytes, randomUUID } from "node:crypto";
import { prisma } from "../prisma/client";
import { DEFAULT_POS_API_BUSINESS_ID } from "./validators";

const DEFAULT_PERMISSIONS = [
  "sell:create",
  "ticket:view",
  "ticket:void",
  "ticket:return",
  "cash:open",
  "cash:close",
  "cash:adjust",
  "inventory:view",
  "inventory:update",
  "inventory:adjust",
  "catalog:create",
  "catalog:update",
  "supplier:view",
  "supplier:create",
  "supplier:update",
  "sync:send",
  "sync:configure",
  "users:create",
  "users:update",
  "users:permissions",
  "data:reset",
  "license:view",
  "license:update",
  "support:evidence"
] as const;

const ROLE_DEFINITIONS = [
  {
    code: "admin_owner",
    label: "Admin / Owner",
    description: "Control operativo completo de usuarios, caja, inventario, configuración, licencias y reset seguro.",
    permissions: [...DEFAULT_PERMISSIONS]
  },
  {
    code: "cashier",
    label: "Cashier",
    description: "Venta local, catálogo, tickets propios y caja solo cuando el permiso esté activo.",
    permissions: ["sell:create", "ticket:view", "cash:open", "cash:close", "inventory:view", "license:view"]
  },
  {
    code: "supervisor",
    label: "Supervisor",
    description: "Revisión operativa, reportes, pendientes, sincronización, devoluciones y ajustes permitidos.",
    permissions: [
      "ticket:view",
      "ticket:return",
      "cash:close",
      "cash:adjust",
      "inventory:view",
      "inventory:update",
      "inventory:adjust",
      "supplier:view",
      "sync:send",
      "support:evidence"
    ]
  },
  {
    code: "support_internal",
    label: "Support",
    description: "Rol técnico interno oculto de la lista operativa normal; no expone secretos.",
    permissions: ["license:view", "sync:send", "support:evidence"]
  }
] as const;

type RoleCode = (typeof ROLE_DEFINITIONS)[number]["code"];

type LocalAdminUserInput = {
  businessId?: string;
  userId?: string | null;
  fullName?: string | null;
  alias?: string | null;
  email?: string | null;
  phone?: string | null;
  roleCode?: string | null;
  pin?: string | null;
  status?: string | null;
  actorId?: string | null;
};

function asCleanString(value: unknown, fallback = "") {
  return typeof value === "string" && value.trim() ? value.trim() : fallback;
}

function normalizeEmail(value: unknown) {
  const email = asCleanString(value).toLocaleLowerCase("es-MX");
  return email.includes("@") ? email : null;
}

function normalizeStatus(value: unknown) {
  const status = asCleanString(value, "ACTIVE").toUpperCase();
  if (status === "INACTIVE" || status === "DELETED") return status;
  return "ACTIVE";
}

function normalizeRoleCode(value: unknown): RoleCode {
  const roleCode = asCleanString(value, "cashier") as RoleCode;
  return ROLE_DEFINITIONS.some((role) => role.code === roleCode) ? roleCode : "cashier";
}

function normalizePin(value: unknown, required: boolean) {
  const pin = asCleanString(value);
  if (!pin && !required) return null;
  if (!/^\d{6}$/.test(pin)) throw new Error("LOCAL_USER_PIN_INVALID");
  return pin;
}

function generateEmployeeId() {
  return `emp_${Date.now().toString(36)}_${randomUUID().slice(0, 8)}`;
}

function buildDisplayName(input: LocalAdminUserInput) {
  const fullName = asCleanString(input.fullName);
  const alias = asCleanString(input.alias);
  if (!fullName) throw new Error("LOCAL_USER_FULL_NAME_REQUIRED");
  return alias ? `${fullName} (${alias})` : fullName;
}

function hashPin(input: { businessId: string; userId: string; pin: string; salt: string }) {
  return createHash("sha256")
    .update(`${input.businessId}:${input.userId}:${input.salt}:${input.pin}`)
    .digest("hex");
}

async function ensureBusiness(tx: any, businessId: string) {
  await tx.business.upsert({
    where: { id: businessId },
    update: {},
    create: { id: businessId, name: "PRISMA Tablet Local", taxId: null, currency: "MXN" }
  });
}

async function audit(tx: any, input: {
  businessId: string;
  actorId?: string | null;
  topic: string;
  entityType: string;
  entityId: string;
  summary: string;
  before?: unknown;
  after?: unknown;
  metadata?: Record<string, unknown>;
}) {
  await tx.auditEvent.create({
    data: {
      id: `audit_${randomUUID()}`,
      businessId: input.businessId,
      actorId: input.actorId ?? null,
      topic: input.topic,
      entityType: input.entityType,
      entityId: input.entityId,
      summary: input.summary,
      beforeJson: input.before === undefined ? null : JSON.stringify(input.before),
      afterJson: input.after === undefined ? null : JSON.stringify(input.after),
      metadataJson: input.metadata === undefined ? null : JSON.stringify(input.metadata)
    }
  });
}

async function auditPin(tx: any, input: { businessId: string; userId: string; pin: string; actorId?: string | null; topic: string }) {
  const salt = randomBytes(16).toString("hex");
  const pinHash = hashPin({ businessId: input.businessId, userId: input.userId, pin: input.pin, salt });
  await audit(tx, {
    businessId: input.businessId,
    actorId: input.actorId,
    topic: input.topic,
    entityType: "tablet_user_pin",
    entityId: input.userId,
    summary: "PIN local de 6 dígitos actualizado; se conserva solo hash para verificación posterior.",
    metadata: { pinHash, salt, pinLength: 6, secretStoredAsHash: true }
  });
}

export async function ensureLocalAdminBootstrap(businessId = DEFAULT_POS_API_BUSINESS_ID) {
  const db = prisma as any;
  await db.$transaction(async (tx: any) => {
    await ensureBusiness(tx, businessId);
    for (const permission of DEFAULT_PERMISSIONS) {
      await tx.permission.upsert({
        where: { businessId_code: { businessId, code: permission } },
        update: { label: permission },
        create: { id: `perm_${permission.replace(/[^a-z0-9]+/gi, "_")}`, businessId, code: permission, label: permission }
      });
    }

    for (const role of ROLE_DEFINITIONS) {
      const permissionRows = await tx.permission.findMany({ where: { businessId, code: { in: role.permissions } }, select: { id: true } });
      await tx.role.upsert({
        where: { businessId_code: { businessId, code: role.code } },
        update: {
          label: role.label,
          description: role.description,
          status: "ACTIVE",
          permissions: { set: permissionRows.map((permission: { id: string }) => ({ id: permission.id })) }
        },
        create: {
          id: `role_${role.code}`,
          businessId,
          code: role.code,
          label: role.label,
          description: role.description,
          status: "ACTIVE",
          permissions: { connect: permissionRows.map((permission: { id: string }) => ({ id: permission.id })) }
        }
      });
    }
  });
}

export async function getLocalAdminSnapshot(businessId = DEFAULT_POS_API_BUSINESS_ID) {
  await ensureLocalAdminBootstrap(businessId);
  const db = prisma as any;
  const [users, roles, permissions, auditCount] = await Promise.all([
    db.user.findMany({
      where: { businessId, status: { not: "DELETED" } },
      orderBy: [{ status: "asc" }, { displayName: "asc" }],
      include: { roles: { include: { permissions: true } } }
    }),
    db.role.findMany({ where: { businessId, status: "ACTIVE" }, orderBy: { label: "asc" }, include: { permissions: true } }),
    db.permission.findMany({ where: { businessId }, orderBy: { code: "asc" } }),
    db.auditEvent.count({ where: { businessId, topic: { startsWith: "tablet.user." } } }).catch(() => 0)
  ]);

  const supportRoleId = roles.find((role: any) => role.code === "support_internal")?.id;
  const operationalUsers = users
    .filter((user: any) => !supportRoleId || !user.roles.some((role: any) => role.id === supportRoleId))
    .map((user: any) => ({
      id: user.id,
      employeeId: user.id,
      displayName: user.displayName,
      email: user.email,
      status: user.status,
      createdAt: user.createdAt.toISOString(),
      updatedAt: user.updatedAt.toISOString(),
      lastAccess: null as string | null,
      roles: user.roles.map((role: any) => ({
        code: role.code,
        label: role.label,
        permissions: role.permissions.map((permission: any) => permission.code).sort()
      }))
    }));

  return {
    businessId,
    users: operationalUsers,
    roles: roles
      .filter((role: any) => role.code !== "support_internal")
      .map((role: any) => ({
        code: role.code,
        label: role.label,
        description: role.description,
        permissions: role.permissions.map((permission: any) => permission.code).sort()
      })),
    permissions: permissions.map((permission: any) => ({ code: permission.code, label: permission.label })),
    support: {
      internalRoleConfigured: roles.some((role: any) => role.code === "support_internal"),
      hiddenFromOperationalList: true,
      supportEvidencePermission: permissions.some((permission: any) => permission.code === "support:evidence")
    },
    auditTrailCount: auditCount
  };
}

export async function createLocalUser(input: LocalAdminUserInput) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  const displayName = buildDisplayName(input);
  const roleCode = normalizeRoleCode(input.roleCode);
  const pin = normalizePin(input.pin, true);
  const phone = asCleanString(input.phone);
  const alias = asCleanString(input.alias);
  const db = prisma as any;
  const userId = generateEmployeeId();
  await ensureLocalAdminBootstrap(businessId);
  return db.$transaction(async (tx: any) => {
    const role = await tx.role.findUniqueOrThrow({ where: { businessId_code: { businessId, code: roleCode } } });
    const user = await tx.user.create({
      data: {
        id: userId,
        businessId,
        displayName,
        email: normalizeEmail(input.email),
        status: "ACTIVE",
        roles: { connect: [{ id: role.id }] }
      },
      include: { roles: true }
    });
    if (pin) await auditPin(tx, { businessId, userId, pin, actorId: input.actorId, topic: "tablet.user.pin.created" });
    await audit(tx, {
      businessId,
      actorId: input.actorId,
      topic: "tablet.user.created",
      entityType: "tablet_user",
      entityId: userId,
      summary: "Usuario local creado con baja suave, rol y PIN de 6 dígitos.",
      after: { userId, displayName, email: user.email, roleCode, status: user.status },
      metadata: { alias: alias || null, phone: phone || null, employeeId: userId, pinConfigured: Boolean(pin) }
    });
    return { userId, status: user.status };
  });
}

export async function updateLocalUser(input: LocalAdminUserInput) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  const userId = asCleanString(input.userId);
  if (!userId) throw new Error("LOCAL_USER_ID_REQUIRED");
  const roleCode = normalizeRoleCode(input.roleCode);
  const pin = normalizePin(input.pin, false);
  const db = prisma as any;
  await ensureLocalAdminBootstrap(businessId);
  return db.$transaction(async (tx: any) => {
    const before = await tx.user.findFirstOrThrow({ where: { id: userId, businessId }, include: { roles: true } });
    const role = await tx.role.findUniqueOrThrow({ where: { businessId_code: { businessId, code: roleCode } } });
    const user = await tx.user.update({
      where: { id_businessId: { id: userId, businessId } },
      data: {
        displayName: buildDisplayName(input),
        email: normalizeEmail(input.email),
        status: normalizeStatus(input.status),
        roles: { set: [{ id: role.id }] }
      },
      include: { roles: true }
    });
    if (pin) await auditPin(tx, { businessId, userId, pin, actorId: input.actorId, topic: "tablet.user.pin.updated" });
    await audit(tx, {
      businessId,
      actorId: input.actorId,
      topic: "tablet.user.updated",
      entityType: "tablet_user",
      entityId: userId,
      summary: "Usuario local actualizado con rol, estado y auditoría.",
      before: { displayName: before.displayName, email: before.email, status: before.status, roles: before.roles.map((role: any) => role.code) },
      after: { displayName: user.displayName, email: user.email, status: user.status, roles: user.roles.map((role: any) => role.code) },
      metadata: { alias: asCleanString(input.alias) || null, phone: asCleanString(input.phone) || null, pinUpdated: Boolean(pin) }
    });
    return { userId, status: user.status };
  });
}

export async function setLocalUserStatus(input: { businessId?: string; userId?: string | null; status: "ACTIVE" | "INACTIVE" | "DELETED"; actorId?: string | null }) {
  const businessId = input.businessId || DEFAULT_POS_API_BUSINESS_ID;
  const userId = asCleanString(input.userId);
  if (!userId) throw new Error("LOCAL_USER_ID_REQUIRED");
  const db = prisma as any;
  await ensureLocalAdminBootstrap(businessId);
  return db.$transaction(async (tx: any) => {
    const before = await tx.user.findFirstOrThrow({ where: { id: userId, businessId } });
    const user = await tx.user.update({ where: { id_businessId: { id: userId, businessId } }, data: { status: input.status } });
    await audit(tx, {
      businessId,
      actorId: input.actorId,
      topic: input.status === "DELETED" ? "tablet.user.soft_deleted" : "tablet.user.status.updated",
      entityType: "tablet_user",
      entityId: userId,
      summary: input.status === "DELETED" ? "Usuario local marcado como baja suave." : "Estado del usuario local actualizado.",
      before: { status: before.status },
      after: { status: user.status }
    });
    return { userId, status: user.status };
  });
}

export type LocalAdminSnapshot = Awaited<ReturnType<typeof getLocalAdminSnapshot>>;
