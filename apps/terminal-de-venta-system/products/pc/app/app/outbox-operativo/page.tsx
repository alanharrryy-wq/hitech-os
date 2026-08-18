import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSyncCommandCenter } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

export default async function OutboxOperationalPage({ searchParams }: { searchParams?: SearchParams | Promise<SearchParams> }) {
  const model = await getPcSyncCommandCenter(searchParams ? await searchParams : undefined);
  return (
    <PcCommandCenterPage
      model={{
        ...model,
        currentPath: "/outbox-operativo",
        kicker: "cola operativa",
        title: "Outbox operativo",
        description: "Eventos, intentos, conflictos y pendientes reales de sincronización."
      }}
    />
  );
}
