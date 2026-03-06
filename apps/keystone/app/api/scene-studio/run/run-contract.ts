export interface SceneStudioRunPayload {
  readonly sceneIds: readonly string[];
  readonly mode: "smoke" | "full";
  readonly updateBaseline: boolean;
  readonly routeFilter: string | null;
  readonly tags: readonly string[];
  readonly strict: boolean;
  readonly strictThreshold: string | null;
  readonly serverMode: "dev" | "prod";
  readonly timeoutMs: number;
  readonly passthroughArgs: readonly string[];
}

export type ParsedSceneStudioRunPayload =
  | {
      readonly ok: true;
      readonly payload: SceneStudioRunPayload;
    }
  | {
      readonly ok: false;
      readonly error: string;
    };

interface ParsedValue<T> {
  readonly ok: true;
  readonly value: T;
}

interface ParsedError {
  readonly ok: false;
  readonly error: string;
}

const DEFAULT_TIMEOUT_MS = 300_000;
const MIN_TIMEOUT_MS = 5_000;
const MAX_TIMEOUT_MS = 900_000;

function uniqueNonEmptyStrings(values: readonly string[]): string[] {
  const unique = new Set<string>();

  for (const value of values) {
    const normalized = value.trim();
    if (normalized.length > 0) {
      unique.add(normalized);
    }
  }

  return [...unique];
}

function parseStringArray(value: unknown, fieldName: string): ParsedValue<string[]> | ParsedError {
  if (value === undefined) {
    return { ok: true, value: [] };
  }

  if (!Array.isArray(value) || value.some((entry) => typeof entry !== "string")) {
    return { ok: false, error: `Field "${fieldName}" must be an array of strings.` };
  }

  return { ok: true, value: uniqueNonEmptyStrings(value as string[]) };
}

function parseOptionalString(value: unknown, fieldName: string): ParsedValue<string | null> | ParsedError {
  if (value === undefined || value === null) {
    return { ok: true, value: null };
  }

  if (typeof value !== "string") {
    return { ok: false, error: `Field "${fieldName}" must be a string.` };
  }

  const normalized = value.trim();
  return { ok: true, value: normalized.length > 0 ? normalized : null };
}

function parseTimeoutMs(value: unknown): ParsedValue<number> | ParsedError {
  if (value === undefined) {
    return { ok: true, value: DEFAULT_TIMEOUT_MS };
  }

  if (typeof value !== "number" || !Number.isFinite(value)) {
    return { ok: false, error: 'Field "timeoutMs" must be a finite number.' };
  }

  const rounded = Math.round(value);
  if (rounded < MIN_TIMEOUT_MS || rounded > MAX_TIMEOUT_MS) {
    return {
      ok: false,
      error: `Field "timeoutMs" must be between ${MIN_TIMEOUT_MS} and ${MAX_TIMEOUT_MS}.`
    };
  }

  return { ok: true, value: rounded };
}

function defaultPayload(): SceneStudioRunPayload {
  return {
    sceneIds: [],
    mode: "smoke",
    updateBaseline: false,
    routeFilter: null,
    tags: [],
    strict: false,
    strictThreshold: null,
    serverMode: "dev",
    timeoutMs: DEFAULT_TIMEOUT_MS,
    passthroughArgs: []
  };
}

export function parseSceneStudioRunPayload(payload: unknown): ParsedSceneStudioRunPayload {
  if (payload === undefined || payload === null) {
    return { ok: true, payload: defaultPayload() };
  }

  if (typeof payload !== "object" || Array.isArray(payload)) {
    return { ok: false, error: "Payload must be a JSON object." };
  }

  const candidate = payload as Record<string, unknown>;

  const sceneIds = parseStringArray(candidate["sceneIds"], "sceneIds");
  if (!sceneIds.ok) {
    return sceneIds;
  }

  const tags = parseStringArray(candidate["tags"] ?? candidate["sceneTags"], "tags");
  if (!tags.ok) {
    return tags;
  }

  const passthroughArgs = parseStringArray(candidate["passthroughArgs"], "passthroughArgs");
  if (!passthroughArgs.ok) {
    return passthroughArgs;
  }

  const routeFilter = parseOptionalString(candidate["route"], "route");
  if (!routeFilter.ok) {
    return routeFilter;
  }

  const strictThreshold = parseOptionalString(candidate["strictThreshold"], "strictThreshold");
  if (!strictThreshold.ok) {
    return strictThreshold;
  }

  const timeoutMs = parseTimeoutMs(candidate["timeoutMs"]);
  if (!timeoutMs.ok) {
    return timeoutMs;
  }

  return {
    ok: true,
    payload: {
      sceneIds: sceneIds.value,
      mode: candidate["mode"] === "full" ? "full" : "smoke",
      updateBaseline: candidate["updateBaseline"] === true,
      routeFilter: routeFilter.value,
      tags: tags.value,
      strict: candidate["strict"] === true,
      strictThreshold: strictThreshold.value,
      serverMode: candidate["serverMode"] === "prod" ? "prod" : "dev",
      timeoutMs: timeoutMs.value,
      passthroughArgs: passthroughArgs.value
    }
  };
}

export function buildSceneStudioRunnerArgs(
  runnerScriptPath: string,
  payload: SceneStudioRunPayload
): string[] {
  const args: string[] = [runnerScriptPath, "--json", `--server-mode=${payload.serverMode}`];

  if (payload.mode === "smoke") {
    args.push("--smoke");
  }

  if (payload.mode === "full") {
    args.push("--full");
  }

  args.push(`--timeout-ms=${payload.timeoutMs}`);

  if (payload.updateBaseline) {
    args.push("--update-baseline");
  }

  if (payload.strict) {
    args.push("--strict");
  }

  if (payload.strictThreshold) {
    args.push(`--strict-threshold=${payload.strictThreshold}`);
  }

  if (payload.routeFilter) {
    args.push(`--route=${payload.routeFilter}`);
  }

  for (const sceneId of payload.sceneIds) {
    args.push(`--scene-id=${sceneId}`);
  }

  for (const tag of payload.tags) {
    args.push(`--tag=${tag}`);
  }

  if (payload.passthroughArgs.length > 0) {
    args.push("--", ...payload.passthroughArgs);
  }

  return args;
}
