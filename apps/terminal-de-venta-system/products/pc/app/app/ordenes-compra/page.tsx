import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function PurchaseOrdersPage() {
  const workspace = await getOperationWorkspace("purchasing");
  return (
    <OperationWorkspace
      currentPath="/ordenes-compra"
      workspace={{
        ...workspace,
        kicker: "órdenes de compra",
        title: "Órdenes de compra",
        description: "Pedidos reales, proveedor, unidades, pendientes, total y riesgo desde persistencia canónica."
      }}
    />
  );
}
