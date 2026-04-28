import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { readCompleteSaleInput, validatorErrorToMessage } from "@/server/pos-api/validators";
import { posEngineRepository } from "@/server/pos-engine";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const input = await readCompleteSaleInput(request);
    const sale = await posEngineRepository.completeLocalSale(input);
    return ok({ sale }, { status: 201 }, {
      endpoint: "POST /api/pos/sales/complete",
      businessId: sale.businessId,
      terminalId: sale.terminalId,
      events: sale.events.map((event) => event.topic)
    });
  } catch (error) {
    const validation = validatorErrorToMessage(error);
    if (validation.code !== "POS_API_VALIDATION_ERROR") {
      return fail(validation.code, validation.message, 400);
    }
    return toPosApiError(error);
  }
}
