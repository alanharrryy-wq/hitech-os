import { FEATURE_FLAGS_DEFAULTS, type FeatureFlags, type HealthReport } from "@hitech/contracts";

const apiBaseUrl = (import.meta.env.VITE_CORE_API_URL as string | undefined) ?? "http://127.0.0.1:3001";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${path} (${response.status})`);
  }

  return (await response.json()) as T;
}

export async function getFeatureFlags(): Promise<FeatureFlags> {
  try {
    const payload = await fetchJson<FeatureFlags>("/flags");
    return {
      ...FEATURE_FLAGS_DEFAULTS,
      ...payload
    };
  } catch {
    return FEATURE_FLAGS_DEFAULTS;
  }
}

export async function getHealth(): Promise<HealthReport> {
  return fetchJson<HealthReport>("/health");
}

export function getApiBaseUrl(): string {
  return apiBaseUrl;
}
