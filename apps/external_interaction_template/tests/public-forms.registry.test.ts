import { describe, expect, it } from "vitest";

import {
  getPublicFormRegistration,
  listPublicFormRegistrations,
  validatePublicFormOperation
} from "@/lib/integrations/public-forms";

describe("public form registry governance", () => {
  it("registers multiple explicit public form modules", () => {
    const registrations = listPublicFormRegistrations();
    const formTypeIds = registrations.map((entry) => entry.formTypeId);

    expect(formTypeIds).toContain("service_request_public");
    expect(formTypeIds).toContain("approval_packet_public");
  });

  it("enforces schema and step boundaries when x-form-type is provided", () => {
    expect(() =>
      validatePublicFormOperation({
        formTypeId: "service_request_public",
        schemaId: "service_request",
        stepId: "requester",
        capability: "create"
      })
    ).not.toThrow();

    expect(() =>
      validatePublicFormOperation({
        formTypeId: "service_request_public",
        schemaId: "approval_packet",
        stepId: "requester",
        capability: "create"
      })
    ).toThrow("bound to schema");

    expect(() =>
      validatePublicFormOperation({
        formTypeId: "approval_packet_public",
        schemaId: "approval_packet",
        capability: "attachments"
      })
    ).toThrow("does not allow attachments");
  });

  it("provides deterministic lookup for registered form types", () => {
    const service = getPublicFormRegistration("service_request_public");
    expect(service.schemaId).toBe("service_request");
    expect(service.updateStepIds).toContain("context");
  });
});

