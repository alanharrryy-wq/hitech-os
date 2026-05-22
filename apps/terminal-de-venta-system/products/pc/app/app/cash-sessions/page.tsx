import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcCashSessions } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function PcCashSessionsPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const params = searchParams ? await searchParams : undefined;
  const model = await getPcCashSessions(params);
  return <PcCommandCenterPage model={model} />;
}
