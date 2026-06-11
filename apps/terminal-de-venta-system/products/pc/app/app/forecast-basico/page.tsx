import { DecisionScreen } from "@components/uiux/decision-screen";
import { getPurchasingScreenContract } from "@/uiux/purchasing-screen-contract";

export const dynamic = "force-dynamic";

const CURRENT_PATH = "/forecast-basico";

export default async function BasicForecastPage() {
  return <DecisionScreen {...getPurchasingScreenContract(CURRENT_PATH)} currentPath={CURRENT_PATH} />;
}
