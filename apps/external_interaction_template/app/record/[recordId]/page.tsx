import { notFound } from "next/navigation";

import { RecordDetail } from "@components/records/record-detail";
import { getSchema } from "@/lib/core/schema-registry";
import { getRecordById, listRecordSubresources } from "@/lib/services/records";

export const dynamic = "force-dynamic";

interface RecordPageProps {
  params: Promise<{ recordId: string }>;
}

export default async function RecordPage({ params }: RecordPageProps) {
  const { recordId } = await params;
  const record = await getRecordById(recordId);
  if (!record) {
    notFound();
  }

  const schema = getSchema(record.recordTypeId);
  const details = await listRecordSubresources(recordId);

  return (
    <RecordDetail
      record={record}
      schema={schema}
      submissions={details.submissions}
      attachments={details.attachments}
      dispatchJobs={details.dispatchJobs}
      syncEvents={details.syncEvents}
    />
  );
}
