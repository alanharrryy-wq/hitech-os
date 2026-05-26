import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { DEFAULT_POS_API_BUSINESS_ID } from "@/server/pos-api/validators";
import { configureSalesResetSecurity, performSalesReset, previewSalesReset } from "@/server/pos-api/sales-reset.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function businessIdFromUrl(request: Request) {
  const value = new URL(request.url).searchParams.get("businessId")?.trim();
  return value || DEFAULT_POS_API_BUSINESS_ID;
}

export async function GET(request: Request) {
  try {
    const businessId = businessIdFromUrl(request);
    const preview = await previewSalesReset(businessId);
    return ok({ preview }, undefined, {
      endpoint: "GET /api/pos/admin/sales-reset",
      businessId,
      locked: true,
      destructiveAction: true
    });
  } catch (error) {
    return toPosApiError(error);
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const businessId = typeof body?.businessId === "string" && body.businessId.trim()
      ? body.businessId.trim()
      : DEFAULT_POS_API_BUSINESS_ID;
    const operatorNote = typeof body?.operatorNote === "string" ? body.operatorNote.slice(0, 600) : null;
    const questionId = typeof body?.questionId === "string" ? body.questionId : "";
    const securityAnswer = typeof body?.securityAnswer === "string" ? body.securityAnswer : "";
    const adminPin = typeof body?.adminPin === "string" ? body.adminPin : "";

    if (body?.action === "configure_security") {
      const result = await configureSalesResetSecurity({ businessId, questionId, securityAnswer, adminPin, operatorNote });
      return ok({ result }, { status: 200 }, {
        endpoint: "POST /api/pos/admin/sales-reset",
        businessId,
        destructiveAction: false,
        securityConfigured: true
      });
    }

    const result = await performSalesReset({ businessId, questionId, securityAnswer, adminPin, operatorNote });
    return ok({ result }, { status: 200 }, {
      endpoint: "POST /api/pos/admin/sales-reset",
      businessId,
      destructiveAction: true,
      preservesLicenseConfig: true
    });
  } catch (error) {
    if (error instanceof Error) {
      if (error.message === "RESET_SECURITY_NOT_CONFIGURED") {
        return fail("RESET_SECURITY_NOT_CONFIGURED", "Configura primero la pregunta de seguridad y el PIN admin.", 428);
      }
      if (error.message === "RESET_ADMIN_PIN_INVALID") {
        return fail("RESET_ADMIN_PIN_INVALID", "El PIN admin no coincide.", 403);
      }
      if (error.message === "RESET_SECURITY_ANSWER_INVALID") {
        return fail("RESET_SECURITY_ANSWER_INVALID", "La respuesta de seguridad no coincide.", 403);
      }
      if (error.message === "RESET_SECURITY_QUESTION_MISMATCH") {
        return fail("RESET_SECURITY_QUESTION_MISMATCH", "La pregunta seleccionada no corresponde a la configuración local.", 403);
      }
      if (error.message === "RESET_ADMIN_PIN_INVALID_FORMAT") {
        return fail("RESET_ADMIN_PIN_INVALID_FORMAT", "El PIN admin debe tener exactamente 6 dígitos.", 400);
      }
      if (error.message === "RESET_SECURITY_ANSWER_INVALID_FORMAT") {
        return fail("RESET_SECURITY_ANSWER_INVALID_FORMAT", "La respuesta debe ser una sola palabra de 2 a 48 caracteres.", 400);
      }
      if (error.message === "RESET_SECURITY_QUESTION_INVALID") {
        return fail("RESET_SECURITY_QUESTION_INVALID", "Selecciona una pregunta de seguridad válida.", 400);
      }
    }
    return toPosApiError(error);
  }
}
