import { prisma } from "../prisma/client";
import { readRuntimeSnapshotInput } from "../tablet-runtime-snapshot";

export type TabletOperationalPermission = "cash:adjust" | "inventory:adjust";

export type TabletPermissionEvidence = {
  actorId: string;
  permission: TabletOperationalPermission;
  authorizationMode: "role_permission" | "configured_runtime_operator";
};

export class TabletPermissionError extends Error {
  constructor(
    readonly code: string,
    message: string,
    readonly status = 403,
    readonly details: Record<string, unknown> = {}
  ) {
    super(message);
    this.name = "TabletPermissionError";
  }
}

type PermissionInput = {
  businessId: string;
  terminalId: string;
  actorId: string;
  permission: TabletOperationalPermission;
};

export async function assertTabletOperationalPermission(
  input: PermissionInput,
  db: any = prisma
): Promise<TabletPermissionEvidence> {
  const runtime = readRuntimeSnapshotInput();
  if (input.businessId !== runtime.businessId || input.terminalId !== runtime.terminalId) {
    throw new TabletPermissionError(
      "TABLET_OPERATION_SCOPE_MISMATCH",
      "La operación no pertenece al negocio o terminal configurados en esta Tablet.",
      403,
      { businessId: input.businessId, terminalId: input.terminalId }
    );
  }

  const [actor, activeUserCount] = await Promise.all([
    db.user.findFirst({
      where: { id: input.actorId, businessId: input.businessId, status: "ACTIVE" },
      include: { roles: { where: { status: "ACTIVE" }, include: { permissions: true } } }
    }),
    db.user.count({ where: { businessId: input.businessId, status: "ACTIVE" } })
  ]);

  if (actor) {
    const permissions = new Set<string>(
      actor.roles.flatMap((role: { permissions: Array<{ code: string }> }) => role.permissions.map((permission) => permission.code))
    );
    if (!permissions.has(input.permission)) {
      throw new TabletPermissionError(
        "TABLET_OPERATION_PERMISSION_DENIED",
        "El responsable no tiene permiso para completar esta operación.",
        403,
        { actorId: input.actorId, permission: input.permission }
      );
    }
    return { actorId: actor.id, permission: input.permission, authorizationMode: "role_permission" };
  }

  if (activeUserCount > 0 || input.actorId !== runtime.operatorId) {
    throw new TabletPermissionError(
      "TABLET_OPERATION_ACTOR_DENIED",
      "El responsable no coincide con un usuario activo autorizado en esta Tablet.",
      403,
      { actorId: input.actorId, permission: input.permission }
    );
  }

  return {
    actorId: input.actorId,
    permission: input.permission,
    authorizationMode: "configured_runtime_operator"
  };
}
