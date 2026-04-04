import { getAdapter } from "@/lib/adapters";
import { getSchema } from "@/lib/core/schema-registry";
import { ensureActionAvailable, canTransition } from "@/lib/core/state";
import { type ActorContext } from "@/lib/core/types";
import { ensureTemplateBootstrap } from "@/lib/services/bootstrap";
import { getExternalStore } from "@/lib/store";

export interface ApplyActionRequest {
  recordId: string;
  actionId: string;
  actor: ActorContext;
  note?: string;
  payload?: Record<string, unknown>;
}

export async function applyRecordAction(request: ApplyActionRequest) {
  await ensureTemplateBootstrap();

  const store = getExternalStore();
  const record = await store.getRecordById(request.recordId);
  if (!record) {
    throw new Error(`Record '${request.recordId}' not found`);
  }

  const schema = getSchema(record.recordTypeId);
  const action = schema.actions.find((entry) => entry.id === request.actionId);
  if (!action) {
    throw new Error(`Action '${request.actionId}' is not defined in schema '${schema.id}'`);
  }

  ensureActionAvailable(record, action, request.actor);

  if (action.requiresComment && !request.note) {
    throw new Error(`Action '${action.id}' requires a note`);
  }

  if (action.kind === "dispatch") {
    const adapter = getAdapter(action.adapterId ?? schema.adapterBindings.outbound);
    const job = await store.createDispatchJob({
      recordId: record.id,
      adapterId: adapter.id,
      payload: request.payload ?? {}
    });

    await store.updateDispatchJob({
      jobId: job.id,
      status: "running",
      attempts: job.attempts + 1
    });

    const response = await adapter.dispatch({
      record,
      schema,
      action,
      payload: request.payload ?? {}
    });

    const status = response.ok ? "succeeded" : "failed";
    const updatedJob = await store.updateDispatchJob({
      jobId: job.id,
      status,
      attempts: job.attempts + 1,
      response: response.responsePayload,
      error: response.error
    });

    const targetState = response.ok ? action.nextState ?? "dispatched" : "failed";
    if (!canTransition(record.state, targetState)) {
      throw new Error(`Invalid transition from '${record.state}' to '${targetState}'`);
    }

    let updatedRecord = await store.setRecordState(record.id, targetState);
    await store.createSubmission({
      recordId: record.id,
      actor: request.actor,
      payload: {
        action: action.id,
        note: request.note,
        adapter: adapter.id,
        ok: response.ok
      }
    });

    await store.createSyncEvent({
      recordId: record.id,
      direction: "outbound",
      adapterId: adapter.id,
      status: response.ok ? "synced" : "retryable",
      summary: response.summary,
      payload: response.responsePayload,
      error: response.error
    });

    if (response.ok && updatedRecord.state !== "synced") {
      if (!canTransition(updatedRecord.state, "synced")) {
        throw new Error(`Invalid transition from '${updatedRecord.state}' to 'synced'`);
      }
      updatedRecord = await store.setRecordState(record.id, "synced");
    }

    return {
      record: updatedRecord,
      dispatchJob: updatedJob,
      response
    };
  }

  const nextState = action.nextState;
  let updatedRecord = record;
  if (nextState) {
    if (!canTransition(record.state, nextState)) {
      throw new Error(`Invalid transition from '${record.state}' to '${nextState}'`);
    }
    updatedRecord = await store.setRecordState(record.id, nextState);
  }

  await store.createSubmission({
    recordId: record.id,
    actor: request.actor,
    payload: {
      action: action.id,
      note: request.note,
      payload: request.payload ?? {}
    }
  });

  await store.createSyncEvent({
    recordId: record.id,
    direction: "outbound",
    adapterId: action.adapterId ?? schema.adapterBindings.outbound,
    status: "pending",
    summary: `Action '${action.label}' executed`,
    payload: {
      action: action.id,
      note: request.note
    }
  });

  return {
    record: updatedRecord,
    response: {
      ok: true,
      summary: `Action '${action.label}' applied`
    }
  };
}

export async function retryDispatchJob(jobId: string, actor: ActorContext) {
  await ensureTemplateBootstrap();
  const store = getExternalStore();
  const job = await store.getDispatchJob(jobId);
  if (!job) {
    throw new Error(`Dispatch job '${jobId}' not found`);
  }

  const record = await store.getRecordById(job.recordId);
  if (!record) {
    throw new Error(`Record '${job.recordId}' not found`);
  }

  const schema = getSchema(record.recordTypeId);
  const action = schema.actions.find((entry) => entry.kind === "dispatch");
  if (!action) {
    throw new Error(`No dispatch action configured for schema '${schema.id}'`);
  }

  const adapter = getAdapter(job.adapterId);

  await store.updateDispatchJob({
    jobId: job.id,
    status: "running",
    attempts: job.attempts + 1
  });

  const response = await adapter.dispatch({
    record,
    schema,
    action,
    payload: job.payload
  });

  const status = response.ok ? "succeeded" : "failed";
  const updatedJob = await store.updateDispatchJob({
    jobId: job.id,
    status,
    attempts: job.attempts + 1,
    response: response.responsePayload,
    error: response.error
  });

  let updatedRecord = record;
  if (response.ok) {
    const dispatchState = action.nextState ?? "dispatched";
    if (updatedRecord.state !== dispatchState) {
      if (!canTransition(updatedRecord.state, dispatchState)) {
        throw new Error(`Invalid transition from '${updatedRecord.state}' to '${dispatchState}'`);
      }
      updatedRecord = await store.setRecordState(record.id, dispatchState);
    }

    if (updatedRecord.state !== "synced") {
      if (!canTransition(updatedRecord.state, "synced")) {
        throw new Error(`Invalid transition from '${updatedRecord.state}' to 'synced'`);
      }
      updatedRecord = await store.setRecordState(record.id, "synced");
    }
  } else if (updatedRecord.state !== "failed") {
    if (!canTransition(updatedRecord.state, "failed")) {
      throw new Error(`Invalid transition from '${updatedRecord.state}' to 'failed'`);
    }
    updatedRecord = await store.setRecordState(record.id, "failed");
  }

  await store.createSubmission({
    recordId: record.id,
    actor,
    payload: {
      action: "dispatch_retry",
      jobId: job.id,
      ok: response.ok,
      state: updatedRecord.state
    }
  });

  await store.createSyncEvent({
    recordId: record.id,
    direction: "outbound",
    adapterId: adapter.id,
    status: response.ok ? "synced" : "retryable",
    summary: response.ok ? response.summary : response.summary || "Retry failed",
    payload: response.responsePayload,
    error: response.error
  });

  return {
    job: updatedJob,
    record: updatedRecord,
    response
  };
}

export async function listSyncCenterData() {
  await ensureTemplateBootstrap();
  const store = getExternalStore();
  const [events, jobs] = await Promise.all([store.listSyncEvents(), store.listDispatchJobs()]);
  return { events, jobs };
}
