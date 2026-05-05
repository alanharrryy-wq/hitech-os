import { ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { getConflictCatalog } from "@/lib/backoffice/conflicts";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";
import { backofficeAuditMeta, readBackofficeAuditActor } from "@/lib/backoffice/security-audit";

import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api"; // PRISMA_LICENSE_02AB_PC_IMPORT
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  
  // PRISMA_LICENSE_02AB_BEGIN:sync.conflict.resolve
  const prismaLicenseGate = await guardPcFeatureForApi("sync.conflict.resolve");
  if (prismaLicenseGate) return prismaLicenseGate;
  // PRISMA_LICENSE_02AB_END:sync.conflict.resolve
try {
    const sync = await getBackofficeModuleOverview("sync");
    const actor = readBackofficeAuditActor(request);
    const audit = backofficeAuditMeta("sync.conflict.resolve", {
      ...actor,
      entityType: "ConflictCatalog",
      entityId: "sync-conflicts",
      after: {
        mode: "read_only_catalog",
        rows: sync.table.rows.length
      }
    });
    return ok(
      {
        catalog: getConflictCatalog(),
        syncMetrics: sync.metrics,
        rows: sync.table.rows
      },
      {
        endpoint: "GET /api/backoffice/sync/conflicts",
        persistence: sync.meta.persistence,
        permission: "sync.conflict.resolve",
        mode: "read_only_catalog",
        audit
      }
    );
  } catch (error) {
    return toBackofficeError(error);
  }
}
