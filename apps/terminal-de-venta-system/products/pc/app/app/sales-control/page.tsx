import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSalesControl } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

export default async function SalesControlPage({ searchParams }: { searchParams?: SearchParams | Promise<SearchParams> }) {
  const model = await getPcSalesControl(searchParams ? await searchParams : undefined);
  return <PcCommandCenterPage model={model} />;
}
