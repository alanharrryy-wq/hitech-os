import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcDataQuality } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function DataQualityPage() {
  const model = await getPcDataQuality();
  return <PcCommandCenterPage model={model} />;
}
