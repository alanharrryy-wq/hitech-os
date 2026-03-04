"use client";

import { parseOrThrow } from "@hitech/contracts";
import {
  ArtifactRunIndexSchema,
  CapabilityStatusSchema,
  OperatorHudStatusSchema,
  PitchProgramSchema,
  TriageActionRequestSchema
} from "./schemas";
import type {
  ArtifactRunIndex,
  CapabilityMode,
  CapabilityStatus,
  OperatorHudStatus,
  PitchProgram,
  SupportBundle,
  TriageActionRequest,
  TriageActionResult
} from "./types";

async function fetchJson(path: string, init?: RequestInit): Promise<unknown> {
  const response = await fetch(path, {
    ...init,
    cache: "no-store",
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed ${response.status} ${path}: ${text}`);
  }

  return (await response.json()) as unknown;
}

export async function fetchCapabilities(mode: CapabilityMode): Promise<CapabilityStatus> {
  const result = await fetchJson(`/api/pitch-engine/capabilities?debug=1&requestedMode=${mode}`);
  return parseOrThrow(CapabilityStatusSchema, result, {
    resource: "pitch-engine.capabilities",
    operation: "client-fetch"
  });
}

export async function fetchPrograms(): Promise<PitchProgram[]> {
  const result = await fetchJson("/api/pitch-engine/programs?debug=1");
  return parseOrThrow(
    PitchProgramSchema.array(),
    result,
    {
      resource: "pitch-engine.programs",
      operation: "client-fetch"
    }
  );
}

export async function createProgram(input: {
  readonly name: string;
  readonly description: string;
  readonly owner: string;
}): Promise<PitchProgram> {
  const result = await fetchJson("/api/pitch-engine/programs?debug=1", {
    method: "POST",
    body: JSON.stringify({ action: "create", ...input })
  });

  return parseOrThrow(PitchProgramSchema, result, {
    resource: "pitch-engine.program-create",
    operation: "client-fetch"
  });
}

export async function importProgram(program: PitchProgram): Promise<PitchProgram> {
  const result = await fetchJson("/api/pitch-engine/programs?debug=1", {
    method: "POST",
    body: JSON.stringify({ action: "import", program })
  });

  return parseOrThrow(PitchProgramSchema, result, {
    resource: "pitch-engine.program-import",
    operation: "client-fetch"
  });
}

export async function updateProgram(programId: string, program: PitchProgram): Promise<PitchProgram> {
  const result = await fetchJson(`/api/pitch-engine/programs/${programId}?debug=1`, {
    method: "PUT",
    body: JSON.stringify({ program })
  });

  return parseOrThrow(PitchProgramSchema, result, {
    resource: "pitch-engine.program-update",
    operation: "client-fetch"
  });
}

export async function deleteProgram(programId: string): Promise<{ readonly ok: true }> {
  const result = await fetchJson(`/api/pitch-engine/programs/${programId}?debug=1`, {
    method: "DELETE"
  });

  return result as { readonly ok: true };
}

export async function fetchOperatorStatus(): Promise<OperatorHudStatus> {
  const result = await fetchJson("/api/pitch-engine/status?debug=1");
  return parseOrThrow(OperatorHudStatusSchema, result, {
    resource: "pitch-engine.operator-status",
    operation: "client-fetch"
  });
}

export async function fetchArtifactRuns(): Promise<ArtifactRunIndex[]> {
  const result = await fetchJson("/api/pitch-engine/artifacts?debug=1");
  return parseOrThrow(ArtifactRunIndexSchema.array(), result, {
    resource: "pitch-engine.artifacts",
    operation: "client-fetch"
  });
}

export async function triageAction(request: TriageActionRequest): Promise<TriageActionResult> {
  parseOrThrow(TriageActionRequestSchema, request, {
    resource: "pitch-engine.triage-request",
    operation: "client-validate"
  });

  const result = await fetchJson("/api/pitch-engine/triage?debug=1", {
    method: "POST",
    body: JSON.stringify(request)
  });

  return result as TriageActionResult;
}

export async function exportSupportBundle(payload: {
  readonly selectedProgramId: string | null;
  readonly selectedSceneId: string | null;
  readonly selectedSequenceId: string | null;
  readonly links: string[];
  readonly capabilityStatus: CapabilityStatus;
  readonly operatorHud: OperatorHudStatus;
  readonly environment: {
    readonly userAgent: string;
    readonly viewport: {
      readonly width: number;
      readonly height: number;
      readonly dpr: number;
    };
    readonly flags: string[];
  };
}): Promise<SupportBundle> {
  const result = await fetchJson("/api/pitch-engine/support-bundle?debug=1", {
    method: "POST",
    body: JSON.stringify(payload)
  });

  return result as SupportBundle;
}
