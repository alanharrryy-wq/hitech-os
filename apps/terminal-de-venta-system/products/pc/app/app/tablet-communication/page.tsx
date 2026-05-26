import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcTabletCommunication } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function TabletCommunicationPage() {
  const model = await getPcTabletCommunication();
  return <PcCommandCenterPage model={model} />;
}
