import { PageLoading } from "@components/ui/page-loading";

export default function SyncLoading() {
  return <PageLoading titleKey="loading.sync.title" subtitleKey="loading.sync.subtitle" variant="split" />;
}
