import { DecisionScreen } from "@components/uiux/decision-screen";
import { purchasingScreenContract } from "@/uiux/purchasing-screen-contract";

export const dynamic = "force-dynamic";

export default async function ReceivingIncidentsPage() {
  return <DecisionScreen {...purchasingScreenContract} currentPath="/receiving" />;
}
