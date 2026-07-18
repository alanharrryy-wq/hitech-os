import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSyncCommandCenter } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

export default async function OperationalSyncPage({ searchParams }: { searchParams?: SearchParams | Promise<SearchParams> }) {
  const model = await getPcSyncCommandCenter(searchParams ? await searchParams : undefined);

  return (
    <PcCommandCenterPage
      model={{
        ...model,
        currentPath: "/sync-operativo",
        title: "Sincronización operativa",
        description: "Eventos, entregas, conflictos y confirmaciones que requieren seguimiento."
      }}
    />
  );
}
