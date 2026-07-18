import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function SuppliersPage() {
  const workspace = await getOperationWorkspace("purchasing");
  return (
    <OperationWorkspace
      currentPath="/proveedores"
      workspace={{
        ...workspace,
        kicker: "proveedores",
        title: "Proveedores y compras",
        description: "Órdenes, recepción y señales de reabasto asociadas a proveedores canónicos."
      }}
    />
  );
}
