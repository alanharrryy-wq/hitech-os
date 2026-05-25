import { DecisionScreen } from "@components/uiux/decision-screen";
import { reportsScreenContract } from "@/uiux/reports-screen-contract";

export const dynamic = "force-dynamic";

export default async function ExportablesPage() {
  return <DecisionScreen {...reportsScreenContract} currentPath="/exportables" />;
}
