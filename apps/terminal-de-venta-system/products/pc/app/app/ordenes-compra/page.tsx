import { DecisionScreen } from "@components/uiux/decision-screen";
import { purchasingScreenContract } from "@/uiux/purchasing-screen-contract";

export const dynamic = "force-static";

export default function PurchaseOrdersPage() {
  return <DecisionScreen {...purchasingScreenContract} currentPath="/ordenes-compra" />;
}
