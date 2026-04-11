import { buildOutboundPayload } from "@/lib/adapters/transform";
import { type ExternalAdapter } from "@/lib/adapters/types";

export class RestAdapter implements ExternalAdapter {
  readonly id = "rest";
  readonly label = "REST Adapter";
  readonly direction = "both" as const;

  async dispatch(request: Parameters<ExternalAdapter["dispatch"]>[0]) {
    const endpoint = process.env.EXTERNAL_INTERACTION_REST_ENDPOINT;
    if (!endpoint) {
      return {
        ok: false,
        statusCode: 500,
        summary: "REST endpoint is not configured",
        error: "Missing EXTERNAL_INTERACTION_REST_ENDPOINT"
      };
    }

    try {
      const payload = buildOutboundPayload(request);
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify(payload)
      });
      const body = await response.text();
      return {
        ok: response.ok,
        statusCode: response.status,
        summary: response.ok ? "REST dispatch succeeded" : "REST dispatch failed",
        responsePayload: {
          body
        },
        error: response.ok ? undefined : `HTTP ${response.status}`
      };
    } catch (error) {
      return {
        ok: false,
        statusCode: 500,
        summary: "REST dispatch exception",
        error: error instanceof Error ? error.message : "Unknown dispatch error"
      };
    }
  }
}
