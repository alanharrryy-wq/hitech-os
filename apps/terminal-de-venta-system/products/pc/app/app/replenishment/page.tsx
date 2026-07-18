import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function ReplenishmentPage() {
  const workspace = await getOperationWorkspace("replenishment");
  return <OperationWorkspace workspace={workspace} />;
}
