import {
  type ActorContext,
  type Attachment,
  type AttachmentInput,
  type DispatchJob,
  type DispatchStatus,
  type ExternalRecord,
  type RecordFilter,
  type RecordState,
  type Submission,
  type SyncEvent,
  type SyncStatus
} from "@/lib/core/types";

export interface CreateRecordInput {
  schemaId: string;
  title: string;
  actor: ActorContext;
  fields: Record<string, unknown>;
  secureToken: string;
  state?: RecordState;
}

export interface UpdateRecordInput {
  recordId: string;
  actor: ActorContext;
  fields: Record<string, unknown>;
  state?: RecordState;
}

export interface CreateSubmissionInput {
  recordId: string;
  actor: ActorContext;
  stepId?: string;
  payload: Record<string, unknown>;
}

export interface CreateDispatchJobInput {
  recordId: string;
  adapterId: string;
  payload: Record<string, unknown>;
}

export interface UpdateDispatchJobInput {
  jobId: string;
  status: DispatchStatus;
  response?: Record<string, unknown>;
  error?: string;
  attempts: number;
}

export interface CreateSyncEventInput {
  recordId: string;
  direction: "inbound" | "outbound";
  adapterId: string;
  status: SyncStatus;
  summary: string;
  payload?: Record<string, unknown>;
  error?: string;
}

export interface ExternalStore {
  ensureRecordType(schemaId: string, title: string, summary: string, category: string, config: unknown): Promise<void>;
  createRecord(input: CreateRecordInput): Promise<ExternalRecord>;
  getRecordById(recordId: string): Promise<ExternalRecord | null>;
  getRecordByToken(token: string): Promise<ExternalRecord | null>;
  listRecords(filter?: RecordFilter): Promise<ExternalRecord[]>;
  updateRecord(input: UpdateRecordInput): Promise<ExternalRecord>;
  setRecordState(recordId: string, state: RecordState): Promise<ExternalRecord>;
  createSubmission(input: CreateSubmissionInput): Promise<Submission>;
  listSubmissions(recordId: string): Promise<Submission[]>;
  addAttachment(recordId: string, attachment: AttachmentInput): Promise<Attachment>;
  listAttachments(recordId: string): Promise<Attachment[]>;
  createDispatchJob(input: CreateDispatchJobInput): Promise<DispatchJob>;
  updateDispatchJob(input: UpdateDispatchJobInput): Promise<DispatchJob>;
  getDispatchJob(jobId: string): Promise<DispatchJob | null>;
  listDispatchJobs(recordId?: string): Promise<DispatchJob[]>;
  createSyncEvent(input: CreateSyncEventInput): Promise<SyncEvent>;
  listSyncEvents(recordId?: string): Promise<SyncEvent[]>;
}
