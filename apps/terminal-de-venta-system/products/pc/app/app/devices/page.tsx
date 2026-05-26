import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcDeviceFleet } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function DevicesPage() {
  const model = await getPcDeviceFleet();
  return <PcCommandCenterPage model={model} />;
}
