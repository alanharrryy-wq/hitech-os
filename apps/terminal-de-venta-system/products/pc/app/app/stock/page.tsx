import { ModuleOverviewPage } from "@components/backoffice/module-overview-page";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const dynamic = "force-dynamic";

export default async function StockPage() {
  return <ModuleOverviewPage overview={await getBackofficeModuleOverview("stock")} />;
}
