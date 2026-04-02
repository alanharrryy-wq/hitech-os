import { buildOutboundPayload } from "@/lib/adapters/transform";
import { type ExternalAdapter } from "@/lib/adapters/types";

export class LocalAdapter implements ExternalAdapter {
  readonly id = "local";
  readonly label = "Local Adapter";
  readonly direction = "both" as const;

  async dispatch(request: Parameters<ExternalAdapter["dispatch"]>[0]) {
    const payload = buildOutboundPayload(request);
    return {
      ok: true,
      statusCode: 200,
      summary: "Stored in local adapter log",
      responsePayload: {
        accepted: true,
        adapter: this.id,
        receivedAt: new Date().toISOString(),
        payload
      }
    };
  }
}
