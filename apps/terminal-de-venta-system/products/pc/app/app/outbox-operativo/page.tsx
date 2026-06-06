import { DecisionScreen } from "@components/uiux/decision-screen";
import { syncScreenContract } from "@/uiux/sync-screen-contract";

export const dynamic = "force-static";

export default function OutboxOperationalPage() {
  return <DecisionScreen {...syncScreenContract} currentPath="/outbox-operativo" />;
}
