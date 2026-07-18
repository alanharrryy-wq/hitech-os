import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function ReceivingPage() {
  const workspace = await getOperationWorkspace("receiving");
  return <OperationWorkspace workspace={workspace} />;
}
