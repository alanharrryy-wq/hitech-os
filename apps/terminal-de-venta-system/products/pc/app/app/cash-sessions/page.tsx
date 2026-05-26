import { PcCommandCenterPage } from "@components/control/pc-command-center-page";
import { getPcCashSessions } from "@/server/services/pc-command-center.service";

export const dynamic = "force-dynamic";

export default async function CashSessionsPage() {
  const model = await getPcCashSessions();
  return <PcCommandCenterPage model={model} />;
}
