import { RecordInbox } from "@components/records/record-inbox";
import { listSchemas } from "@/lib/core/schema-registry";
import { listRecords } from "@/lib/services/records";

export const dynamic = "force-dynamic";

interface InboxPageProps {
  searchParams: Promise<{ schemaId?: string }>;
}

export default async function InboxPage({ searchParams }: InboxPageProps) {
  const query = await searchParams;
  const [schemas, records] = await Promise.all([
    Promise.resolve(listSchemas()),
    listRecords({ schemaId: query.schemaId })
  ]);

  return <RecordInbox records={records} schemas={schemas} />;
}
