import { PageLoading } from "@components/ui/page-loading";

export default function InboxLoading() {
  return <PageLoading titleKey="loading.inbox.title" subtitleKey="loading.inbox.subtitle" variant="list" />;
}
