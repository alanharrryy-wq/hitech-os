export type RequestPriority = "low" | "medium" | "high" | "urgent";
export type Region = "north" | "south" | "east" | "west" | "global";

export interface Step1Input {
  readonly request_title: string;
  readonly request_description: string;
  readonly request_priority: RequestPriority;
  readonly requester_name: string;
  readonly requester_email: string;
}

export interface Step2Input {
  readonly required_by: string;
  readonly region: Region | "";
  readonly needs_attachment: boolean;
}

export interface DraftRecordRef {
  readonly recordId: string;
  readonly secureToken: string;
}

export interface DraftStoragePayload {
  readonly recordId: string;
  readonly secureToken: string;
  readonly step1: Step1Input;
  readonly step2: Step2Input;
  readonly savedAtIso: string;
}

export interface CreateDraftRequestBody {
  readonly schemaId: "service_request";
  readonly title: string;
  readonly fields: Step1Input;
  readonly stepId: "requester";
  readonly submit: false;
}

export interface ContextFields {
  required_by?: string;
  region?: Region;
  needs_attachment: boolean;
}

export interface UpdateDraftRequestBody {
  readonly fields: ContextFields;
  readonly stepId: "context";
}

export interface SubmitFinalRequestBody extends UpdateDraftRequestBody {
  readonly state: "submitted";
}

export interface CreateDraftResponse {
  readonly record: {
    readonly id: string;
    readonly secureToken: string;
  };
}
