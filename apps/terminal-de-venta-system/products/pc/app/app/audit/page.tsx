import { ModuleOverviewPage } from "@components/backoffice/module-overview-page";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const dynamic = "force-dynamic";

export default async function AuditPage() {
  const overview = await getBackofficeModuleOverview("audit");
  return <ModuleOverviewPage overview={overview} />;
}
