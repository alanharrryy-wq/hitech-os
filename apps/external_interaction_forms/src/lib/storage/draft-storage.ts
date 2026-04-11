import { brandConfig } from "@/lib/config/brand";
import type { DraftStoragePayload } from "@/lib/api/types";

const STORAGE_KEY = brandConfig.storageKey;

export function saveDraftLocal(draft: DraftStoragePayload): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
}

export function loadDraftLocal(): DraftStoragePayload | null {
  if (typeof window === "undefined") {
    return null;
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as DraftStoragePayload;
    if (!parsed.recordId || !parsed.secureToken || !parsed.step1 || !parsed.step2) {
      return null;
    }

    return parsed;
  } catch {
    return null;
  }
}

export function clearDraftLocal(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(STORAGE_KEY);
}
