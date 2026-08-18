import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcDataQuality } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function OperationalStatesPage() {
  const model = await getPcDataQuality();
  return <PcCommandCenterPage model={{ ...model, currentPath: "/estados-operativos", title: "Estados operativos", description: "Estados derivados de datos reales y diagnósticos disponibles, sin valores escritos a mano." }} />;
}
