import type { OperatorHudStatus, PitchEngineUiState } from "../types";

export const LOCAL_STORAGE_KEYS = {
  hud: "keystone.pitch-engine.hud",
  librarySelection: "keystone.pitch-engine.selection",
  capabilityRequestedMode: "keystone.pitch-engine.requested-mode",
  lastProgram: "keystone.pitch-engine.programs",
  triageZoom: "keystone.pitch-engine.triage.zoom"
} as const;

export function readJsonStorage<T>(key: string): T | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    const value = window.localStorage.getItem(key);
    if (!value) {
      return null;
    }

    return JSON.parse(value) as T;
  } catch {
    return null;
  }
}

export function writeJsonStorage<T>(key: string, value: T): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Ignore storage errors in dev-only UI.
  }
}

export function buildDefaultHudStatus(): OperatorHudStatus {
  return {
    serverStatus: "starting",
    lastRunStatus: "unknown",
    lastRunPath: null,
    lastErrorTail: null,
    lastArtifactRunId: null,
    updatedAt: new Date().toISOString()
  };
}

export function isReducedMotionPreferred(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function getDeviceMemoryGb(): number | null {
  if (typeof navigator === "undefined") {
    return null;
  }

  const navWithMemory = navigator as Navigator & { deviceMemory?: number };
  if (typeof navWithMemory.deviceMemory === "number") {
    return navWithMemory.deviceMemory;
  }

  return null;
}

export function getHardwareConcurrency(): number | null {
  if (typeof navigator === "undefined") {
    return null;
  }

  if (typeof navigator.hardwareConcurrency === "number") {
    return navigator.hardwareConcurrency;
  }

  return null;
}

export function getViewportWidth(): number {
  if (typeof window === "undefined") {
    return 1920;
  }

  return window.innerWidth;
}

export function buildEnvironmentSummary(flags: string[]): PitchEngineUiState["operatorHud"] {
  return {
    serverStatus: "ready",
    lastRunStatus: "unknown",
    lastRunPath: null,
    lastErrorTail: flags.length > 0 ? `flags:${flags.join(",")}` : null,
    lastArtifactRunId: null,
    updatedAt: new Date().toISOString()
  };
}
