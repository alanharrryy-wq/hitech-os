import { prisma } from "@/lib/db";
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

function parseObject(value: string | null | undefined): Record<string, unknown> {
  if (!value) return {};
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function stringify(value: unknown): string {
  return JSON.stringify(value ?? {});
}

function asExternalRecord(entity: {
  id: string;
  recordType: { schemaId: string };
  state: string;
  title: string;
  secureToken: string;
  fields: string;
  actorId: string | null;
  createdAt: Date;
  updatedAt: Date;
  submittedAt: Date | null;
  lastSyncAt: Date | null;
}): ExternalRecord {
  return {
    id: entity.id,
    recordTypeId: entity.recordType.schemaId,
    state: entity.state as ExternalRecord["state"],
    title: entity.title,
    secureToken: entity.secureToken,
    fields: parseObject(entity.fields),
    actorId: entity.actorId ?? undefined,
    createdAt: entity.createdAt,
    updatedAt: entity.updatedAt,
    submittedAt: entity.submittedAt ?? undefined,
    lastSyncAt: entity.lastSyncAt ?? undefined
  };
}

function asSubmission(entity: {
  id: string;
  recordId: string;
  actorId: string | null;
  stepId: string | null;
  payload: string;
  createdAt: Date;
}): Submission {
  return {
    id: entity.id,
    recordId: entity.recordId,
    actorId: entity.actorId ?? undefined,
    stepId: entity.stepId ?? undefined,
    payload: parseObject(entity.payload),
    createdAt: entity.createdAt
  };
}

function asAttachment(entity: {
  id: string;
  recordId: string;
  name: string;
  mimeType: string | null;
  size: number | null;
  storageKey: string | null;
  createdAt: Date;
}): Attachment {
  return {
    id: entity.id,
    recordId: entity.recordId,
    name: entity.name,
    mimeType: entity.mimeType ?? undefined,
    size: entity.size ?? undefined,
    storageKey: entity.storageKey ?? undefined,
    createdAt: entity.createdAt
  };
}

function asDispatchJob(entity: {
  id: string;
  recordId: string;
  adapterId: string;
  status: string;
  payload: string;
  response: string | null;
  error: string | null;
  attempts: number;
  createdAt: Date;
  updatedAt: Date;
}): DispatchJob {
  return {
    id: entity.id,
    recordId: entity.recordId,
    adapterId: entity.adapterId,
    status: entity.status as DispatchJob["status"],
    payload: parseObject(entity.payload),
    response: entity.response ? parseObject(entity.response) : undefined,
    error: entity.error ?? undefined,
    attempts: entity.attempts,
    createdAt: entity.createdAt,
    updatedAt: entity.updatedAt
  };
}

function asSyncEvent(entity: {
  id: string;
  recordId: string;
  direction: string;
  adapterId: string;
  status: string;
  summary: string;
  payload: string | null;
  error: string | null;
  createdAt: Date;
}): SyncEvent {
  return {
    id: entity.id,
    recordId: entity.recordId,
    direction: entity.direction as SyncEvent["direction"],
    adapterId: entity.adapterId,
    status: entity.status as SyncEvent["status"],
    summary: entity.summary,
    payload: entity.payload ? parseObject(entity.payload) : undefined,
    error: entity.error ?? undefined,
    createdAt: entity.createdAt
  };
}

export class PrismaExternalStore implements ExternalStore {
  async ensureRecordType(schemaId: string, title: string, summary: string, category: string, config: unknown): Promise<void> {
    await prisma.recordType.upsert({
      where: { schemaId },
      create: {
        schemaId,
        title,
        summary,
        category,
        config: stringify(config)
      },
      update: {
        title,
        summary,
        category,
        config: stringify(config)
      }
    });
  }

  async createRecord(input: CreateRecordInput): Promise<ExternalRecord> {
    const recordType = await prisma.recordType.findUnique({ where: { schemaId: input.schemaId } });
    if (!recordType) {
      throw new Error(`Schema '${input.schemaId}' has not been registered in storage`);
    }

    const entity = await prisma.externalRecord.create({
      data: {
        recordTypeId: recordType.id,
        actorId: input.actor.actorId,
        title: input.title,
        state: input.state ?? "draft",
        fields: stringify(input.fields),
        secureToken: input.secureToken
      },
      include: {
        recordType: {
          select: {
            schemaId: true
          }
        }
      }
    });

    return asExternalRecord(entity);
  }

  async getRecordById(recordId: string): Promise<ExternalRecord | null> {
    const entity = await prisma.externalRecord.findUnique({
      where: { id: recordId },
      include: {
        recordType: {
          select: {
            schemaId: true
          }
        }
      }
    });

    return entity ? asExternalRecord(entity) : null;
  }

  async getRecordByToken(token: string): Promise<ExternalRecord | null> {
    const entity = await prisma.externalRecord.findUnique({
      where: { secureToken: token },
      include: {
        recordType: {
          select: {
            schemaId: true
          }
        }
      }
    });

    return entity ? asExternalRecord(entity) : null;
  }

  async listRecords(filter?: RecordFilter): Promise<ExternalRecord[]> {
    const entities = await prisma.externalRecord.findMany({
      where: {
        state: filter?.state,
        recordType: filter?.schemaId
          ? {
              schemaId: filter.schemaId
            }
          : undefined,
        OR: filter?.query
          ? [
              {
                title: {
                  contains: filter.query
                }
              },
              {
                fields: {
                  contains: filter.query
                }
              }
            ]
          : undefined
      },
      orderBy: {
        updatedAt: "desc"
      },
      include: {
        recordType: {
          select: {
            schemaId: true
          }
        }
      }
    });

    return entities.map(asExternalRecord);
  }

  async updateRecord(input: UpdateRecordInput): Promise<ExternalRecord> {
    const current = await this.getRecordById(input.recordId);
    if (!current) {
      throw new Error(`Record '${input.recordId}' not found`);
    }

    const mergedFields = {
      ...current.fields,
      ...input.fields
    };

    const entity = await prisma.externalRecord.update({
      where: { id: input.recordId },
      data: {
        fields: stringify(mergedFields),
        state: input.state,
        submittedAt: input.state === "submitted" ? new Date() : undefined
      },
      include: {
        recordType: {
          select: {
            schemaId: true
          }
        }
      }
    });

    return asExternalRecord(entity);
  }

  async setRecordState(recordId: string, state: ExternalRecord["state"]): Promise<ExternalRecord> {
    const entity = await prisma.externalRecord.update({
      where: { id: recordId },
      data: {
        state,
        submittedAt: state === "submitted" ? new Date() : undefined,
        lastSyncAt: state === "synced" ? new Date() : undefined
      },
      include: {
        recordType: {
          select: {
            schemaId: true
          }
        }
      }
    });

    return asExternalRecord(entity);
  }

  async createSubmission(input: CreateSubmissionInput): Promise<Submission> {
    const entity = await prisma.submission.create({
      data: {
        recordId: input.recordId,
        actorId: input.actor.actorId,
        stepId: input.stepId,
        payload: stringify(input.payload)
      }
    });

    return asSubmission(entity);
  }

  async listSubmissions(recordId: string): Promise<Submission[]> {
    const entities = await prisma.submission.findMany({ where: { recordId }, orderBy: { createdAt: "desc" } });
    return entities.map(asSubmission);
  }

  async addAttachment(
    recordId: string,
    attachment: { name: string; mimeType?: string; size?: number; storageKey?: string }
  ): Promise<Attachment> {
    const entity = await prisma.attachment.create({
      data: {
        recordId,
        name: attachment.name,
        mimeType: attachment.mimeType,
        size: attachment.size,
        storageKey: attachment.storageKey
      }
    });

    return asAttachment(entity);
  }

  async listAttachments(recordId: string): Promise<Attachment[]> {
    const entities = await prisma.attachment.findMany({ where: { recordId }, orderBy: { createdAt: "desc" } });
    return entities.map(asAttachment);
  }

  async createDispatchJob(input: CreateDispatchJobInput): Promise<DispatchJob> {
    const entity = await prisma.dispatchJob.create({
      data: {
        recordId: input.recordId,
        adapterId: input.adapterId,
        payload: stringify(input.payload),
        status: "pending"
      }
    });

    return asDispatchJob(entity);
  }

  async updateDispatchJob(input: UpdateDispatchJobInput): Promise<DispatchJob> {
    const entity = await prisma.dispatchJob.update({
      where: { id: input.jobId },
      data: {
        status: input.status,
        response: input.response ? stringify(input.response) : undefined,
        error: input.error,
        attempts: input.attempts
      }
    });

    return asDispatchJob(entity);
  }

  async getDispatchJob(jobId: string): Promise<DispatchJob | null> {
    const entity = await prisma.dispatchJob.findUnique({ where: { id: jobId } });
    return entity ? asDispatchJob(entity) : null;
  }

  async listDispatchJobs(recordId?: string): Promise<DispatchJob[]> {
    const entities = await prisma.dispatchJob.findMany({
      where: recordId ? { recordId } : undefined,
      orderBy: { updatedAt: "desc" }
    });
    return entities.map(asDispatchJob);
  }

  async createSyncEvent(input: CreateSyncEventInput): Promise<SyncEvent> {
    const entity = await prisma.syncEvent.create({
      data: {
        recordId: input.recordId,
        direction: input.direction,
        adapterId: input.adapterId,
        status: input.status,
        summary: input.summary,
        payload: input.payload ? stringify(input.payload) : undefined,
        error: input.error
      }
    });

    return asSyncEvent(entity);
  }

  async listSyncEvents(recordId?: string): Promise<SyncEvent[]> {
    const entities = await prisma.syncEvent.findMany({
      where: recordId ? { recordId } : undefined,
      orderBy: { createdAt: "desc" }
    });
    return entities.map(asSyncEvent);
  }
}
