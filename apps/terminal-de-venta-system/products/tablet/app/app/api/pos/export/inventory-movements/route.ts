import { toPosApiError } from "@/server/pos-api/errors";
import { fail, ok } from "@/server/pos-api/responses";
import { readPosExportInput, validatorErrorToMessage } from "@/server/pos-api/validators";
import { buildInventoryMovementsExport, csvResponse } from "@/server/pos-export";
import { readTabletAuditActor, tabletAuditHeaders, tabletAuditMeta } from "@/server/pos-security/audit";

import { guardTabletFeatureForApi } from "@/server/licensing/tablet-license-api"; // PRISMA_LICENSE_02AB_TABLET_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  
  // PRISMA_LICENSE_02AB_BEGIN:export.advanced
  const prismaLicenseGate = await guardTabletFeatureForApi("export.advanced");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:export.advanced
try {
    const searchParams = new URL(request.url).searchParams;
    const input = readPosExportInput(searchParams);
    const result = await buildInventoryMovementsExport(input);
    const actor = readTabletAuditActor(searchParams);
    const audit = tabletAuditMeta("export.local.create", {
      ...actor,
      terminalId: input.terminalId ?? "tablet-local",
      businessId: input.businessId,
      entityType: "InventoryMovementExport",
      entityId: result.filename,
      after: { format: input.format, count: result.data.count }
    });
    if (input.format === "csv") return csvResponse(result.filename, result.csv, tabletAuditHeaders(audit));
    return ok(result.data, undefined, {
      endpoint: "GET /api/pos/export/inventory-movements",
      format: input.format,
      businessId: input.businessId,
      audit
    });
  } catch (error) {
    const validation = validatorErrorToMessage(error);
    if (validation.code !== "POS_API_VALIDATION_ERROR") {
      return fail(validation.code, validation.message, 400);
    }
    return toPosApiError(error);
  }
}
