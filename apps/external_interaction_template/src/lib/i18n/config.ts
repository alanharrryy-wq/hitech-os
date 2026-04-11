import { SUPPORTED_LOCALES, type Locale } from "@/lib/i18n/types";

export const DEFAULT_LOCALE: Locale = "es";
export const FALLBACK_LOCALE: Locale = "es";
export const LOCALE_STORAGE_KEY = "external_interaction_template.locale";

export function isLocale(value: string | null | undefined): value is Locale {
  return value === "es" || value === "en";
}

export { SUPPORTED_LOCALES };