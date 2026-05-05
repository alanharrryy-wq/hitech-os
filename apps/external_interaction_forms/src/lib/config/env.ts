import { brandConfig } from "./brand";

export interface FormsPublicEnv {
  readonly apiBaseUrl: string;
  readonly publicAppUrl: string;
}

export interface FormsServerEnv {
  readonly engineApiBaseUrl: string;
}

let cachedEnv: FormsPublicEnv | null = null;
let cachedServerEnv: FormsServerEnv | null = null;

function normalizeBaseUrl(value: string | undefined, fallback: string): string {
  const candidate = value?.trim();
  if (!candidate) {
    return fallback;
  }

  try {
    const normalized = new URL(candidate);
    return normalized.toString().replace(/\/$/, "");
  } catch {
    return fallback;
  }
}

export function getFormsPublicEnv(): FormsPublicEnv {
  if (cachedEnv) {
    return cachedEnv;
  }

  const isProduction = process.env["NODE_ENV"] === "production";
  const apiFallback = isProduction
    ? brandConfig.defaults.prodApiBaseUrl
    : brandConfig.defaults.apiBaseUrl;
  const appFallback = isProduction
    ? brandConfig.defaults.prodAppUrl
    : brandConfig.defaults.appUrl;

  cachedEnv = {
    apiBaseUrl: normalizeBaseUrl(process.env["NEXT_PUBLIC_API_BASE_URL"], apiFallback),
    publicAppUrl: normalizeBaseUrl(process.env["NEXT_PUBLIC_FORMS_APP_URL"], appFallback)
  };

  return cachedEnv;
}

export function getFormsServerEnv(): FormsServerEnv {
  if (cachedServerEnv) {
    return cachedServerEnv;
  }

  const isProduction = process.env["NODE_ENV"] === "production";
  const fallback = isProduction ? brandConfig.defaults.prodApiBaseUrl : brandConfig.defaults.apiBaseUrl;

  cachedServerEnv = {
    engineApiBaseUrl: normalizeBaseUrl(
      process.env["FORMS_ENGINE_API_BASE_URL"] ?? process.env["NEXT_PUBLIC_API_BASE_URL"],
      fallback
    )
  };

  return cachedServerEnv;
}
