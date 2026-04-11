const isProduction = process.env["NODE_ENV"] === "production";
const DEFAULT_OPERATOR_APP_URL = isProduction ? "" : "http://127.0.0.1:3110";
const DEFAULT_FORMS_APP_URL = isProduction ? "https://forms.hitechrts.com" : "http://127.0.0.1:3200";

function normalizeExternalUrl(value: string): string | null {
  if (!value) {
    return null;
  }

  try {
    const normalized = new URL(value);
    return normalized.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

function resolveOptionalUrl(value: string | undefined, fallback: string): string | null {
  const candidate = (value?.trim() || fallback).trim();
  return normalizeExternalUrl(candidate);
}

function resolveRequiredUrl(value: string | undefined, fallback: string): string {
  const candidate = (value?.trim() || fallback).trim();
  const normalized = normalizeExternalUrl(candidate);
  if (normalized) {
    return normalized;
  }

  return fallback;
}

const operatorAppUrl = resolveOptionalUrl(
  process.env["NEXT_PUBLIC_OPERATOR_APP_URL"],
  DEFAULT_OPERATOR_APP_URL
);

export const externalAppLinks = {
  operatorAppUrl,
  showOperatorEntry: Boolean(operatorAppUrl),
  formsAppUrl: resolveRequiredUrl(process.env["NEXT_PUBLIC_FORMS_APP_URL"], DEFAULT_FORMS_APP_URL)
} as const;
