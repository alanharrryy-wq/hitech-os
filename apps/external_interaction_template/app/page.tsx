import { LauncherPageClient } from "@components/home/launcher-page-client";
import { listSchemas } from "@/lib/core/schema-registry";
import { listRecords } from "@/lib/services/records";
import { listSyncCenterData } from "@/lib/services/actions";

export const dynamic = "force-dynamic";

export default async function LauncherPage() {
  const schemas = listSchemas();
  const [records, syncData] = await Promise.all([listRecords(), listSyncCenterData()]);

  return <LauncherPageClient schemas={schemas} records={records} syncData={syncData} />;
}
