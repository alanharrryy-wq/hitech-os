import { DecisionScreen } from "@components/uiux/decision-screen";
import { reportsScreenContract } from "@/uiux/reports-screen-contract";

export const dynamic = "force-dynamic";

export default async function TableroKpiPage() {
  return <DecisionScreen {...reportsScreenContract} currentPath="/tablero-kpi" />;
}
