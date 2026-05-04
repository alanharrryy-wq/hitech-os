import { prismaMobileErrorMessage } from "../prisma-mobile-error";
import type { EndpointRole, FetchResult, UpstreamId } from "./types";

export type DataPlaneHttpOptions = { upstream: UpstreamId; role: EndpointRole; timeoutMs: number; retryCount: number };

function abortErrorName(error: unknown): string {
  return error instanceof Error ? error.name : "Error";
}

function errorMessage(error: unknown): string {
  return prismaMobileErrorMessage(error, "Error de red sin detalle legible");
}

async function attemptFetchJson<T>(url: string, options: DataPlaneHttpOptions): Promise<FetchResult<T>> {
  const started = Date.now();
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs);
  try {
    const response = await fetch(url, { cache: "no-store", signal: controller.signal, headers: { Accept: "application/json" } });
    const latencyMs = Date.now() - started;
    if (!response.ok) {
      return { status: "http_error", upstream: options.upstream, role: options.role, url, data: null, httpStatus: response.status, latencyMs, error: `HTTP ${response.status}` };
    }
    try {
      const data = (await response.json()) as T;
      return { status: "ok", upstream: options.upstream, role: options.role, url, data, httpStatus: response.status, latencyMs };
    } catch (error) {
      return { status: "parse_error", upstream: options.upstream, role: options.role, url, data: null, httpStatus: response.status, latencyMs, error: errorMessage(error) };
    }
  } catch (error) {
    const latencyMs = Date.now() - started;
    const timedOut = abortErrorName(error) === "AbortError";
    return { status: timedOut ? "timeout" : "network_error", upstream: options.upstream, role: options.role, url, data: null, latencyMs, error: timedOut ? `Timeout ${options.timeoutMs}ms` : errorMessage(error) };
  } finally {
    clearTimeout(timeout);
  }
}

export async function fetchJsonWithRetry<T>(url: string | null, options: DataPlaneHttpOptions): Promise<FetchResult<T>> {
  if (!url) return { status: "disabled", upstream: options.upstream, role: options.role, url: "disabled", data: null, latencyMs: 0, error: "Origen no configurado" };
  let last: FetchResult<T> | null = null;
  for (let attempt = 0; attempt <= options.retryCount; attempt += 1) {
    last = await attemptFetchJson<T>(url, options);
    if (last.status === "ok") return last;
  }
  return last ?? { status: "network_error", upstream: options.upstream, role: options.role, url, data: null, latencyMs: 0, error: "No hubo intento HTTP" };
}

export function probeFromFetchResult(result: FetchResult<unknown>) {
  return { id: result.upstream, ok: result.status === "ok", url: result.url, status: result.httpStatus, latencyMs: result.latencyMs, error: result.error };
}
