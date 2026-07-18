import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { readOperationalTaskUpdate, updateOperationalTask } from "@/server/services/operational-task.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function PATCH(request: Request, context: { params: Promise<{ taskId: string }> }) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const taskId = (await context.params).taskId.trim();
    if (!taskId) return fail("OPERATIONAL_TASK_ID_REQUIRED", "La tarea no es válida.", 400);
    const body = await request.json().catch(() => {
      throw new Error("INVALID_JSON_BODY");
    });
    const task = await updateOperationalTask(taskId, readOperationalTaskUpdate(body));
    if (!task) return fail("OPERATIONAL_TASK_NOT_FOUND", "La tarea no existe en este negocio.", 404);
    return ok({ task }, { endpoint: "PATCH /api/backoffice/operational-tasks/:taskId", readAfterWrite: true });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "El cuerpo JSON no es válido.", 400);
    if (code === "OPERATIONAL_TASK_VERSION_REQUIRED") return fail(code, "La actualización requiere la versión leída de la tarea.", 400);
    if (code === "OPERATIONAL_TASK_STATUS_INVALID") return fail(code, "El estado solicitado no es válido.", 400);
    if (code === "OPERATIONAL_TASK_ASSIGNEE_NOT_FOUND") return fail(code, "La persona asignada no pertenece al negocio o no está activa.", 422);
    if (code === "OPERATIONAL_TASK_VERSION_CONFLICT") return fail(code, "La tarea cambió en otra sesión. Vuelve a cargarla antes de actualizar.", 409);
    if (code === "OPERATIONAL_TASK_TERMINAL_STATE") return fail(code, "Una tarea completada o cancelada no puede volver a abrirse desde esta acción.", 409);
    return toBackofficeError(error);
  }
}
