import { DecisionScreen } from "@components/uiux/decision-screen";
import { reportsScreenContract } from "@/uiux/reports-screen-contract";

export const dynamic = "force-static";

export default function MetricasDiaPage() {
  return <DecisionScreen {...reportsScreenContract} currentPath="/metricas-dia" />;
}
