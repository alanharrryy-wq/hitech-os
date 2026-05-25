import { DecisionScreen } from "@components/uiux/decision-screen";
import { systemScreenContract } from "@/uiux/system-screen-contract";

export const dynamic = "force-dynamic";

export default async function ReferenciaVisualPage() {
  return <DecisionScreen {...systemScreenContract} currentPath="/referencia-visual" />;
}
