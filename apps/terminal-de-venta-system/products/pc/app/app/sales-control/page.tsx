import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSalesControl } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function SalesControlPage() {
  const model = await getPcSalesControl();
  return <PcCommandCenterPage model={model} />;
}
