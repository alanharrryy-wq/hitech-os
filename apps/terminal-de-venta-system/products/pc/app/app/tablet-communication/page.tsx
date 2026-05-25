import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcTabletCommunication } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function PcTabletCommunicationPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const params = searchParams ? await searchParams : undefined;
  const model = await getPcTabletCommunication(params);
  return <PcCommandCenterPage model={model} />;
}
