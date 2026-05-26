import { fail, ok } from "@/server/pos-api/responses";
import { DEFAULT_POS_API_BUSINESS_ID } from "@/server/pos-api/validators";
import { createLocalUser, getLocalAdminSnapshot, setLocalUserStatus, updateLocalUser } from "@/server/pos-api/local-admin.prisma";
import { toPosApiError } from "@/server/pos-api/errors";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function businessIdFromUrl(request: Request) {
  const value = new URL(request.url).searchParams.get("businessId")?.trim();
  return value || DEFAULT_POS_API_BUSINESS_ID;
}

function businessIdFromBody(body: any) {
  return typeof body?.businessId === "string" && body.businessId.trim() ? body.businessId.trim() : DEFAULT_POS_API_BUSINESS_ID;
}

function cleanBody(body: any) {
  return {
    businessId: businessIdFromBody(body),
    userId: typeof body?.userId === "string" ? body.userId : null,
    fullName: typeof body?.fullName === "string" ? body.fullName : null,
    alias: typeof body?.alias === "string" ? body.alias : null,
    email: typeof body?.email === "string" ? body.email : null,
    phone: typeof body?.phone === "string" ? body.phone : null,
    roleCode: typeof body?.roleCode === "string" ? body.roleCode : null,
    pin: typeof body?.pin === "string" ? body.pin : null,
    status: typeof body?.status === "string" ? body.status : null,
    actorId: typeof body?.actorId === "string" ? body.actorId : null
  };
}

export async function GET(request: Request) {
  try {
    const businessId = businessIdFromUrl(request);
    const snapshot = await getLocalAdminSnapshot(businessId);
    return ok({ snapshot }, undefined, {
      endpoint: "GET /api/pos/admin/local-users",
      businessId,
      usersRolesPermissions: true
    });
  } catch (error) {
    return toPosApiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const action = typeof body?.action === "string" ? body.action : "";
    const input = cleanBody(body);
    let result: unknown;

    if (action === "create_user") {
      result = await createLocalUser(input);
    } else if (action === "update_user") {
      result = await updateLocalUser(input);
    } else if (action === "deactivate_user") {
      result = await setLocalUserStatus({ businessId: input.businessId, userId: input.userId, status: "INACTIVE", actorId: input.actorId });
    } else if (action === "reactivate_user") {
      result = await setLocalUserStatus({ businessId: input.businessId, userId: input.userId, status: "ACTIVE", actorId: input.actorId });
    } else if (action === "soft_delete_user") {
      result = await setLocalUserStatus({ businessId: input.businessId, userId: input.userId, status: "DELETED", actorId: input.actorId });
    } else {
      return fail("LOCAL_USER_ACTION_REQUIRED", "Selecciona una acción válida para usuarios locales.", 400);
    }

    const snapshot = await getLocalAdminSnapshot(input.businessId);
    return ok({ result, snapshot }, { status: 200 }, {
      endpoint: "POST /api/pos/admin/local-users",
      businessId: input.businessId,
      localUsersRolesPermissions: true
    });
  } catch (error) {
    if (error instanceof Error) {
      if (error.message === "LOCAL_USER_PIN_INVALID") {
        return fail("LOCAL_USER_PIN_INVALID", "El PIN debe tener exactamente 6 dígitos.", 400);
      }
      if (error.message === "LOCAL_USER_FULL_NAME_REQUIRED") {
        return fail("LOCAL_USER_FULL_NAME_REQUIRED", "Captura el nombre completo del usuario.", 400);
      }
      if (error.message === "LOCAL_USER_ID_REQUIRED") {
        return fail("LOCAL_USER_ID_REQUIRED", "Selecciona un usuario local válido.", 400);
      }
    }
    return toPosApiError(error);
  }
}
