import { persistSyncIngestPayload } from "@/server/services/sync-ingest.service";
import type { IngestClassification } from "./event-contract";

export async function persistIngestPayload(input: unknown): Promise<IngestClassification> {
  return persistSyncIngestPayload(input) as Promise<IngestClassification>;
}
