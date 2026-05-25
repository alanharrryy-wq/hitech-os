import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function DashboardKPIPage() {
  const workspace = await getOperationWorkspace("dashboard");
  return (
    <main
      data-prisma-visual="cloudglass-layer-pack-01"
      data-prisma-background="fractured-graphite-cloudglass"
    >
      <OperationWorkspace workspace={workspace} />
    </main>
  );
}
