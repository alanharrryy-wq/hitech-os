import type {
  DataProvider,
  DataSetId,
  ProviderId,
  ProviderResponse,
  Query,
  QueryPrimitive,
  QueryValue
} from "../types.js";

const HTTP_PROVIDER_ID: ProviderId = "http";

export interface HttpRequestDescriptor {
  readonly url: string;
  readonly init?: RequestInit;
}

export interface HttpProviderOptions {
  readonly id?: ProviderId;
  readonly baseUrl?: string;
  readonly defaultRetries?: number;
  readonly retryBackoffMs?: number;
  readonly cacheTtlMs?: number;
  readonly fetchImpl?: typeof fetch;
  readonly buildRequest?: (query: Query) => HttpRequestDescriptor;
}

class RetryableHttpError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "RetryableHttpError";
    this.status = status;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isRetryableStatus(status: number): boolean {
  return status === 408 || status === 425 || status === 429 || status >= 500;
}

function toPrimitiveMetadata(value: unknown): QueryPrimitive | undefined {
  if (value === null || typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return value;
  }
  return undefined;
}

function pickStringParam(params: Query["params"], key: string): string | undefined {
  if (params === undefined) {
    return undefined;
  }

  const value = params[key];
  const candidate = Array.isArray(value) ? value[0] : value;
  return typeof candidate === "string" ? candidate : undefined;
}

function resolveBaseUrl(input: string | undefined): string {
  if (input && input.length > 0) {
    return input;
  }

  if (typeof window !== "undefined" && window.location?.origin) {
    return window.location.origin;
  }

  return "http://127.0.0.1";
}

function defaultBuildRequestFactory(baseUrl: string): (query: Query) => HttpRequestDescriptor {
  return (query: Query) => {
    const path = pickStringParam(query.params, "path") ??
      (query.datasetId ? `/api/dev/kpi/datasets/${query.datasetId}` : undefined);

    if (path === undefined) {
      throw new Error("http provider requires params.path or query.datasetId.");
    }

    const url = new URL(path, baseUrl).toString();
    const method = pickStringParam(query.params, "method") ?? "GET";

    return {
      url,
      init: {
        method
      }
    };
  };
}

function mergeSignals(signal: AbortSignal | undefined, timeoutMs: number | undefined): AbortSignal | undefined {
  if (signal === undefined && timeoutMs === undefined) {
    return undefined;
  }

  if (timeoutMs === undefined) {
    return signal;
  }

  const controller = new AbortController();
  const timer = setTimeout(() => {
    controller.abort(`request timed out after ${timeoutMs}ms`);
  }, timeoutMs);

  if (signal !== undefined) {
    if (signal.aborted) {
      clearTimeout(timer);
      controller.abort(signal.reason);
    } else {
      signal.addEventListener(
        "abort",
        () => {
          clearTimeout(timer);
          controller.abort(signal.reason);
        },
        { once: true }
      );
    }
  }

  controller.signal.addEventListener(
    "abort",
    () => {
      clearTimeout(timer);
    },
    { once: true }
  );

  return controller.signal;
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      resolve();
    }, ms);

    if (signal === undefined) {
      return;
    }

    if (signal.aborted) {
      clearTimeout(timer);
      reject(signal.reason ?? new Error("aborted"));
      return;
    }

    signal.addEventListener(
      "abort",
      () => {
        clearTimeout(timer);
        reject(signal.reason ?? new Error("aborted"));
      },
      { once: true }
    );
  });
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as unknown;
  }

  return await response.text();
}

function toMetadata(input: Record<string, unknown>, attempts: number): Record<string, QueryPrimitive> {
  const metadata: Record<string, QueryPrimitive> = {
    source: "http-provider",
    attempts
  };

  for (const [key, value] of Object.entries(input)) {
    if (key === "data" || key === "payload" || key === "metadata") {
      continue;
    }

    const primitive = toPrimitiveMetadata(value);
    if (primitive !== undefined) {
      metadata[key] = primitive;
    }
  }

  return metadata;
}

function withDefaultMetadata(
  value: QueryValue | undefined,
  fallback: QueryPrimitive
): QueryPrimitive {
  if (value === undefined) {
    return fallback;
  }

  if (Array.isArray(value)) {
    const first = value[0];
    if (first === undefined) {
      return fallback;
    }
    return (first ?? fallback) as QueryPrimitive;
  }

  return value as QueryPrimitive;
}

export function createHttpProvider(options: HttpProviderOptions = {}): DataProvider {
  const providerId = options.id ?? HTTP_PROVIDER_ID;
  const baseUrl = resolveBaseUrl(options.baseUrl);
  const fetchImpl = options.fetchImpl ?? fetch;
  const retries = Math.max(0, options.defaultRetries ?? 2);
  const retryBackoffMs = Math.max(0, options.retryBackoffMs ?? 250);
  const cacheTtlMs = options.cacheTtlMs ?? 10_000;
  const buildRequest = options.buildRequest ?? defaultBuildRequestFactory(baseUrl);

  return {
    id: providerId,
    async query(input: Query): Promise<ProviderResponse> {
      const requestedRetries = Math.max(0, input.retryCount ?? retries);
      let attempts = 0;

      while (true) {
        attempts += 1;

        const descriptor = buildRequest(input);
        const signal = mergeSignals(input.signal, input.timeoutMs);

        try {
          const headers = new Headers(descriptor.init?.headers);
          if (!headers.has("content-type")) {
            headers.set("content-type", "application/json");
          }

          const requestInit: RequestInit = {
            ...descriptor.init,
            cache: "no-store",
            headers
          };
          if (signal !== undefined) {
            requestInit.signal = signal;
          }

          const response = await fetchImpl(descriptor.url, requestInit);

          if (!response.ok) {
            const bodyText = await response.text();
            if (isRetryableStatus(response.status) && attempts <= requestedRetries + 1) {
              throw new RetryableHttpError(
                response.status,
                `Retryable HTTP ${response.status} for ${descriptor.url}: ${bodyText.slice(0, 200)}`
              );
            }

            throw new Error(`HTTP ${response.status} for ${descriptor.url}: ${bodyText.slice(0, 200)}`);
          }

          const body = await parseResponseBody(response);

          if (!isRecord(body)) {
            return {
              providerId,
              datasetId: input.datasetId,
              dataShapeId: input.dataShapeId ?? "timeSeries",
              data: body,
              cacheTtlMs,
              metadata: {
                source: "http-provider",
                attempts
              }
            };
          }

          const dataShapeId =
            input.dataShapeId ??
            (typeof body["dataShapeId"] === "string" ? body["dataShapeId"] : "timeSeries");

          const datasetId =
            input.datasetId ??
            (typeof body["datasetId"] === "string" ? (body["datasetId"] as DataSetId) : undefined);

          const metadataSource =
            isRecord(body["metadata"]) && typeof body["metadata"]["source"] === "string"
              ? (body["metadata"]["source"] as string)
              : "http-provider";

          const metadata = {
            ...toMetadata(body, attempts),
            source: metadataSource,
            requestPath: withDefaultMetadata(input.params?.["path"], "")
          };

          return {
            providerId,
            datasetId,
            dataShapeId,
            data: body["payload"] ?? body["data"] ?? body,
            cacheTtlMs,
            metadata
          };
        } catch (error) {
          const aborted =
            error instanceof DOMException
              ? error.name === "AbortError"
              : error instanceof Error && error.name === "AbortError";

          if (aborted) {
            throw error;
          }

          const isRetryable = error instanceof RetryableHttpError;
          const attemptsLeft = attempts <= requestedRetries;

          if (!isRetryable || !attemptsLeft) {
            throw error;
          }

          const backoff = retryBackoffMs * Math.max(1, attempts);
          await sleep(backoff, input.signal);
        }
      }
    }
  };
}


