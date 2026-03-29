import { WINDOW_LAYOUT_VERSION, type WindowLayout, type WindowLayoutEntry } from "./types";

export const ACTIVE_LAYOUT_STORAGE_KEY = "keystone:studio:layout:active";
export const PRESETS_STORAGE_KEY = "keystone:studio:layout:presets";
export const LAST_PRESET_STORAGE_KEY = "keystone:studio:layout:lastPreset";
const LEGACY_IMPORTED_STORAGE_KEY = "keystone:studio:layout:legacyImported";

const LEGACY_LAYOUT_KEYS = [
  "keystone:studio:floating-windows",
  "keystone:scene-studio:floating-windows",
  "keystone:scene-studio:layout",
  "keystone:studio:windows"
] as const;

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function asFiniteNumber(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return null;
  }

  return value;
}

function asBoolean(value: unknown): boolean | null {
  if (typeof value === "boolean") {
    return value;
  }

  return null;
}

function parseEntry(value: unknown): WindowLayoutEntry | null {
  if (!isRecord(value)) {
    return null;
  }

  const x = asFiniteNumber(value["x"]);
  const y = asFiniteNumber(value["y"]);
  const w = asFiniteNumber(value["w"] ?? value["width"]);
  const h = asFiniteNumber(value["h"] ?? value["height"]);
  const z = asFiniteNumber(value["z"]) ?? 1000;
  const visible = asBoolean(value["visible"]) ?? true;
  const collapsed = asBoolean(value["collapsed"]) ?? false;

  if (x === null || y === null || w === null || h === null) {
    return null;
  }

  return {
    x,
    y,
    w,
    h,
    z,
    visible,
    collapsed
  };
}

function parseWindowsRecord(input: unknown): Record<string, WindowLayoutEntry> | null {
  if (!isRecord(input)) {
    return null;
  }

  const entries: Array<[string, WindowLayoutEntry]> = [];

  for (const [windowId, value] of Object.entries(input)) {
    const parsed = parseEntry(value);
    if (!parsed) {
      continue;
    }

    entries.push([windowId, parsed]);
  }

  if (entries.length === 0) {
    return null;
  }

  return Object.fromEntries(entries);
}

function parseLayout(input: unknown): WindowLayout | null {
  if (!isRecord(input)) {
    return null;
  }

  const version = input["version"];
  const preset = input["preset"];
  const windows = parseWindowsRecord(input["windows"]);

  if (version !== WINDOW_LAYOUT_VERSION || typeof preset !== "string" || !windows) {
    return null;
  }

  return {
    version: WINDOW_LAYOUT_VERSION,
    preset,
    windows
  };
}

function safeGetItem(storageKey: string): string | null {
  if (!canUseStorage()) {
    return null;
  }

  try {
    return window.localStorage.getItem(storageKey);
  } catch {
    return null;
  }
}

function safeSetItem(storageKey: string, value: string): void {
  if (!canUseStorage()) {
    return;
  }

  try {
    window.localStorage.setItem(storageKey, value);
  } catch {
    // Ignore localStorage failures.
  }
}

export function loadActiveLayout(): WindowLayout | null {
  const raw = safeGetItem(ACTIVE_LAYOUT_STORAGE_KEY);
  if (!raw) {
    return null;
  }

  try {
    const parsed = JSON.parse(raw) as unknown;
    return parseLayout(parsed);
  } catch {
    return null;
  }
}

export function saveActiveLayout(layout: WindowLayout): void {
  safeSetItem(ACTIVE_LAYOUT_STORAGE_KEY, JSON.stringify(layout));
}

export function loadCustomPresets(): Record<string, WindowLayout> {
  const raw = safeGetItem(PRESETS_STORAGE_KEY);
  if (!raw) {
    return {};
  }

  try {
    const parsed = JSON.parse(raw) as unknown;
    if (!isRecord(parsed)) {
      return {};
    }

    const entries: Array<[string, WindowLayout]> = [];

    for (const [presetId, value] of Object.entries(parsed)) {
      const parsedLayout = parseLayout(value);
      if (!parsedLayout) {
        continue;
      }

      entries.push([presetId, parsedLayout]);
    }

    return Object.fromEntries(entries);
  } catch {
    return {};
  }
}

export function saveCustomPresets(presets: Record<string, WindowLayout>): void {
  safeSetItem(PRESETS_STORAGE_KEY, JSON.stringify(presets));
}

export function loadLastPreset(): string | null {
  const value = safeGetItem(LAST_PRESET_STORAGE_KEY);
  if (!value || value.trim().length === 0) {
    return null;
  }

  return value;
}

export function saveLastPreset(presetId: string): void {
  if (presetId.trim().length === 0) {
    return;
  }

  safeSetItem(LAST_PRESET_STORAGE_KEY, presetId);
}

function parseLegacyLayout(input: unknown): WindowLayout | null {
  if (isRecord(input) && "windows" in input) {
    const parsed = parseLayout(input);
    if (parsed) {
      return parsed;
    }
  }

  const windows = parseWindowsRecord(input);
  if (!windows) {
    return null;
  }

  return {
    version: WINDOW_LAYOUT_VERSION,
    preset: "debug",
    windows
  };
}

export function loadLegacyLayoutOnce(): WindowLayout | null {
  const alreadyImported = safeGetItem(LEGACY_IMPORTED_STORAGE_KEY) === "1";
  if (alreadyImported) {
    return null;
  }

  for (const key of LEGACY_LAYOUT_KEYS) {
    const raw = safeGetItem(key);
    if (!raw) {
      continue;
    }

    try {
      const parsed = JSON.parse(raw) as unknown;
      const legacy = parseLegacyLayout(parsed);
      if (legacy) {
        safeSetItem(LEGACY_IMPORTED_STORAGE_KEY, "1");
        return legacy;
      }
    } catch {
      continue;
    }
  }

  safeSetItem(LEGACY_IMPORTED_STORAGE_KEY, "1");
  return null;
}

export function parseLayoutJson(raw: string): WindowLayout | null {
  try {
    const parsed = JSON.parse(raw) as unknown;
    return parseLayout(parsed);
  } catch {
    return null;
  }
}

export function stringifyLayout(layout: WindowLayout): string {
  return `${JSON.stringify(layout, null, 2)}\n`;
}
