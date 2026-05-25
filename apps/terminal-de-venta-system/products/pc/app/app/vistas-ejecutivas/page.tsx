import { DecisionScreen } from "@components/uiux/decision-screen";
import { reportsScreenContract } from "@/uiux/reports-screen-contract";

export const dynamic = "force-dynamic";

export default async function VistasEjecutivasPage() {
  return <DecisionScreen {...reportsScreenContract} currentPath="/vistas-ejecutivas" />;
}
