import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcSalesControl } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function PcSalesControlPage({ searchParams }: { searchParams?: Promise<Record<string, string | string[] | undefined>> }) {
  const params = searchParams ? await searchParams : undefined;
  const model = await getPcSalesControl(params);
  return <PcCommandCenterPage model={model} />;
}
