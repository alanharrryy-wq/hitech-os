import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcLicenseRuntimeControl } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function PcLicenseRuntimePage() {
  const model = await getPcLicenseRuntimeControl();
  return <PcCommandCenterPage model={model} />;
}
