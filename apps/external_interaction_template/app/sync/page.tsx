import { SyncCenter } from "@components/sync/sync-center";
import { listSyncCenterData } from "@/lib/services/actions";

export const dynamic = "force-dynamic";

export default async function SyncPage() {
  const data = await listSyncCenterData();

  return <SyncCenter jobs={data.jobs} events={data.events} />;
}
