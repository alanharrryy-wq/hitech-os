import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function ReceivingIncidentsPage() {
  const workspace = await getOperationWorkspace("receiving");
  const receipts = workspace.receipts.filter((row) => row.discrepancyQty !== 0);
  return (
    <OperationWorkspace
      currentPath="/incidencias-recepcion"
      workspace={{
        ...workspace,
        kicker: "diferencias de recepción",
        title: "Incidencias de recepción",
        description: "Sólo recepciones reales con diferencia entre cantidades esperadas y recibidas.",
        receipts,
        summary: { ...workspace.summary, receiptsWithDiscrepancy: receipts.length }
      }}
    />
  );
}
