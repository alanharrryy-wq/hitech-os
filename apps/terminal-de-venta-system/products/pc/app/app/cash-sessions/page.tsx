import { DecisionScreen } from "@components/uiux/decision-screen";
import { salesAndCashScreenContract } from "@/uiux/sales-and-cash-screen-contract";

export const dynamic = "force-dynamic";

export default async function CashSessionsPage() {
  return <DecisionScreen {...salesAndCashScreenContract} currentPath="/cash-sessions" />;
}
