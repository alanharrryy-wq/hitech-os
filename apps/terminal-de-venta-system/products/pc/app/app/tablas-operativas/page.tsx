import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcDataQuality } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function OperationalTablesPage() {
  const model = await getPcDataQuality();
  return <PcCommandCenterPage model={{ ...model, currentPath: "/tablas-operativas", title: "Tablas operativas", description: "Tablas reales de calidad, consistencia y señales de operación; no una maqueta genérica." }} />;
}
