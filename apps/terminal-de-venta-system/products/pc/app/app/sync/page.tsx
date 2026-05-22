import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSyncCommandCenter } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function SyncPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const params = searchParams ? await searchParams : undefined;
  const model = await getPcSyncCommandCenter(params);
  return <PcCommandCenterPage model={model} />;
}
