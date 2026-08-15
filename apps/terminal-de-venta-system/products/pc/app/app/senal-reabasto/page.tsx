import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function ReplenishmentSignalPage() {
  const workspace = await getOperationWorkspace("replenishment");
  return (
    <OperationWorkspace
      currentPath="/senal-reabasto"
      workspace={{
        ...workspace,
        kicker: "señales de reabasto",
        title: "Señales de reabasto",
        description: "Prioridad, existencias, mínimos, máximos y sugerido leídos de señales canónicas de reabasto."
      }}
    />
  );
}
