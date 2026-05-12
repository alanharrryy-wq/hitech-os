import {
  REQUIRED_SYNC_EVENT_FIELDS,
  RECOGNIZED_SYNC_TOPICS,
  SUPPORTED_SYNC_SCHEMA_VERSIONS,
  classifySyncIngestPayload,
  extractSyncEvents,
  validateSyncEventEnvelope,
  type SyncEventEnvelope,
  type SyncIngestClassification,
  type SyncIngestResult,
  type SyncEventStatus
} from "@/server/validators/sync-event-contract";

export const REQUIRED_EVENT_FIELDS = REQUIRED_SYNC_EVENT_FIELDS;
export const RECOGNIZED_EVENT_TOPICS = RECOGNIZED_SYNC_TOPICS;
export const SUPPORTED_SCHEMA_VERSIONS = SUPPORTED_SYNC_SCHEMA_VERSIONS;

export type RecognizedEventTopic = (typeof RECOGNIZED_EVENT_TOPICS)[number];
export type IngestResultStatus = SyncEventStatus;
export type BackofficeEventEnvelope = SyncEventEnvelope & { topic: RecognizedEventTopic };
export type IngestEventResult = SyncIngestResult;
export type IngestClassification = SyncIngestClassification;

export function extractIngestEvents(input: unknown): unknown[] {
  return extractSyncEvents(input);
}

export function validateBackofficeEvent(input: unknown) {
  return validateSyncEventEnvelope(input);
}

export function classifyIngestPayload(input: unknown): IngestClassification {
  return classifySyncIngestPayload(input);
}
