import type {
  CreateRecordPayload,
  DraftRecordRef,
  SubmitRecordPayload,
  UpdateRecordPayload
} from "@/lib/forms/contracts";

const FORMS_GATEWAY_BASE = "/api/forms-gateway";

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
    if (payload.error) return payload.error;
    if (payload.message) return payload.message;
  } catch {
    // noop
  }
  return response.statusText || "Network error";
}

async function requestJson<TResponse>(
  path: string,
  init: RequestInit & { readonly skipJson?: boolean } = {}
): Promise<TResponse> {
  const response = await fetch(`${FORMS_GATEWAY_BASE}${path}`, {
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

export async function createDraftRecord(
  formTypeId: string,
  payload: CreateRecordPayload
): Promise<DraftRecordRef> {
  const data = await requestJson<{ record: { id: string; secureToken: string } }>("/records", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...ACTOR_HEADERS,
      "x-form-type": formTypeId
    },
    body: JSON.stringify(payload)
  });

  return {
    recordId: data.record.id,
    secureToken: data.record.secureToken
  };
}

export async function updateDraftByToken(
  formTypeId: string,
  secureToken: string,
  payload: UpdateRecordPayload
): Promise<void> {
  const encodedToken = encodeURIComponent(secureToken);
  await requestJson<void>(`/records/token/${encodedToken}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...ACTOR_HEADERS,
      "x-flow-token": secureToken,
      "x-form-type": formTypeId
    },
    body: JSON.stringify(payload),
    skipJson: true
  });
}

export async function submitRecordByToken(
  formTypeId: string,
  secureToken: string,
  payload: SubmitRecordPayload
): Promise<void> {
  const encodedToken = encodeURIComponent(secureToken);
  await requestJson<void>(`/records/token/${encodedToken}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...ACTOR_HEADERS,
      "x-flow-token": secureToken,
      "x-form-type": formTypeId
    },
    body: JSON.stringify(payload),
    skipJson: true
  });
}

export async function uploadAttachmentForRecord(
  formTypeId: string,
  recordId: string,
  file: File
): Promise<void> {
  const formData = new FormData();
  formData.set("file", file);

  const encodedRecordId = encodeURIComponent(recordId);
  await requestJson<void>(`/records/${encodedRecordId}/attachments`, {
    method: "POST",
    headers: {
      ...ACTOR_HEADERS,
      "x-form-type": formTypeId
    },
    body: formData,
    skipJson: true
  });
}

