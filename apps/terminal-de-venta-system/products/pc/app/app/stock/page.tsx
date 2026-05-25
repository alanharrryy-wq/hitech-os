import { DecisionScreen } from "@components/uiux/decision-screen";
import { inventoryScreenContract } from "@/uiux/inventory-screen-contract";

export const dynamic = "force-dynamic";

export default async function StockPage() {
  return <DecisionScreen {...inventoryScreenContract} currentPath="/stock" />;
}
