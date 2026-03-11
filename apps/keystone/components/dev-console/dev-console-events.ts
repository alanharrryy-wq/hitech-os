"use client";

export const DEV_CONSOLE_DIAGNOSTICS_EVENT = "hitech:dev-console:diagnostics";
export const DEV_CONSOLE_REQUEST_DIAGNOSTICS_EVENT = "hitech:dev-console:request-diagnostics";
export const DEV_CONSOLE_FLAGS_EVENT = "hitech:dev-console:flags";
export const DEV_CONSOLE_SNAPSHOT_EVENT = "hitech:dev-console:snapshot";
export const DEV_CONSOLE_OPEN_SCENE_EVENT = "hitech:dev-console:open-scene";
export const DEV_CONSOLE_VALIDATE_SCENE_EVENT = "hitech:dev-console:validate-scene";
export const DEV_CONSOLE_ACTION_RESULT_EVENT = "hitech:dev-console:action-result";
export const DEV_CONSOLE_SCENE_LOOK_MODEL_EVENT = "hitech:dev-console:scene-look-model";

export type DevConsoleActionName =
  | "snapshot"
  | "open-scene"
  | "validate-scene"
  | "toggle-scene-group"
  | "refresh-diagnostics";

export interface DevConsoleActionResult {
  readonly action: DevConsoleActionName;
  readonly ok: boolean;
  readonly message: string;
  readonly at: string;
  readonly requestId?: string;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export function dispatchDevConsoleActionResult(detail: DevConsoleActionResult) {
  if (typeof window === "undefined") {
    return;
  }
  window.dispatchEvent(
    new CustomEvent<DevConsoleActionResult>(DEV_CONSOLE_ACTION_RESULT_EVENT, {
      detail
    })
  );
}

export function normalizeRoutePath(value: string | null | undefined): string {
  if (!value) {
    return "/pitch";
  }
  return value.startsWith("/") ? value : `/${value}`;
}

export function normalizeQueryString(value: string | null | undefined): string {
  if (!value) {
    return "";
  }
  return value.startsWith("?") ? value.slice(1) : value;
}

export function buildCanonicalPath(route: string | null | undefined, query: string | null | undefined): string {
  const normalizedRoute = normalizeRoutePath(route);
  const normalizedQuery = normalizeQueryString(query);
  return normalizedQuery.length > 0 ? `${normalizedRoute}?${normalizedQuery}` : normalizedRoute;
}
