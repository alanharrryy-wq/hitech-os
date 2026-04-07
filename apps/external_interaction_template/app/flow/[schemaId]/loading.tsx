import { PageLoading } from "@components/ui/page-loading";

export default function FlowLoading() {
  return <PageLoading title="Preparing flow runner" subtitle="Resolving schema, resume token context and step shell." variant="flow" />;
}
