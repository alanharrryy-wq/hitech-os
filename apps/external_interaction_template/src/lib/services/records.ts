import { getSchema } from "@/lib/core/schema-registry";
import { type ActorContext, type ExternalRecord, type RecordFilter } from "@/lib/core/types";
import { canTransition } from "@/lib/core/state";
import { validateStepPayload } from "@/lib/core/validation";
import { randomToken } from "@/lib/utils";
import { ensureTemplateBootstrap } from "@/lib/services/bootstrap";
import { getExternalStore } from "@/lib/store";

export interface CreateRecordRequest {
  schemaId: string;
  actor: ActorContext;
  title?: string;
  fields?: Record<string, unknown>;
  stepId?: string;
  submit?: boolean;
}

export interface UpdateRecordRequest {
  recordId: string;
  actor: ActorContext;
  fields: Record<string, unknown>;
  stepId?: string;
  state?: ExternalRecord["state"];
}

export async function listRecords(filter?: RecordFilter): Promise<ExternalRecord[]> {
  await ensureTemplateBootstrap();
  return getExternalStore().listRecords(filter);
}

export async function getRecordById(recordId: string): Promise<ExternalRecord | null> {
  await ensureTemplateBootstrap();
  return getExternalStore().getRecordById(recordId);
}

export async function getRecordByToken(token: string): Promise<ExternalRecord | null> {
  await ensureTemplateBootstrap();
  return getExternalStore().getRecordByToken(token);
}

export async function createRecord(request: CreateRecordRequest): Promise<ExternalRecord> {
  await ensureTemplateBootstrap();
  const store = getExternalStore();
  const schema = getSchema(request.schemaId);

  const currentValues = request.fields ?? {};
  const stepId = request.stepId ?? schema.flow.steps[0]?.id;
  if (!stepId) {
    throw new Error(`Schema '${schema.id}' does not define any flow step`);
  }

  const validation = validateStepPayload(schema, stepId, currentValues, request.actor.role);
  if (!validation.ok) {
    throw new Error(`Validation failed: ${JSON.stringify("errors" in validation ? validation.errors : {})}`);
  }
  const primaryListField = schema.views.listFields[0] ?? schema.fields[0]?.id ?? "title";

  const recordTitle =
    request.title ??
    (typeof currentValues[primaryListField] === "string"
      ? (currentValues[primaryListField] as string)
      : `${schema.title} ${new Date().toISOString().slice(0, 10)}`);

  const state = request.submit ? "submitted" : "draft";

  const record = await store.createRecord({
    schemaId: schema.id,
    title: recordTitle,
    actor: request.actor,
    fields: currentValues,
    secureToken: randomToken("ext"),
    state
  });

  await store.createSubmission({
    recordId: record.id,
    actor: request.actor,
    stepId,
    payload: validation.data
  });

  await store.createSyncEvent({
    recordId: record.id,
    direction: "inbound",
    adapterId: schema.adapterBindings.inbound,
    status: "pending",
    summary: request.submit ? "Record submitted from external flow" : "Draft created",
    payload: validation.data
  });

  return record;
}

export async function updateRecord(request: UpdateRecordRequest): Promise<ExternalRecord> {
  await ensureTemplateBootstrap();
  const store = getExternalStore();
  const existing = await store.getRecordById(request.recordId);
  if (!existing) {
    throw new Error(`Record '${request.recordId}' not found`);
  }

  const schema = getSchema(existing.recordTypeId);
  const stepId = request.stepId ?? schema.flow.steps[0]?.id;
  if (!stepId) {
    throw new Error(`Schema '${schema.id}' does not define flow steps`);
  }

  const merged = {
    ...existing.fields,
    ...request.fields
  };

  const validation = validateStepPayload(schema, stepId, merged, request.actor.role);
  if (!validation.ok) {
    throw new Error(`Validation failed: ${JSON.stringify("errors" in validation ? validation.errors : {})}`);
  }

  if (request.state && !canTransition(existing.state, request.state)) {
    throw new Error(`Invalid transition from '${existing.state}' to '${request.state}'`);
  }

  const updated = await store.updateRecord({
    recordId: existing.id,
    actor: request.actor,
    fields: request.fields,
    state: request.state
  });

  await store.createSubmission({
    recordId: updated.id,
    actor: request.actor,
    stepId,
    payload: validation.data
  });

  await store.createSyncEvent({
    recordId: updated.id,
    direction: "inbound",
    adapterId: schema.adapterBindings.inbound,
    status: "pending",
    summary: "Record updated from external flow",
    payload: request.fields
  });

  return updated;
}

export async function addAttachmentMetadata(
  recordId: string,
  actor: ActorContext,
  attachment: { name: string; mimeType?: string; size?: number; storageKey?: string }
) {
  await ensureTemplateBootstrap();
  const store = getExternalStore();
  const record = await store.getRecordById(recordId);
  if (!record) {
    throw new Error(`Record '${recordId}' not found`);
  }

  const entity = await store.addAttachment(recordId, attachment);
  await store.createSyncEvent({
    recordId,
    direction: "inbound",
    adapterId: "local",
    status: "pending",
    summary: "Attachment metadata added",
    payload: {
      actor: actor.actorId,
      name: attachment.name
    }
  });

  return entity;
}

export async function listRecordSubresources(recordId: string) {
  await ensureTemplateBootstrap();
  const store = getExternalStore();
  const [submissions, attachments, dispatchJobs, syncEvents] = await Promise.all([
    store.listSubmissions(recordId),
    store.listAttachments(recordId),
    store.listDispatchJobs(recordId),
    store.listSyncEvents(recordId)
  ]);

  return { submissions, attachments, dispatchJobs, syncEvents };
}
