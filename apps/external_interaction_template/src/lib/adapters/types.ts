import { type ActionDefinition, type ExternalRecord, type RecordTypeSchema } from "@/lib/core/types";

export interface DispatchRequest {
  record: ExternalRecord;
  schema: RecordTypeSchema;
  action: ActionDefinition;
  payload: Record<string, unknown>;
}

export interface DispatchResponse {
  ok: boolean;
  statusCode: number;
  summary: string;
  responsePayload?: Record<string, unknown>;
  error?: string;
}

export interface ExternalAdapter {
  id: string;
  label: string;
  direction: "inbound" | "outbound" | "both";
  dispatch(request: DispatchRequest): Promise<DispatchResponse>;
}
