import type { AgentCapabilities, HealthReport, JobRequest, JobResult } from "../contracts.ts";
import { validateAgentCapabilities, validateJobResult } from "../contracts.ts";

export interface AiAgentClientConfig {
  baseUrl: string;
  timeoutMs: number;
}

export interface ClientFailure {
  ok: false;
  statusCode: number;
  errorCode: string;
  message: string;
}

export interface ClientSuccess<T> {
  ok: true;
  statusCode: number;
  data: T;
}

export type ClientResult<T> = ClientFailure | ClientSuccess<T>;

function joinUrl(baseUrl: string, path: string): string {
  const normalizedBase = baseUrl.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

async function fetchJson(url: string, init: RequestInit, timeoutMs: number): Promise<ClientResult<unknown>> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal
    });
    const text = await response.text();
    let payload: unknown = null;

    if (text.trim().length > 0) {
      try {
        payload = JSON.parse(text) as unknown;
      } catch {
        return {
          ok: false,
          statusCode: response.status,
          errorCode: "AGENT_INVALID_JSON",
          message: "ai-agent returned non-JSON payload"
        };
      }
    }

    if (!response.ok) {
      return {
        ok: false,
        statusCode: response.status,
        errorCode: "AGENT_HTTP_ERROR",
        message: `ai-agent responded with HTTP ${response.status}`
      };
    }

    return {
      ok: true,
      statusCode: response.status,
      data: payload
    };
  } catch (error) {
    return {
      ok: false,
      statusCode: 503,
      errorCode: "AGENT_UNREACHABLE",
      message: error instanceof Error ? error.message : "unknown fetch failure"
    };
  } finally {
    clearTimeout(timeout);
  }
}

export class AiAgentClient {
  readonly #config: AiAgentClientConfig;

  constructor(config: AiAgentClientConfig) {
    this.#config = config;
  }

  async getCapabilities(): Promise<ClientResult<AgentCapabilities>> {
    const response = await fetchJson(joinUrl(this.#config.baseUrl, "/capabilities"), { method: "GET" }, this.#config.timeoutMs);
    if (!response.ok) {
      return response;
    }

    const validated = validateAgentCapabilities(response.data);
    if (!validated.ok || validated.value === undefined) {
      return {
        ok: false,
        statusCode: 502,
        errorCode: "AGENT_INVALID_CAPABILITIES",
        message: validated.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
      };
    }

    return {
      ok: true,
      statusCode: 200,
      data: validated.value
    };
  }

  async runJob(request: JobRequest): Promise<ClientResult<JobResult>> {
    const response = await fetchJson(
      joinUrl(this.#config.baseUrl, "/jobs/run"),
      {
        method: "POST",
        headers: {
          "content-type": "application/json"
        },
        body: JSON.stringify(request)
      },
      this.#config.timeoutMs
    );

    if (!response.ok) {
      return response;
    }

    const validated = validateJobResult(response.data);
    if (!validated.ok || validated.value === undefined) {
      return {
        ok: false,
        statusCode: 502,
        errorCode: "AGENT_INVALID_JOB_RESULT",
        message: validated.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
      };
    }

    return {
      ok: true,
      statusCode: 200,
      data: validated.value
    };
  }

  async health(): Promise<ClientResult<HealthReport>> {
    const response = await fetchJson(joinUrl(this.#config.baseUrl, "/health"), { method: "GET" }, this.#config.timeoutMs);
    if (!response.ok) {
      return response;
    }

    const data = response.data as HealthReport;
    if (!data || typeof data !== "object") {
      return {
        ok: false,
        statusCode: 502,
        errorCode: "AGENT_INVALID_HEALTH",
        message: "health payload must be an object"
      };
    }

    return {
      ok: true,
      statusCode: 200,
      data
    };
  }
}
