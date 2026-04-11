import { notFound } from "next/navigation";

import { FlowPageClient } from "@components/flow/flow-page-client";
import { getSchema } from "@/lib/core/schema-registry";
import { getRecordByToken } from "@/lib/services/records";

export const dynamic = "force-dynamic";

interface FlowPageProps {
  params: Promise<{ schemaId: string }>;
  searchParams: Promise<{ token?: string; mode?: string }>;
}

export default async function FlowPage({ params, searchParams }: FlowPageProps) {
  const { schemaId } = await params;
  const query = await searchParams;

  let schema;
  try {
    schema = getSchema(schemaId);
  } catch {
    notFound();
  }

  const initialRecord = query.token ? await getRecordByToken(query.token) : null;

  return <FlowPageClient schema={schema} initialRecord={initialRecord} queryToken={query.token ?? ""} />;
}
