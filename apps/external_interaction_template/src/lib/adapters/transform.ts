import { type DispatchRequest } from "@/lib/adapters/types";

export function buildOutboundPayload(request: DispatchRequest): Record<string, unknown> {
  return {
    record_id: request.record.id,
    schema_id: request.schema.id,
    action_id: request.action.id,
    state: request.record.state,
    secure_token: request.record.secureToken,
    title: request.record.title,
    fields: request.record.fields,
    metadata: {
      outbound_at: new Date().toISOString(),
      adapter_hint: request.schema.adapterBindings.outbound,
      tags: request.schema.tags
    },
    ...(request.payload ?? {})
  };
}
