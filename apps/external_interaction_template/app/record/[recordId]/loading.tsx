import { PageLoading } from "@components/ui/page-loading";

export default function RecordLoading() {
  return <PageLoading title="Loading record detail" subtitle="Pulling activity, attachments and action rails into view." variant="detail" />;
}
