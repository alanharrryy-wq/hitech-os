import { randomUUID } from "crypto";

import {
  type Attachment,
  type DispatchJob,
  type ExternalRecord,
  type RecordFilter,
  type Submission,
  type SyncEvent
} from "@/lib/core/types";
import {
  type CreateDispatchJobInput,
  type CreateRecordInput,
  type CreateSubmissionInput,
  type CreateSyncEventInput,
  type ExternalStore,
  type UpdateDispatchJobInput,
  type UpdateRecordInput
} from "@/lib/store/types";

function now(): Date {
  return new Date();
}

export class MemoryExternalStore implements ExternalStore {
  private records = new Map<string, ExternalRecord>();
  private submissions = new Map<string, Submission[]>();
  private attachments = new Map<string, Attachment[]>();
  private dispatchJobs = new Map<string, DispatchJob>();
  private syncEvents: SyncEvent[] = [];
  private recordTypes = new Map<string, { title: string; summary: string; category: string; config: unknown }>();

  async ensureRecordType(schemaId: string, title: string, summary: string, category: string, config: unknown): Promise<void> {
    this.recordTypes.set(schemaId, { title, summary, category, config });
  }

  async createRecord(input: CreateRecordInput): Promise<ExternalRecord> {
    const created = now();
    const record: ExternalRecord = {
      id: randomUUID(),
      recordTypeId: input.schemaId,
      state: input.state ?? "draft",
      title: input.title,
      secureToken: input.secureToken,
      fields: { ...input.fields },
      actorId: input.actor.actorId,
      createdAt: created,
      updatedAt: created
    };

    this.records.set(record.id, record);
    return { ...record };
  }

  async getRecordById(recordId: string): Promise<ExternalRecord | null> {
    const record = this.records.get(recordId);
    return record ? { ...record, fields: { ...record.fields } } : null;
  }

  async getRecordByToken(token: string): Promise<ExternalRecord | null> {
    const record = Array.from(this.records.values()).find((entry) => entry.secureToken === token);
    return record ? { ...record, fields: { ...record.fields } } : null;
  }

  async listRecords(filter?: RecordFilter): Promise<ExternalRecord[]> {
    const query = filter?.query?.toLowerCase().trim();
    return Array.from(this.records.values())
      .filter((record) => {
        if (filter?.schemaId && record.recordTypeId !== filter.schemaId) return false;
        if (filter?.state && record.state !== filter.state) return false;
        if (query) {
          const blob = JSON.stringify(record.fields).toLowerCase();
          if (!record.title.toLowerCase().includes(query) && !blob.includes(query)) {
            return false;
          }
        }
        return true;
      })
      .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
      .map((record) => ({ ...record, fields: { ...record.fields } }));
  }

  async updateRecord(input: UpdateRecordInput): Promise<ExternalRecord> {
    const current = this.records.get(input.recordId);
    if (!current) {
      throw new Error(`Record '${input.recordId}' not found`);
    }

    const updated: ExternalRecord = {
      ...current,
      state: input.state ?? current.state,
      fields: {
        ...current.fields,
        ...input.fields
      },
      updatedAt: now(),
      submittedAt: input.state === "submitted" ? now() : current.submittedAt
    };

    this.records.set(updated.id, updated);
    return { ...updated, fields: { ...updated.fields } };
  }

  async setRecordState(recordId: string, state: ExternalRecord["state"]): Promise<ExternalRecord> {
    const current = this.records.get(recordId);
    if (!current) {
      throw new Error(`Record '${recordId}' not found`);
    }

    const updated: ExternalRecord = {
      ...current,
      state,
      updatedAt: now(),
      submittedAt: state === "submitted" ? now() : current.submittedAt,
      lastSyncAt: state === "synced" ? now() : current.lastSyncAt
    };

    this.records.set(recordId, updated);
    return { ...updated, fields: { ...updated.fields } };
  }

  async createSubmission(input: CreateSubmissionInput): Promise<Submission> {
    const submission: Submission = {
      id: randomUUID(),
      recordId: input.recordId,
      actorId: input.actor.actorId,
      stepId: input.stepId,
      payload: { ...input.payload },
      createdAt: now()
    };
    const current = this.submissions.get(input.recordId) ?? [];
    current.push(submission);
    this.submissions.set(input.recordId, current);
    return { ...submission, payload: { ...submission.payload } };
  }

  async listSubmissions(recordId: string): Promise<Submission[]> {
    return (this.submissions.get(recordId) ?? []).map((entry) => ({ ...entry, payload: { ...entry.payload } }));
  }

  async addAttachment(recordId: string, attachment: { name: string; mimeType?: string; size?: number; storageKey?: string }): Promise<Attachment> {
    const entity: Attachment = {
      id: randomUUID(),
      recordId,
      name: attachment.name,
      mimeType: attachment.mimeType,
      size: attachment.size,
      storageKey: attachment.storageKey,
      createdAt: now()
    };

    const current = this.attachments.get(recordId) ?? [];
    current.push(entity);
    this.attachments.set(recordId, current);
    return { ...entity };
  }

  async listAttachments(recordId: string): Promise<Attachment[]> {
    return (this.attachments.get(recordId) ?? []).map((entry) => ({ ...entry }));
  }

  async createDispatchJob(input: CreateDispatchJobInput): Promise<DispatchJob> {
    const entity: DispatchJob = {
      id: randomUUID(),
      recordId: input.recordId,
      adapterId: input.adapterId,
      status: "pending",
      payload: { ...input.payload },
      attempts: 0,
      createdAt: now(),
      updatedAt: now()
    };
    this.dispatchJobs.set(entity.id, entity);
    return { ...entity, payload: { ...entity.payload } };
  }

  async updateDispatchJob(input: UpdateDispatchJobInput): Promise<DispatchJob> {
    const job = this.dispatchJobs.get(input.jobId);
    if (!job) {
      throw new Error(`Dispatch job '${input.jobId}' not found`);
    }

    const updated: DispatchJob = {
      ...job,
      status: input.status,
      response: input.response,
      error: input.error,
      attempts: input.attempts,
      updatedAt: now()
    };

    this.dispatchJobs.set(updated.id, updated);
    return { ...updated, payload: { ...updated.payload }, response: updated.response ? { ...updated.response } : undefined };
  }

  async getDispatchJob(jobId: string): Promise<DispatchJob | null> {
    const job = this.dispatchJobs.get(jobId);
    return job
      ? {
          ...job,
          payload: { ...job.payload },
          response: job.response ? { ...job.response } : undefined
        }
      : null;
  }

  async listDispatchJobs(recordId?: string): Promise<DispatchJob[]> {
    return Array.from(this.dispatchJobs.values())
      .filter((job) => (recordId ? job.recordId === recordId : true))
      .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
      .map((entry) => ({
        ...entry,
        payload: { ...entry.payload },
        response: entry.response ? { ...entry.response } : undefined
      }));
  }

  async createSyncEvent(input: CreateSyncEventInput): Promise<SyncEvent> {
    const event: SyncEvent = {
      id: randomUUID(),
      recordId: input.recordId,
      direction: input.direction,
      adapterId: input.adapterId,
      status: input.status,
      summary: input.summary,
      payload: input.payload,
      error: input.error,
      createdAt: now()
    };

    this.syncEvents.push(event);
    return { ...event, payload: event.payload ? { ...event.payload } : undefined };
  }

  async listSyncEvents(recordId?: string): Promise<SyncEvent[]> {
    return this.syncEvents
      .filter((event) => (recordId ? event.recordId === recordId : true))
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .map((event) => ({ ...event, payload: event.payload ? { ...event.payload } : undefined }));
  }
}
