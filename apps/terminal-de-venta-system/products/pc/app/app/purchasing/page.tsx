import { OperationWorkspace } from "@components/operations/operation-workspace";
import { getOperationWorkspace } from "@/server/services/operation-control.service";

export const dynamic = "force-dynamic";

export default async function PurchasingPage() {
  const workspace = await getOperationWorkspace("purchasing");
  return <OperationWorkspace workspace={workspace} />;
}
