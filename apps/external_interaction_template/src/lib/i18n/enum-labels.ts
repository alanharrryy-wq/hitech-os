import { translate } from "@/lib/i18n/dictionary";
import type { DispatchStatus, RecordState, SyncStatus } from "@/lib/core/types";
import { formatHumanLabel, resolveActiveLocale } from "@/lib/utils";

export type Translator = (key: string, values?: Record<string, string | number>) => string;

function fallbackLabel(value: string): string {
  return formatHumanLabel(value);
}

export function mapRecordStateLabel(state: RecordState | string, t: Translator): string {
  switch (state) {
    case "draft":
    case "submitted":
    case "in_review":
    case "awaiting_update":
    case "approved":
    case "rejected":
    case "dispatched":
    case "synced":
    case "failed":
      return t(`recordState.${state}.label`);
    default:
      return fallbackLabel(String(state));
  }
}

export function mapRecordStateDescription(state: RecordState | string, t: Translator): string {
  switch (state) {
    case "draft":
    case "submitted":
    case "in_review":
    case "awaiting_update":
    case "approved":
    case "rejected":
    case "dispatched":
    case "synced":
    case "failed":
      return t(`recordState.${state}.description`);
    default:
      return t("recordState.unknown.description");
  }
}

export function mapDispatchStatusLabel(status: DispatchStatus | string, t: Translator): string {
  switch (status) {
    case "pending":
    case "running":
    case "succeeded":
    case "failed":
      return t(`dispatchStatus.${status}.label`);
    default:
      return fallbackLabel(String(status));
  }
}

export function mapSyncStatusLabel(status: SyncStatus | string, t: Translator): string {
  switch (status) {
    case "pending":
    case "synced":
    case "failed":
    case "retryable":
      return t(`syncStatus.${status}.label`);
    default:
      return fallbackLabel(String(status));
  }
}

export function mapRecordStateLabelForLocale(state: RecordState | string, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);
  return mapRecordStateLabel(state, (key, values) => translate(activeLocale, key, values));
}

export function mapRecordStateDescriptionForLocale(state: RecordState | string, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);
  return mapRecordStateDescription(state, (key, values) => translate(activeLocale, key, values));
}

export function mapDispatchStatusLabelForLocale(status: DispatchStatus | string, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);
  return mapDispatchStatusLabel(status, (key, values) => translate(activeLocale, key, values));
}

export function mapSyncStatusLabelForLocale(status: SyncStatus | string, locale?: string | null): string {
  const activeLocale = resolveActiveLocale(locale);
  return mapSyncStatusLabel(status, (key, values) => translate(activeLocale, key, values));
}
