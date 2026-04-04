import { PageLoading } from "@components/ui/page-loading";

export default function SyncLoading() {
  return <PageLoading title="Loading sync center" subtitle="Assembling dispatch jobs, event telemetry and recovery controls." variant="split" />;
}
