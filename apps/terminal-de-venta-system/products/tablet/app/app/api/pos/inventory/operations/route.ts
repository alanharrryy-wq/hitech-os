import { guardTabletLocalPosForApi } from "@/server/licensing/tablet-license-api";
import { inventoryOperationsRepository } from "@/server/inventory-operations/repository.prisma";
import { InventoryOperationError, readInventoryOperationInput, readInventorySnapshotInput } from "@/server/inventory-operations/types";
import { fail, ok } from "@/server/pos-api/responses";
import { TabletPermissionError } from "@/server/pos-security/permissions.prisma";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const licenseGate = await guardTabletLocalPosForApi();
  if (licenseGate) return licenseGate;
  try {
    const input = readInventorySnapshotInput(new URL(request.url).searchParams);
    const snapshot = await inventoryOperationsRepository.snapshot(input);
    return ok(snapshot, undefined, { endpoint: "GET /api/pos/inventory/operations", businessId: input.businessId, terminalId: input.terminalId });
  } catch (error) {
    if (error instanceof InventoryOperationError) return fail(error.code, error.message, error.status, error.details);
    return fail("INVENTORY_OPERATIONS_INTERNAL_ERROR", "No se pudo consultar la operación de inventario.", 500);
  }
}

export async function POST(request: Request) {
  const licenseGate = await guardTabletLocalPosForApi();
  if (licenseGate) return licenseGate;
  try {
    const input = await readInventoryOperationInput(request);
    const result = await inventoryOperationsRepository.execute(input);
    return ok({ result }, { status: result.deduplicated ? 200 : 201 }, { endpoint: "POST /api/pos/inventory/operations", businessId: input.businessId, terminalId: input.terminalId, action: input.action, operationId: result.operationId, deduplicated: result.deduplicated });
  } catch (error) {
    if (error instanceof InventoryOperationError) return fail(error.code, error.message, error.status, error.details);
    if (error instanceof TabletPermissionError) return fail(error.code, error.message, error.status, error.details);
    return fail("INVENTORY_OPERATIONS_INTERNAL_ERROR", "No se pudo completar la operación de inventario.", 500);
  }
}
