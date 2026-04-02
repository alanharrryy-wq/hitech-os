import { describe, expect, it, beforeEach } from "vitest";

import { getSchema, listSchemas } from "@/lib/core/schema-registry";
import { recordPreviewFields } from "@/lib/core/record-view";
import { isActionAvailable } from "@/lib/core/state";
import { validateStepPayload } from "@/lib/core/validation";
import { isFieldVisible } from "@/lib/core/visibility";
import { applyRecordAction, listSyncCenterData } from "@/lib/services/actions";
import { resetBootstrapFlagForTests } from "@/lib/services/bootstrap";
import { createRecord, getRecordByToken, listRecords, updateRecord } from "@/lib/services/records";
import { MemoryExternalStore } from "@/lib/store/memory-store";
import { setExternalStoreForTests } from "@/lib/store";

const actor = {
  role: "operator" as const,
  actorId: "tester"
};

describe("external interaction template core", () => {
  beforeEach(() => {
    setExternalStoreForTests(new MemoryExternalStore());
    resetBootstrapFlagForTests();
  });

  it("renders schema-driven step definitions", () => {
    const schemas = listSchemas();
    expect(schemas.length).toBeGreaterThanOrEqual(3);
    const service = getSchema("service_request");
    expect(service.flow.steps.length).toBeGreaterThan(1);
    expect(service.fields.some((field) => field.id === "request_title")).toBe(true);
  });

  it("validates required fields", () => {
    const schema = getSchema("service_request");
    const result = validateStepPayload(schema, "requester", {
      request_title: "",
      requester_name: "x"
    });
    expect(result.ok).toBe(false);
  });

  it("evaluates conditional field visibility", () => {
    const schema = getSchema("service_request");
    const attachmentField = schema.fields.find((field) => field.id === "attachments");
    expect(attachmentField).toBeTruthy();
    expect(isFieldVisible(attachmentField!, { needs_attachment: false }, "external_user")).toBe(false);
    expect(isFieldVisible(attachmentField!, { needs_attachment: true }, "external_user")).toBe(true);
  });

  it("creates and submits records", async () => {
    const record = await createRecord({
      schemaId: "service_request",
      actor,
      fields: {
        request_title: "A",
        request_description: "B",
        request_priority: "high",
        requester_name: "Kai",
        requester_email: "kai@example.com"
      },
      stepId: "requester",
      submit: true
    });

    expect(record.state).toBe("submitted");
    const records = await listRecords({ schemaId: "service_request" });
    expect(records.length).toBe(1);
  });

  it("resumes and updates records via token lookup", async () => {
    const record = await createRecord({
      schemaId: "approval_packet",
      actor,
      fields: {
        packet_title: "Packet",
        packet_owner: "Alex",
        packet_scope: "Scope text",
        packet_due_date: "2026-05-01"
      },
      stepId: "packet",
      submit: false
    });

    const found = await getRecordByToken(record.secureToken);
    expect(found?.id).toBe(record.id);

    const updated = await updateRecord({
      recordId: record.id,
      actor,
      stepId: "decision",
      fields: {
        risk_level: "high",
        compliance_reviewed: true
      },
      state: "submitted"
    });

    expect(updated.state).toBe("submitted");
    expect(updated.fields.risk_level).toBe("high");
  });

  it("builds preview rows for review surfaces", async () => {
    const record = await createRecord({
      schemaId: "inspection_checklist",
      actor,
      fields: {
        site_name: "north",
        inspector: "liam",
        inspection_date: "2026-05-12",
        inspection_type: "routine"
      },
      stepId: "meta"
    });

    const preview = recordPreviewFields(record);
    expect(preview.length).toBeGreaterThan(0);
  });

  it("computes action availability by state and role", () => {
    const schema = getSchema("approval_packet");
    const approve = schema.actions.find((action) => action.id === "approve");
    expect(approve).toBeTruthy();
    expect(isActionAvailable("in_review", approve!, { role: "approver" })).toBe(true);
    expect(isActionAvailable("approved", approve!, { role: "approver" })).toBe(false);
  });

  it("executes outbound dispatch with success using local adapter", async () => {
    const record = await createRecord({
      schemaId: "inspection_checklist",
      actor,
      fields: {
        site_name: "north",
        inspector: "liam",
        inspection_date: "2026-05-12",
        inspection_type: "routine"
      },
      stepId: "meta",
      submit: true
    });

    await updateRecord({
      recordId: record.id,
      actor,
      stepId: "checks",
      fields: {
        condition_score: 80,
        requires_follow_up: false
      },
      state: "in_review"
    });

    const result = await applyRecordAction({
      recordId: record.id,
      actionId: "dispatch",
      actor
    });

    expect(result.response.ok).toBe(true);
  });

  it("records retryable sync status when outbound adapter fails", async () => {
    const record = await createRecord({
      schemaId: "service_request",
      actor,
      fields: {
        request_title: "A",
        request_description: "B",
        request_priority: "high",
        requester_name: "Kai",
        requester_email: "kai@example.com"
      },
      stepId: "requester",
      submit: true
    });

    await updateRecord({
      recordId: record.id,
      actor,
      stepId: "context",
      fields: {
        region: "north",
        needs_attachment: false
      },
      state: "in_review"
    });

    await applyRecordAction({ recordId: record.id, actionId: "approve", actor });
    await applyRecordAction({ recordId: record.id, actionId: "dispatch", actor });

    const syncData = await listSyncCenterData();
    expect(syncData.events.some((event) => event.status === "retryable")).toBe(true);
  });

  it("switches across schema examples without changing architecture", async () => {
    for (const schema of listSchemas()) {
      const firstStep = schema.flow.steps[0];
      if (!firstStep) continue;
      const fields: Record<string, unknown> = {};
      for (const fieldId of firstStep.fieldIds) {
        const definition = schema.fields.find((entry) => entry.id === fieldId);
        if (!definition) continue;
        if (definition.kind === "checkbox") fields[fieldId] = false;
        else if (definition.kind === "number") fields[fieldId] = 1;
        else if (definition.kind === "select") fields[fieldId] = definition.options?.[0] ?? "";
        else fields[fieldId] = "seed";
      }

      const record = await createRecord({
        schemaId: schema.id,
        actor,
        fields,
        stepId: firstStep.id
      });
      expect(record.recordTypeId).toBe(schema.id);
    }
  });
});
