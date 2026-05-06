export const TABLET_AUDIT_ROLES = ["tablet_operator", "tablet_supervisor"] as const;

export const TABLET_SENSITIVE_ACTION_PERMISSIONS = {
  "pos.sale.complete": "pos.sale.complete",
  "export.local.create": "export.local.create",
  "inventory.local.adjust": "inventory.local.adjust",
  "shift.close": "shift.close"
} as const;

export type TabletAuditRole = (typeof TABLET_AUDIT_ROLES)[number];
export type TabletSensitiveAction = keyof typeof TABLET_SENSITIVE_ACTION_PERMISSIONS;

export type TabletAuditMeta = {
  actorId: string;
  role: TabletAuditRole;
  terminalId: string;
  businessId: string;
  action: TabletSensitiveAction;
  permission: (typeof TABLET_SENSITIVE_ACTION_PERMISSIONS)[TabletSensitiveAction];
  entityType: string;
  entityId: string;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  createdAt: string;
  offlineAllowed: true;
  source: "tablet";
};

type TabletAuditInput = {
  actorId?: string | null;
  role?: string | null;
  terminalId: string;
  businessId: string;
  entityType: string;
  entityId: string;
  before?: Record<string, unknown> | null;
  after?: Record<string, unknown> | null;
  createdAt?: string | Date | null;
};

function normalizeRole(role?: string | null): TabletAuditRole {
  return role === "tablet_supervisor" ? "tablet_supervisor" : "tablet_operator";
}

function normalizeCreatedAt(createdAt?: string | Date | null) {
  if (createdAt instanceof Date) return createdAt.toISOString();
  if (typeof createdAt === "string" && createdAt.trim()) return createdAt.trim();
  return new Date().toISOString();
}

export function readTabletAuditActor(searchParams: URLSearchParams) {
  return {
    actorId:
      searchParams.get("actorId")?.trim() ||
      searchParams.get("operatorId")?.trim() ||
      searchParams.get("cashier")?.trim() ||
      "tablet-operator",
    role: normalizeRole(searchParams.get("role"))
  };
}

export function tabletAuditMeta(action: TabletSensitiveAction, input: TabletAuditInput): TabletAuditMeta {
  return {
    actorId: input.actorId?.trim() || "tablet-operator",
    role: normalizeRole(input.role),
    terminalId: input.terminalId,
    businessId: input.businessId,
    action,
    permission: TABLET_SENSITIVE_ACTION_PERMISSIONS[action],
    entityType: input.entityType,
    entityId: input.entityId,
    before: input.before ?? null,
    after: input.after ?? null,
    createdAt: normalizeCreatedAt(input.createdAt),
    offlineAllowed: true,
    source: "tablet"
  };
}

export function tabletAuditHeaders(audit: TabletAuditMeta): Record<string, string> {
  return {
    "x-prisma-audit-action": audit.action,
    "x-prisma-audit-permission": audit.permission,
    "x-prisma-actor-id": audit.actorId,
    "x-prisma-actor-role": audit.role,
    "x-prisma-audit-entity": `${audit.entityType}:${audit.entityId}`
  };
}
