import { SyncReleaseWorkspace } from "@components/sync/sync-release-workspace";
import { getSyncReleaseWorkspace } from "@/server/services/sync-release.service";

export const dynamic = "force-dynamic";

export default async function SyncPage() {
  const workspace = await getSyncReleaseWorkspace();
  return <SyncReleaseWorkspace workspace={workspace} />;
}
