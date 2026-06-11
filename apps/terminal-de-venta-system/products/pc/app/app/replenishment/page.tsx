import { DecisionScreen } from "@components/uiux/decision-screen";
import { getPurchasingScreenContract } from "@/uiux/purchasing-screen-contract";

export const dynamic = "force-dynamic";

const CURRENT_PATH = "/replenishment";

export default async function ReplenishmentPage() {
  return <DecisionScreen {...getPurchasingScreenContract(CURRENT_PATH)} currentPath={CURRENT_PATH} />;
}
