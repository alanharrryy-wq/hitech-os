import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSyncCommandCenter } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function SyncPage() {
  const model = await getPcSyncCommandCenter();
  return <PcCommandCenterPage model={model} />;
}
