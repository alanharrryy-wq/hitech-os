import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { createOperationalTask, listOperationalTasks, readOperationalTaskCreate } from "@/server/services/operational-task.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const status = new URL(request.url).searchParams.get("status");
    const tasks = await listOperationalTasks(status === "active" || status === "open" || status === "in_progress" || status === "completed" || status === "cancelled" ? status : undefined);
    return ok({ tasks }, { endpoint: "GET /api/backoffice/operational-tasks", bounded: true });
  } catch (error) {
    return toBackofficeError(error);
  }
}

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => {
      throw new Error("INVALID_JSON_BODY");
    });
    const result = await createOperationalTask(readOperationalTaskCreate(body));
    return ok(result, { endpoint: "POST /api/backoffice/operational-tasks", idempotent: result.replayed }, { status: result.replayed ? 200 : 201 });
  } catch (error) {
    const code = error instanceof Error ? error.message : "";
    if (code === "INVALID_JSON_BODY") return fail(code, "El cuerpo JSON no es válido.", 400);
    if (code === "OPERATIONAL_TASK_TITLE_REQUIRED") return fail(code, "Captura un título de al menos 3 caracteres.", 400);
    if (code === "OPERATIONAL_TASK_AREA_REQUIRED") return fail(code, "Selecciona un área operativa.", 400);
    if (code === "OPERATIONAL_TASK_IDEMPOTENCY_REQUIRED") return fail(code, "La solicitud no incluye una llave de idempotencia válida.", 400);
    if (code === "OPERATIONAL_TASK_DUE_AT_INVALID") return fail(code, "La fecha límite no es válida.", 400);
    if (code === "OPERATIONAL_TASK_ASSIGNEE_NOT_FOUND") return fail(code, "La persona asignada no pertenece al negocio o no está activa.", 422);
    return toBackofficeError(error);
  }
}
