import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcDeviceFleet } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

export default async function DevicesPage({ searchParams }: { searchParams?: SearchParams | Promise<SearchParams> }) {
  const model = await getPcDeviceFleet(searchParams ? await searchParams : undefined);
  return <PcCommandCenterPage model={model} />;
}
