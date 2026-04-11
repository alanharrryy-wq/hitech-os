import {
  type ActionDefinition,
  type FieldDefinition,
  type RecordTypeSchema,
  type StepDefinition
} from "@/lib/core/types";

function step(id: string, title: string, description: string, fieldIds: string[]): StepDefinition {
  return { id, title, description, fieldIds };
}

function action(definition: ActionDefinition): ActionDefinition {
  return definition;
}

function field(definition: FieldDefinition): FieldDefinition {
  return definition;
}

const serviceRequestSchema: RecordTypeSchema = {
  id: "service_request",
  title: "Service Request",
  summary: "Capture, review and resolve externally submitted service operations requests.",
  category: "service_operations",
  tags: ["collect", "update", "dispatch", "sync"],
  flow: {
    id: "service-request-flow",
    title: "Service Request Flow",
    accessMode: "public",
    allowDrafts: true,
    steps: [
      step("requester", "Requester", "Who is submitting and what is needed?", [
        "request_title",
        "request_description",
        "request_priority",
        "requester_name",
        "requester_email"
      ]),
      step("context", "Context", "Add timing and optional supporting files.", [
        "required_by",
        "region",
        "needs_attachment",
        "attachments"
      ])
    ]
  },
  fields: [
    field({ id: "request_title", label: "Title", kind: "text", required: true, placeholder: "Request title" }),
    field({
      id: "request_description",
      label: "Description",
      kind: "textarea",
      required: true,
      placeholder: "Describe the request, context and expected outcome"
    }),
    field({
      id: "request_priority",
      label: "Priority",
      kind: "select",
      required: true,
      options: ["low", "medium", "high", "urgent"],
      defaultValue: "medium"
    }),
    field({ id: "requester_name", label: "Requester name", kind: "text", required: true }),
    field({ id: "requester_email", label: "Requester email", kind: "text", required: true }),
    field({ id: "required_by", label: "Required by", kind: "date" }),
    field({ id: "region", label: "Region", kind: "select", options: ["north", "south", "east", "west", "global"] }),
    field({ id: "needs_attachment", label: "Needs attachment", kind: "checkbox", defaultValue: false }),
    field({
      id: "attachments",
      label: "Attachments",
      kind: "file",
      helpText: "Optional files for additional context.",
      visibleWhen: [{ fieldId: "needs_attachment", equals: true }]
    })
  ],
  actions: [
    action({
      id: "confirm",
      label: "Confirm Submission",
      kind: "confirm",
      intent: "primary",
      allowedStates: ["submitted", "awaiting_update"],
      nextState: "in_review",
      allowedRoles: ["reviewer", "approver", "operator"]
    }),
    action({
      id: "request_changes",
      label: "Request Changes",
      kind: "request_changes",
      intent: "secondary",
      allowedStates: ["submitted", "in_review"],
      nextState: "awaiting_update",
      allowedRoles: ["reviewer", "approver", "operator"],
      requiresComment: true
    }),
    action({
      id: "approve",
      label: "Approve",
      kind: "approve",
      intent: "primary",
      allowedStates: ["in_review"],
      nextState: "approved",
      allowedRoles: ["approver", "operator"]
    }),
    action({
      id: "dispatch",
      label: "Dispatch",
      kind: "dispatch",
      intent: "primary",
      allowedStates: ["approved"],
      nextState: "dispatched",
      allowedRoles: ["operator"],
      adapterId: "webhook"
    })
  ],
  views: {
    listFields: ["request_title", "request_priority", "requester_name", "required_by"],
    cardFields: ["request_title", "request_description", "request_priority", "region"],
    detailSections: [
      { id: "summary", title: "Summary", fieldIds: ["request_title", "request_description", "request_priority"] },
      { id: "requester", title: "Requester", fieldIds: ["requester_name", "requester_email", "region"] },
      { id: "delivery", title: "Delivery", fieldIds: ["required_by", "needs_attachment", "attachments"] }
    ]
  },
  adapterBindings: {
    inbound: "local",
    outbound: "webhook"
  }
};

const approvalPacketSchema: RecordTypeSchema = {
  id: "approval_packet",
  title: "Approval Packet",
  summary: "Token-secure packet review and external approval/rejection workflow.",
  category: "approval_workflows",
  tags: ["approve", "reject", "review", "token"],
  flow: {
    id: "approval-packet-flow",
    title: "Approval Packet Flow",
    accessMode: "token",
    allowDrafts: true,
    steps: [
      step("packet", "Packet", "Provide packet context.", [
        "packet_title",
        "packet_owner",
        "packet_scope",
        "packet_due_date"
      ]),
      step("decision", "Decision Inputs", "Complete mandatory checklist before decision.", [
        "risk_level",
        "compliance_reviewed",
        "decision_notes"
      ])
    ]
  },
  fields: [
    field({ id: "packet_title", label: "Packet title", kind: "text", required: true }),
    field({ id: "packet_owner", label: "Owner", kind: "text", required: true }),
    field({ id: "packet_scope", label: "Scope", kind: "textarea", required: true }),
    field({ id: "packet_due_date", label: "Due date", kind: "date" }),
    field({
      id: "risk_level",
      label: "Risk level",
      kind: "select",
      options: ["low", "moderate", "high"],
      defaultValue: "moderate"
    }),
    field({ id: "compliance_reviewed", label: "Compliance reviewed", kind: "checkbox", required: true }),
    field({ id: "decision_notes", label: "Decision notes", kind: "textarea" })
  ],
  actions: [
    action({
      id: "approve",
      label: "Approve Packet",
      kind: "approve",
      intent: "primary",
      allowedStates: ["submitted", "in_review"],
      nextState: "approved",
      allowedRoles: ["approver", "operator"]
    }),
    action({
      id: "reject",
      label: "Reject Packet",
      kind: "reject",
      intent: "danger",
      allowedStates: ["submitted", "in_review"],
      nextState: "rejected",
      allowedRoles: ["approver", "operator"],
      requiresComment: true
    }),
    action({
      id: "request_changes",
      label: "Request Changes",
      kind: "request_changes",
      intent: "secondary",
      allowedStates: ["submitted", "in_review"],
      nextState: "awaiting_update",
      allowedRoles: ["approver", "operator"],
      requiresComment: true
    }),
    action({
      id: "acknowledge",
      label: "Acknowledge",
      kind: "acknowledge",
      intent: "secondary",
      allowedStates: ["approved", "rejected"],
      allowedRoles: ["external_user", "public", "reviewer", "approver", "operator"]
    })
  ],
  views: {
    listFields: ["packet_title", "packet_owner", "risk_level", "packet_due_date"],
    cardFields: ["packet_title", "packet_scope", "risk_level", "compliance_reviewed"],
    detailSections: [
      { id: "packet", title: "Packet", fieldIds: ["packet_title", "packet_owner", "packet_scope", "packet_due_date"] },
      { id: "decision", title: "Decision Inputs", fieldIds: ["risk_level", "compliance_reviewed", "decision_notes"] }
    ]
  },
  adapterBindings: {
    inbound: "rest",
    outbound: "rest"
  }
};

const inspectionChecklistSchema: RecordTypeSchema = {
  id: "inspection_checklist",
  title: "Field Inspection Checklist",
  summary: "Collect field inspection data, review status and sync to external systems.",
  category: "field_operations",
  tags: ["collect", "checklist", "sync", "mobile"],
  flow: {
    id: "inspection-checklist-flow",
    title: "Inspection Checklist Flow",
    accessMode: "authenticated",
    allowDrafts: true,
    steps: [
      step("meta", "Inspection Meta", "Where and when was this inspection made?", [
        "site_name",
        "inspector",
        "inspection_date",
        "inspection_type"
      ]),
      step("checks", "Checks", "Capture condition and findings.", [
        "condition_score",
        "requires_follow_up",
        "findings",
        "photo_attachments"
      ])
    ]
  },
  fields: [
    field({ id: "site_name", label: "Site name", kind: "text", required: true }),
    field({ id: "inspector", label: "Inspector", kind: "text", required: true }),
    field({ id: "inspection_date", label: "Inspection date", kind: "date", required: true }),
    field({
      id: "inspection_type",
      label: "Inspection type",
      kind: "select",
      options: ["routine", "incident", "commissioning", "closure"],
      required: true
    }),
    field({ id: "condition_score", label: "Condition score", kind: "number", required: true }),
    field({ id: "requires_follow_up", label: "Requires follow-up", kind: "checkbox", defaultValue: false }),
    field({ id: "findings", label: "Findings", kind: "textarea" }),
    field({
      id: "photo_attachments",
      label: "Photo attachments",
      kind: "file",
      visibleWhen: [{ fieldId: "requires_follow_up", equals: true }]
    })
  ],
  actions: [
    action({
      id: "confirm",
      label: "Confirm",
      kind: "confirm",
      intent: "primary",
      allowedStates: ["submitted", "awaiting_update"],
      nextState: "in_review",
      allowedRoles: ["reviewer", "operator"]
    }),
    action({
      id: "request_changes",
      label: "Request Update",
      kind: "request_changes",
      intent: "secondary",
      allowedStates: ["submitted", "in_review"],
      nextState: "awaiting_update",
      allowedRoles: ["reviewer", "operator"],
      requiresComment: true
    }),
    action({
      id: "dispatch",
      label: "Dispatch to Target",
      kind: "dispatch",
      intent: "primary",
      allowedStates: ["in_review", "approved"],
      nextState: "dispatched",
      allowedRoles: ["operator"],
      adapterId: "local"
    })
  ],
  views: {
    listFields: ["site_name", "inspector", "inspection_date", "inspection_type"],
    cardFields: ["site_name", "inspection_type", "condition_score", "requires_follow_up"],
    detailSections: [
      { id: "meta", title: "Inspection Meta", fieldIds: ["site_name", "inspector", "inspection_date", "inspection_type"] },
      {
        id: "checks",
        title: "Checks & Findings",
        fieldIds: ["condition_score", "requires_follow_up", "findings", "photo_attachments"]
      }
    ]
  },
  adapterBindings: {
    inbound: "local",
    outbound: "local"
  }
};

export const exampleSchemas: RecordTypeSchema[] = [serviceRequestSchema, approvalPacketSchema, inspectionChecklistSchema];

const schemaMap = new Map(exampleSchemas.map((schema) => [schema.id, schema]));

export function listSchemas(): RecordTypeSchema[] {
  return exampleSchemas;
}

export function getSchema(schemaId: string): RecordTypeSchema {
  const schema = schemaMap.get(schemaId);
  if (!schema) {
    throw new Error(`Unknown schema '${schemaId}'`);
  }
  return schema;
}

export function getFieldById(schema: RecordTypeSchema, fieldId: string): FieldDefinition {
  const definition = schema.fields.find((fieldEntry) => fieldEntry.id === fieldId);
  if (!definition) {
    throw new Error(`Unknown field '${fieldId}' in schema '${schema.id}'`);
  }
  return definition;
}

export function getStepById(schema: RecordTypeSchema, stepId: string): StepDefinition {
  const definition = schema.flow.steps.find((stepEntry) => stepEntry.id === stepId);
  if (!definition) {
    throw new Error(`Unknown step '${stepId}' in schema '${schema.id}'`);
  }
  return definition;
}
