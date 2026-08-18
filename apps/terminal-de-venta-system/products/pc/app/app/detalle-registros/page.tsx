import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcDataQuality } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function RecordDetailPage() {
  const model = await getPcDataQuality();
  return <PcCommandCenterPage model={{ ...model, currentPath: "/detalle-registros", title: "Detalle de registros", description: "Detalle sustentado por lecturas reales de calidad y consistencia de datos." }} />;
}
