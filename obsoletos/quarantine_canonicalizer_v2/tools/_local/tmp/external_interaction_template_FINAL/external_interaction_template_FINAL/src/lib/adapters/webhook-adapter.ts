import { buildOutboundPayload } from "@/lib/adapters/transform";
import { type ExternalAdapter } from "@/lib/adapters/types";

export class WebhookAdapter implements ExternalAdapter {
  readonly id = "webhook";
  readonly label = "Webhook Adapter";
  readonly direction = "outbound" as const;

  async dispatch(request: Parameters<ExternalAdapter["dispatch"]>[0]) {
    const endpoint = process.env.EXTERNAL_INTERACTION_WEBHOOK_URL;
    if (!endpoint) {
      return {
        ok: false,
        statusCode: 500,
        summary: "Webhook endpoint is not configured",
        error: "Missing EXTERNAL_INTERACTION_WEBHOOK_URL"
      };
    }

    try {
      const payload = buildOutboundPayload(request);
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-template-source": "external_interaction_template"
        },
        body: JSON.stringify(payload)
      });
      const responseBody = await response.text();
      return {
        ok: response.ok,
        statusCode: response.status,
        summary: response.ok ? "Webhook dispatch succeeded" : "Webhook dispatch failed",
        responsePayload: {
          body: responseBody
        },
        error: response.ok ? undefined : `HTTP ${response.status}`
      };
    } catch (error) {
      return {
        ok: false,
        statusCode: 500,
        summary: "Webhook dispatch exception",
        error: error instanceof Error ? error.message : "Unknown webhook error"
      };
    }
  }
}
