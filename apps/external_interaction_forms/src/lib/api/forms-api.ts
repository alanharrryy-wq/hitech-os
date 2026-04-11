import { getFormsPublicEnv } from "@/lib/config/env";
import {
  mapStep1ToCreateDraftPayload,
  mapStep2ToSubmitPayload,
  mapStep2ToUpdatePayload
} from "./mappers";
import type { CreateDraftResponse, DraftRecordRef, Step1Input, Step2Input } from "./types";

const ACTOR_HEADERS = {
  "x-actor-role": "public",
  "x-actor-label": "whatsapp-form"
} as const;

interface ApiErrorShape {
  readonly error?: string;
  readonly message?: string;
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as ApiErrorShape;
    if (payload.error) {
      return payload.error;
    }
    if (payload.message) {
      return payload.message;
    }
  } catch {
    // Ignore JSON parse issues and fallback to status text.
  }

  return response.statusText || "Error de red";
}

async function requestJson<TResponse>(
  path: string,
  init: RequestInit & { readonly skipJson?: boolean } = {}
): Promise<TResponse> {
  const { apiBaseUrl } = getFormsPublicEnv();
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    cache: "no-store"
  });

  if (!response.ok) {
    const message = await parseErrorMessage(response);
    throw new Error(`${response.status}: ${message}`);
  }

  if (init.skipJson || response.status === 204) {
    return undefined as TResponse;
  }

  return (await response.json()) as TResponse;
}

export async function createDraft(step1: Step1Input): Promise<DraftRecordRef> {
  const payload = mapStep1ToCreateDraftPayload(step1);
  const data = await requestJson<CreateDraftResponse>("/api/records", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...ACTOR_HEADERS
    },
    body: JSON.stringify(payload)
  });

  return {
    recordId: data.record.id,
    secureToken: data.record.secureToken
  };
}

export async function updateByToken(secureToken: string, step2: Step2Input): Promise<void> {
  const payload = mapStep2ToUpdatePayload(step2);
  const encodedToken = encodeURIComponent(secureToken);

  await requestJson<void>(`/api/records/token/${encodedToken}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...ACTOR_HEADERS,
      "x-flow-token": secureToken
    },
    body: JSON.stringify(payload),
    skipJson: true
  });
}

export async function uploadAttachment(recordId: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.set("file", file);

  const encodedRecordId = encodeURIComponent(recordId);
  await requestJson<void>(`/api/records/${encodedRecordId}/attachments`, {
    method: "POST",
    headers: {
      ...ACTOR_HEADERS
    },
    body: formData,
    skipJson: true
  });
}

export async function submitFinal(secureToken: string, step2: Step2Input): Promise<void> {
  const payload = mapStep2ToSubmitPayload(step2);
  const encodedToken = encodeURIComponent(secureToken);

  await requestJson<void>(`/api/records/token/${encodedToken}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...ACTOR_HEADERS,
      "x-flow-token": secureToken
    },
    body: JSON.stringify(payload),
    skipJson: true
  });
}
