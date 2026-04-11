export const RECORD_STATES = [
  "draft",
  "submitted",
  "in_review",
  "awaiting_update",
  "approved",
  "rejected",
  "dispatched",
  "synced",
  "failed"
] as const;

export type RecordState = (typeof RECORD_STATES)[number];

export const FLOW_ACCESS_MODES = ["public", "authenticated", "token"] as const;
export type FlowAccessMode = (typeof FLOW_ACCESS_MODES)[number];

export type FieldKind =
  | "text"
  | "textarea"
  | "number"
  | "date"
  | "select"
  | "checkbox"
  | "file"
  | "json";

export type ActionKind =
  | "approve"
  | "reject"
  | "request_changes"
  | "confirm"
  | "acknowledge"
  | "dispatch";

export type SyncStatus = "pending" | "synced" | "failed" | "retryable";

export type DispatchStatus = "pending" | "running" | "succeeded" | "failed";

export type AdapterDirection = "inbound" | "outbound";

export type SchemaCategory =
  | "service_operations"
  | "approval_workflows"
  | "field_operations";

export interface ActorContext {
  actorId?: string;
  actorLabel?: string;
  role: "public" | "external_user" | "reviewer" | "approver" | "operator";
  authenticated?: boolean;
  token?: string;
}

export interface ConditionalRule {
  fieldId: string;
  equals?: string | number | boolean;
  notEquals?: string | number | boolean;
  in?: Array<string | number | boolean>;
}

export interface FieldDefinition {
  id: string;
  label: string;
  kind: FieldKind;
  placeholder?: string;
  helpText?: string;
  required?: boolean;
  options?: string[];
  defaultValue?: string | number | boolean | null;
  visibleWhen?: ConditionalRule[];
  editableInStates?: RecordState[];
  visibleToRoles?: ActorContext["role"][];
}

export interface StepDefinition {
  id: string;
  title: string;
  description?: string;
  fieldIds: string[];
}

export interface ActionDefinition {
  id: string;
  label: string;
  kind: ActionKind;
  intent: "primary" | "secondary" | "danger";
  allowedStates: RecordState[];
  allowedRoles?: ActorContext["role"][];
  nextState?: RecordState;
  requiresComment?: boolean;
  adapterId?: string;
}

export interface ViewDefinition {
  listFields: string[];
  cardFields: string[];
  detailSections: Array<{
    id: string;
    title: string;
    fieldIds: string[];
  }>;
}

export interface FlowDefinition {
  id: string;
  title: string;
  accessMode: FlowAccessMode;
  steps: StepDefinition[];
  allowDrafts: boolean;
}

export interface RecordTypeSchema {
  id: string;
  title: string;
  summary: string;
  category: SchemaCategory;
  tags: string[];
  flow: FlowDefinition;
  fields: FieldDefinition[];
  actions: ActionDefinition[];
  views: ViewDefinition;
  adapterBindings: {
    inbound: string;
    outbound: string;
  };
}

export interface AttachmentInput {
  name: string;
  mimeType?: string;
  size?: number;
  storageKey?: string;
}

export interface ExternalRecord {
  id: string;
  recordTypeId: string;
  state: RecordState;
  title: string;
  secureToken: string;
  fields: Record<string, unknown>;
  actorId?: string;
  createdAt: Date;
  updatedAt: Date;
  submittedAt?: Date;
  lastSyncAt?: Date;
}

export interface Submission {
  id: string;
  recordId: string;
  actorId?: string;
  stepId?: string;
  payload: Record<string, unknown>;
  createdAt: Date;
}

export interface Attachment {
  id: string;
  recordId: string;
  name: string;
  mimeType?: string;
  size?: number;
  storageKey?: string;
  createdAt: Date;
}

export interface DispatchJob {
  id: string;
  recordId: string;
  adapterId: string;
  status: DispatchStatus;
  payload: Record<string, unknown>;
  response?: Record<string, unknown>;
  error?: string;
  attempts: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface SyncEvent {
  id: string;
  recordId: string;
  direction: AdapterDirection;
  adapterId: string;
  status: SyncStatus;
  summary: string;
  payload?: Record<string, unknown>;
  error?: string;
  createdAt: Date;
}

export interface RecordFilter {
  schemaId?: string;
  query?: string;
  state?: RecordState;
}

export interface ResumeTokenLookup {
  token: string;
}

export interface DispatchContext {
  schema: RecordTypeSchema;
  action: ActionDefinition;
  actor: ActorContext;
}
