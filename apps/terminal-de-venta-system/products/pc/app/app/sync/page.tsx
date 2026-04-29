import { IngestEventPanel } from "@components/backoffice/ingest-event-panel";
import { ModuleOverviewPage } from "@components/backoffice/module-overview-page";
import { getBackofficeModuleOverview } from "@/lib/backoffice/overview";

export const dynamic = "force-dynamic";

export default async function SyncPage() {
  const overview = await getBackofficeModuleOverview("sync");
  return (
    <ModuleOverviewPage overview={overview}>
      <IngestEventPanel />
    </ModuleOverviewPage>
  );
}
