import { DecisionScreen } from "@components/uiux/decision-screen";
import { insightsScreenContract } from "@/uiux/insights-screen-contract";

export const dynamic = "force-dynamic";

export default async function PrismaInsightsPage() {
  return <DecisionScreen {...insightsScreenContract} currentPath="/prisma-insights" />;
}
