import { DecisionScreen } from "@components/uiux/decision-screen";
import { reportsScreenContract } from "@/uiux/reports-screen-contract";

export const dynamic = "force-dynamic";

export default async function ContratosReportePage() {
  return <DecisionScreen {...reportsScreenContract} currentPath="/contratos-reporte" />;
}
