import { fail, ok } from "@/server/pos-api/responses";
import { readCashMovementInput, readCurrentShiftInput, shiftCashRepository, ShiftError } from "@/server/pos-shift";
import { TabletPermissionError } from "@/server/pos-security/permissions.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const input = readCurrentShiftInput(new URL(request.url).searchParams);
    const movements = await shiftCashRepository.recentMovements(input);
    return ok({ movements }, undefined, { endpoint: "GET /api/pos/cash/movements", businessId: input.businessId, terminalId: input.terminalId });
  } catch (error) {
    if (error instanceof ShiftError) return fail(error.code, error.message, error.status, error.details);
    return fail("CASH_MOVEMENT_INTERNAL_ERROR", "No se pudieron consultar los movimientos de caja.", 500);
  }
}

export async function POST(request: Request) {
  try {
    const input = await readCashMovementInput(request);
    const result = await shiftCashRepository.recordMovement(input);
    return ok(result, { status: result.movement.deduplicated ? 200 : 201 }, {
      endpoint: "POST /api/pos/cash/movements",
      businessId: input.businessId,
      terminalId: input.terminalId,
      cashSessionId: result.movement.cashSessionId,
      deduplicated: result.movement.deduplicated
    });
  } catch (error) {
    if (error instanceof ShiftError) return fail(error.code, error.message, error.status, error.details);
    if (error instanceof TabletPermissionError) return fail(error.code, error.message, error.status, error.details);
    return fail("CASH_MOVEMENT_INTERNAL_ERROR", "No se pudo registrar el movimiento de caja.", 500);
  }
}
