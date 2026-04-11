import { DEFAULT_LOCALE, FALLBACK_LOCALE } from "@/lib/i18n/config";
import { enMessages } from "@/lib/i18n/messages/en";
import { esMessages } from "@/lib/i18n/messages/es";
import type { Locale, MessageDictionary } from "@/lib/i18n/types";

const dictionaries: Record<Locale, MessageDictionary> = {
  es: esMessages,
  en: enMessages
};

function interpolate(template: string, values?: Record<string, string | number>): string {
  if (!values) return template;
  return template.replace(/\{(\w+)\}/g, (_, token: string) => String(values[token] ?? `{${token}}`));
}

export function resolveMessage(locale: Locale, key: string): string {
  return dictionaries[locale][key] ?? dictionaries[FALLBACK_LOCALE][key] ?? (process.env.NODE_ENV === "production" ? key : `[[missing:${key}]]`);
}

export function translate(locale: Locale, key: string, values?: Record<string, string | number>): string {
  return interpolate(resolveMessage(locale, key), values);
}

export function getTranslator(locale: Locale = DEFAULT_LOCALE) {
  return (key: string, values?: Record<string, string | number>) => translate(locale, key, values);
}