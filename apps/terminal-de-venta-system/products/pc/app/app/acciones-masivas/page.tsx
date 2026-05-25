import { DecisionScreen } from "@components/uiux/decision-screen";
import { systemScreenContract } from "@/uiux/system-screen-contract";

export const dynamic = "force-dynamic";

export default async function AccionesMasivasPage() {
  return <DecisionScreen {...systemScreenContract} currentPath="/acciones-masivas" />;
}
