import { DecisionScreen } from "@components/uiux/decision-screen";
import { syncScreenContract } from "@/uiux/sync-screen-contract";

export const dynamic = "force-dynamic";

export default async function TabletCommunicationPage() {
  return <DecisionScreen {...syncScreenContract} currentPath="/tablet-communication" />;
}
