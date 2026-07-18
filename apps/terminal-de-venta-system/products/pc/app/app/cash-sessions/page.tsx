import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcCashSessions } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

type SearchParams = Record<string, string | string[] | undefined>;

export default async function CashSessionsPage({ searchParams }: { searchParams?: SearchParams | Promise<SearchParams> }) {
  const model = await getPcCashSessions(searchParams ? await searchParams : undefined);
  return <PcCommandCenterPage model={model} />;
}
