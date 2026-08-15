import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function SupplierReceivingPage() {
  const workspace = await getOperationWorkspace("receiving");
  return (
    <OperationWorkspace
      currentPath="/recepcion-proveedor"
      workspace={{
        ...workspace,
        kicker: "recepción de proveedor",
        title: "Recepción de proveedor",
        description: "Recepciones reales contra orden, con cantidades, diferencias y total visibles."
      }}
    />
  );
}
