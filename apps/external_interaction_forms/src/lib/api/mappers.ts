import type {
  ContextFields,
  CreateDraftRequestBody,
  Step1Input,
  Step2Input,
  SubmitFinalRequestBody,
  UpdateDraftRequestBody
} from "./types";

function compactContextFields(fields: ContextFields): ContextFields {
  const compacted: ContextFields = {
    needs_attachment: fields.needs_attachment
  };

  if (fields.required_by) {
    compacted.required_by = fields.required_by;
  }

  if (fields.region) {
    compacted.region = fields.region;
  }

  return compacted;
}

export function mapStep1ToCreateDraftPayload(step1: Step1Input): CreateDraftRequestBody {
  return {
    schemaId: "service_request",
    title: step1.request_title,
    fields: {
      request_title: step1.request_title,
      request_description: step1.request_description,
      request_priority: step1.request_priority,
      requester_name: step1.requester_name,
      requester_email: step1.requester_email
    },
    stepId: "requester",
    submit: false
  };
}

export function mapStep2ToContextFields(step2: Step2Input): ContextFields {
  return compactContextFields({
    required_by: step2.required_by || undefined,
    region: step2.region || undefined,
    needs_attachment: step2.needs_attachment
  });
}

export function mapStep2ToUpdatePayload(step2: Step2Input): UpdateDraftRequestBody {
  return {
    fields: mapStep2ToContextFields(step2),
    stepId: "context"
  };
}

export function mapStep2ToSubmitPayload(step2: Step2Input): SubmitFinalRequestBody {
  return {
    fields: mapStep2ToContextFields(step2),
    stepId: "context",
    state: "submitted"
  };
}
