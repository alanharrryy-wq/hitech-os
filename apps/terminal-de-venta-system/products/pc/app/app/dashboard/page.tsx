import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function DashboardKPIPage() {
  const workspace = await getOperationWorkspace("dashboard");
  return <OperationWorkspace workspace={workspace} />;
}
