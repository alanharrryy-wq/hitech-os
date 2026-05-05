import { brandConfig } from "@/lib/config/brand";
import type { DraftRecordRef, FormValues } from "@/lib/forms/contracts";

const STORAGE_KEY = brandConfig.storageKey;

export interface FormDraftSnapshot {
  formTypeId: string;
  recordRef: DraftRecordRef;
  values: FormValues;
  savedAtIso: string;
  stepIndex?: number;
}

interface LegacyDraftShape {
  recordId?: string;
  secureToken?: string;
  step1?: Record<string, unknown>;
  step2?: Record<string, unknown>;
  savedAtIso?: string;
}

function toLegacyServiceRequestDraft(raw: LegacyDraftShape): FormDraftSnapshot | null {
  if (!raw.recordId || !raw.secureToken || !raw.step1 || !raw.step2) {
    return null;
  }

  const values: FormValues = {
    request_title: String(raw.step1["request_title"] ?? ""),
    request_description: String(raw.step1["request_description"] ?? ""),
    request_priority: String(raw.step1["request_priority"] ?? "medium"),
    requester_name: String(raw.step1["requester_name"] ?? ""),
    requester_email: String(raw.step1["requester_email"] ?? ""),
    required_by: String(raw.step2["required_by"] ?? ""),
    region: String(raw.step2["region"] ?? ""),
    needs_attachment: raw.step2["needs_attachment"] === true
  };

  return {
    formTypeId: "service_request_public",
    recordRef: {
      recordId: raw.recordId,
      secureToken: raw.secureToken
    },
    values,
    savedAtIso: typeof raw.savedAtIso === "string" ? raw.savedAtIso : new Date().toISOString(),
    stepIndex: 1
  };
}

export function saveFormDraftLocal(snapshot: FormDraftSnapshot): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
}

export function loadFormDraftLocal(): FormDraftSnapshot | null {
  if (typeof window === "undefined") return null;

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as Partial<FormDraftSnapshot> & LegacyDraftShape;

    if (parsed.formTypeId && parsed.recordRef?.recordId && parsed.recordRef?.secureToken && parsed.values) {
      return {
        formTypeId: parsed.formTypeId,
        recordRef: {
          recordId: parsed.recordRef.recordId,
          secureToken: parsed.recordRef.secureToken
        },
        values: parsed.values,
        savedAtIso: typeof parsed.savedAtIso === "string" ? parsed.savedAtIso : new Date().toISOString(),
        stepIndex: typeof parsed.stepIndex === "number" ? parsed.stepIndex : undefined
      };
    }

    return toLegacyServiceRequestDraft(parsed);
  } catch {
    return null;
  }
}

export function clearFormDraftLocal(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
}
