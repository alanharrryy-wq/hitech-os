import { SyncReleaseWorkspace } from "../../components/sync/sync-release-workspace";
import { getTriDbStatusCard } from "../../src/server/services/tri-db-status.service";

export const dynamic = "force-dynamic";

export default async function SyncPage() {
  const triDbStatus = await getTriDbStatusCard();
  return <SyncReleaseWorkspace triDbStatus={triDbStatus} />;
}
