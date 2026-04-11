import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

import { DEFAULT_LOCALE, isLocale } from "@/lib/i18n/config";
import type { Locale } from "@/lib/i18n/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
export function resolveActiveLocale(preferredLocale?: string | null): Locale {
  if (isLocale(preferredLocale)) return preferredLocale;
  if (typeof document !== "undefined" && isLocale(document.documentElement.lang)) {
    return document.documentElement.lang;
  }
  return DEFAULT_LOCALE;
}

export function formatDateTime(value: string | Date | null | undefined, locale?: string | null): string {
  if (!value) return "-";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return new Intl.DateTimeFormat(resolveActiveLocale(locale), {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

export function formatRelativeTime(value: string | Date | null | undefined, locale?: string | null): string {
  if (!value) return "-";
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return "-";

  const diffMs = date.getTime() - Date.now();
  const absMs = Math.abs(diffMs);
  const rtf = new Intl.RelativeTimeFormat(resolveActiveLocale(locale), { numeric: "auto" });

  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  const week = 7 * day;

  if (absMs < hour) {
    return rtf.format(Math.round(diffMs / minute), "minute");
  }
  if (absMs < day) {
    return rtf.format(Math.round(diffMs / hour), "hour");
  }
  if (absMs < week) {
    return rtf.format(Math.round(diffMs / day), "day");
  }
  return formatDateTime(date, locale);
}

export function formatHumanLabel(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

export function formatValue(value: unknown, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);

  if (value === undefined || value === null || value === "") return "-";
  if (typeof value === "boolean") return value ? (activeLocale === "es" ? "Sí" : "Yes") : "No";
  if (value instanceof Date) return formatDateTime(value, activeLocale);
  if (Array.isArray(value)) return value.length === 0 ? "-" : `${value.length} ${activeLocale === "es" ? (value.length === 1 ? "elemento" : "elementos") : (value.length === 1 ? "item" : "items")}`;
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function formatBytes(value: number | null | undefined): string {
  if (!value || value <= 0) return "-";
  const units = ["B", "KB", "MB", "GB"];
  let size = value;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size >= 10 || unitIndex === 0 ? Math.round(size) : size.toFixed(1)} ${units[unitIndex]}`;
}

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function randomToken(prefix = "tok"): string {
  const seed = Math.random().toString(36).slice(2, 10);
  const stamp = Date.now().toString(36);
  return `${prefix}_${stamp}_${seed}`;
}
