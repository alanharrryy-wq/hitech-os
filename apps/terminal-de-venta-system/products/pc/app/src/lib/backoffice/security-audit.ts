export const BACKOFFICE_AUDIT_ROLES = ["pc_backoffice", "pc_admin"] as const;

export const BACKOFFICE_SENSITIVE_ACTION_PERMISSIONS = {
  "catalog.write": "catalog.write",
  "inventory.adjust.approve": "inventory.adjust.approve",
  "purchase.write": "purchase.write",
  "receiving.write": "receiving.write",
  "sync.ingest.persist": "sync.ingest.write",
  "sync.conflict.resolve": "sync.conflict.resolve",
  "export.consolidated.create": "export.consolidated.create"
} as const;

export type BackofficeAuditRole = (typeof BACKOFFICE_AUDIT_ROLES)[number];
export type BackofficeSensitiveAction = keyof typeof BACKOFFICE_SENSITIVE_ACTION_PERMISSIONS;

export type BackofficeAuditMeta = {
  actorId: string;
  role: BackofficeAuditRole;
  terminalId: string;
  businessId: string;
  action: BackofficeSensitiveAction;
  permission: (typeof BACKOFFICE_SENSITIVE_ACTION_PERMISSIONS)[BackofficeSensitiveAction];
  entityType: string;
  entityId: string;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
  createdAt: string;
  offlineAllowed: false;
  source: "pc";
};

type BackofficeAuditInput = {
  actorId?: string | null;
  role?: string | null;
  terminalId?: string | null;
  businessId?: string | null;
  entityType: string;
  entityId: string;
  before?: Record<string, unknown> | null;
  after?: Record<string, unknown> | null;
  createdAt?: string | Date | null;
};

function normalizeRole(role?: string | null): BackofficeAuditRole {
  return role === "pc_admin" ? "pc_admin" : "pc_backoffice";
}

function normalizeCreatedAt(createdAt?: string | Date | null) {
  if (createdAt instanceof Date) return createdAt.toISOString();
  if (typeof createdAt === "string" && createdAt.trim()) return createdAt.trim();
  return new Date().toISOString();
}

export function readBackofficeAuditActor(request: Request) {
  return {
    actorId:
      request.headers.get("x-actor-id")?.trim() ||
      request.headers.get("x-operator-id")?.trim() ||
      "pc-backoffice-operator",
    role: normalizeRole(request.headers.get("x-actor-role"))
  };
}

export function backofficeAuditMeta(action: BackofficeSensitiveAction, input: BackofficeAuditInput): BackofficeAuditMeta {
  return {
    actorId: input.actorId?.trim() || "pc-backoffice-operator",
    role: normalizeRole(input.role),
    terminalId: input.terminalId?.trim() || "pc-backoffice",
    businessId: input.businessId?.trim() || "backoffice",
    action,
    permission: BACKOFFICE_SENSITIVE_ACTION_PERMISSIONS[action],
    entityType: input.entityType,
    entityId: input.entityId,
    before: input.before ?? null,
    after: input.after ?? null,
    createdAt: normalizeCreatedAt(input.createdAt),
    offlineAllowed: false,
    source: "pc"
  };
}
