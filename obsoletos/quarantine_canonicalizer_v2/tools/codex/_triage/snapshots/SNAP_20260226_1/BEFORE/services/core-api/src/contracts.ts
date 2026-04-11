export type JsonPrimitive = string | number | boolean | null;
export type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

export interface FeatureFlags {
  enableAiExecution: boolean;
  enableCapabilitiesProxy: boolean;
  enableExperimentalUi: boolean;
  enableHealthDashboard: boolean;
}

export const FEATURE_FLAGS_DEFAULTS: FeatureFlags = Object.freeze({
  enableAiExecution: false,
  enableCapabilitiesProxy: false,
  enableExperimentalUi: false,
  enableHealthDashboard: false
});

export type JobKind = "echo" | "summarize_text" | "extract_keywords";
export type JobStatus = "queued" | "running" | "completed" | "failed";
export type LogLevel = "info" | "warn" | "error";
export type HealthStatus = "ok" | "degraded" | "error";

export interface JobRequest {
  jobId: string;
  kind: JobKind;
  input: Record<string, JsonValue>;
  requestedAtUtc: string;
  flags: FeatureFlags;
}

export interface StructuredLog {
  seq: number;
  level: LogLevel;
  event: string;
  message: string;
  atUtc: string;
  details: Record<string, JsonValue>;
}

export interface JobResult {
  jobId: string;
  kind: JobKind;
  status: JobStatus;
  output: Record<string, JsonValue>;
  logs: StructuredLog[];
  finishedAtUtc: string | null;
}

export interface AgentCapabilities {
  serviceName: "ai-agent";
  version: string;
  protocolVersion: string;
  deterministic: true;
  supportedJobKinds: JobKind[];
  maxInputChars: number;
  defaults: FeatureFlags;
  notes: string[];
}

export interface HealthCheck {
  name: string;
  status: HealthStatus;
  message: string;
}

export interface HealthReport {
  service: string;
  version: string;
  contractVersion: string;
  status: HealthStatus;
  timestampUtc: string;
  checks: HealthCheck[];
}

export interface ValidationFailure {
  path: string;
  message: string;
}

export interface ValidationResult<T> {
  ok: boolean;
  value?: T;
  issues: ValidationFailure[];
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isJsonValue(value: unknown, depth = 0): value is JsonValue {
  if (depth > 30) {
    return false;
  }

  if (value === null) {
    return true;
  }

  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return Number.isFinite(value as number) || typeof value !== "number";
  }

  if (Array.isArray(value)) {
    return value.every((item) => isJsonValue(item, depth + 1));
  }

  if (isObject(value)) {
    return Object.values(value).every((entry) => isJsonValue(entry, depth + 1));
  }

  return false;
}

function normalizeIsoDate(input: string): string | null {
  const parsed = new Date(input);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return parsed.toISOString();
}

function normalizeStringArray(input: unknown): string[] | null {
  if (!Array.isArray(input)) {
    return null;
  }

  if (!input.every((item) => typeof item === "string" && item.trim().length > 0)) {
    return null;
  }

  return input.map((item) => item.trim()).sort((left, right) => left.localeCompare(right));
}

export function normalizeFeatureFlags(input: unknown): FeatureFlags {
  if (!isObject(input)) {
    return { ...FEATURE_FLAGS_DEFAULTS };
  }

  return {
    enableAiExecution: Boolean(input.enableAiExecution ?? FEATURE_FLAGS_DEFAULTS.enableAiExecution),
    enableCapabilitiesProxy: Boolean(input.enableCapabilitiesProxy ?? FEATURE_FLAGS_DEFAULTS.enableCapabilitiesProxy),
    enableExperimentalUi: Boolean(input.enableExperimentalUi ?? FEATURE_FLAGS_DEFAULTS.enableExperimentalUi),
    enableHealthDashboard: Boolean(input.enableHealthDashboard ?? FEATURE_FLAGS_DEFAULTS.enableHealthDashboard)
  };
}

export function validateJobRequest(input: unknown): ValidationResult<JobRequest> {
  const issues: ValidationFailure[] = [];

  if (!isObject(input)) {
    return {
      ok: false,
      issues: [{ path: "$", message: "job request must be an object" }]
    };
  }

  const rawJobId = input.jobId;
  const rawKind = input.kind;
  const rawInput = input.input;
  const rawRequestedAtUtc = input.requestedAtUtc;
  const rawFlags = input.flags;

  if (typeof rawJobId !== "string" || rawJobId.trim().length === 0) {
    issues.push({ path: "jobId", message: "jobId must be a non-empty string" });
  }

  const allowedKinds: JobKind[] = ["echo", "summarize_text", "extract_keywords"];
  if (typeof rawKind !== "string" || !allowedKinds.includes(rawKind as JobKind)) {
    issues.push({ path: "kind", message: "kind must be one of echo, summarize_text, extract_keywords" });
  }

  if (!isObject(rawInput)) {
    issues.push({ path: "input", message: "input must be an object" });
  } else {
    for (const [key, value] of Object.entries(rawInput)) {
      if (!isJsonValue(value)) {
        issues.push({ path: `input.${key}`, message: "input values must be JSON-compatible" });
      }
    }
  }

  if (typeof rawRequestedAtUtc !== "string" || normalizeIsoDate(rawRequestedAtUtc) === null) {
    issues.push({ path: "requestedAtUtc", message: "requestedAtUtc must be a valid ISO UTC date string" });
  }

  if (issues.length > 0) {
    return { ok: false, issues };
  }

  const normalizedInput: Record<string, JsonValue> = {};
  for (const key of Object.keys(rawInput as Record<string, JsonValue>).sort((left, right) => left.localeCompare(right))) {
    normalizedInput[key] = (rawInput as Record<string, JsonValue>)[key];
  }

  return {
    ok: true,
    value: {
      jobId: (rawJobId as string).trim(),
      kind: rawKind as JobKind,
      input: normalizedInput,
      requestedAtUtc: normalizeIsoDate(rawRequestedAtUtc as string) ?? new Date(0).toISOString(),
      flags: normalizeFeatureFlags(rawFlags)
    },
    issues
  };
}

export function validateAgentCapabilities(input: unknown): ValidationResult<AgentCapabilities> {
  const issues: ValidationFailure[] = [];

  if (!isObject(input)) {
    return {
      ok: false,
      issues: [{ path: "$", message: "capabilities response must be an object" }]
    };
  }

  const serviceName = input.serviceName;
  const version = input.version;
  const protocolVersion = input.protocolVersion;
  const deterministic = input.deterministic;
  const supportedJobKinds = normalizeStringArray(input.supportedJobKinds);
  const maxInputChars = input.maxInputChars;
  const defaults = normalizeFeatureFlags(input.defaults);
  const notes = normalizeStringArray(input.notes);

  if (serviceName !== "ai-agent") {
    issues.push({ path: "serviceName", message: "serviceName must equal ai-agent" });
  }
  if (typeof version !== "string" || version.trim().length === 0) {
    issues.push({ path: "version", message: "version must be a non-empty string" });
  }
  if (typeof protocolVersion !== "string" || protocolVersion.trim().length === 0) {
    issues.push({ path: "protocolVersion", message: "protocolVersion must be a non-empty string" });
  }
  if (deterministic !== true) {
    issues.push({ path: "deterministic", message: "deterministic must be true" });
  }
  if (supportedJobKinds === null) {
    issues.push({ path: "supportedJobKinds", message: "supportedJobKinds must be a non-empty string array" });
  }
  if (typeof maxInputChars !== "number" || !Number.isInteger(maxInputChars) || maxInputChars <= 0) {
    issues.push({ path: "maxInputChars", message: "maxInputChars must be a positive integer" });
  }
  if (notes === null) {
    issues.push({ path: "notes", message: "notes must be a non-empty string array" });
  }

  if (issues.length > 0) {
    return { ok: false, issues };
  }

  return {
    ok: true,
    value: {
      serviceName: "ai-agent",
      version: version as string,
      protocolVersion: protocolVersion as string,
      deterministic: true,
      supportedJobKinds: supportedJobKinds as JobKind[],
      maxInputChars: maxInputChars as number,
      defaults,
      notes: notes as string[]
    },
    issues
  };
}

export function validateJobResult(input: unknown): ValidationResult<JobResult> {
  const issues: ValidationFailure[] = [];

  if (!isObject(input)) {
    return {
      ok: false,
      issues: [{ path: "$", message: "job result must be an object" }]
    };
  }

  const rawJobId = input.jobId;
  const rawKind = input.kind;
  const rawStatus = input.status;
  const rawOutput = input.output;
  const rawLogs = input.logs;
  const rawFinishedAtUtc = input.finishedAtUtc;

  if (typeof rawJobId !== "string" || rawJobId.trim().length === 0) {
    issues.push({ path: "jobId", message: "jobId must be a non-empty string" });
  }

  const allowedKinds: JobKind[] = ["echo", "summarize_text", "extract_keywords"];
  if (typeof rawKind !== "string" || !allowedKinds.includes(rawKind as JobKind)) {
    issues.push({ path: "kind", message: "kind must be one of echo, summarize_text, extract_keywords" });
  }

  const allowedStatus: JobStatus[] = ["queued", "running", "completed", "failed"];
  if (typeof rawStatus !== "string" || !allowedStatus.includes(rawStatus as JobStatus)) {
    issues.push({ path: "status", message: "status must be queued/running/completed/failed" });
  }

  if (!isObject(rawOutput)) {
    issues.push({ path: "output", message: "output must be an object" });
  } else {
    for (const [key, value] of Object.entries(rawOutput)) {
      if (!isJsonValue(value)) {
        issues.push({ path: `output.${key}`, message: "output values must be JSON-compatible" });
      }
    }
  }

  if (!Array.isArray(rawLogs)) {
    issues.push({ path: "logs", message: "logs must be an array" });
  } else {
    for (const [index, entry] of rawLogs.entries()) {
      if (!isObject(entry)) {
        issues.push({ path: `logs.${index}`, message: "log entry must be an object" });
        continue;
      }

      const requiredKeys = ["seq", "level", "event", "message", "atUtc", "details"] as const;
      for (const key of requiredKeys) {
        if (!(key in entry)) {
          issues.push({ path: `logs.${index}.${key}`, message: "missing required field" });
        }
      }

      if (typeof entry.seq !== "number" || !Number.isInteger(entry.seq) || entry.seq < 0) {
        issues.push({ path: `logs.${index}.seq`, message: "seq must be a non-negative integer" });
      }

      const levels = ["info", "warn", "error"];
      if (typeof entry.level !== "string" || !levels.includes(entry.level)) {
        issues.push({ path: `logs.${index}.level`, message: "level must be info/warn/error" });
      }

      if (typeof entry.event !== "string" || entry.event.trim().length === 0) {
        issues.push({ path: `logs.${index}.event`, message: "event must be non-empty" });
      }

      if (typeof entry.message !== "string" || entry.message.trim().length === 0) {
        issues.push({ path: `logs.${index}.message`, message: "message must be non-empty" });
      }

      if (typeof entry.atUtc !== "string" || normalizeIsoDate(entry.atUtc) === null) {
        issues.push({ path: `logs.${index}.atUtc`, message: "atUtc must be valid ISO date" });
      }

      if (!isObject(entry.details)) {
        issues.push({ path: `logs.${index}.details`, message: "details must be an object" });
      }
    }
  }

  if (rawFinishedAtUtc !== null && (typeof rawFinishedAtUtc !== "string" || normalizeIsoDate(rawFinishedAtUtc) === null)) {
    issues.push({ path: "finishedAtUtc", message: "finishedAtUtc must be null or valid ISO date" });
  }

  if (issues.length > 0) {
    return { ok: false, issues };
  }

  const normalizedOutput: Record<string, JsonValue> = {};
  for (const key of Object.keys(rawOutput as Record<string, JsonValue>).sort((left, right) => left.localeCompare(right))) {
    normalizedOutput[key] = (rawOutput as Record<string, JsonValue>)[key];
  }

  const normalizedLogs = [...(rawLogs as StructuredLog[])].sort((left, right) => left.seq - right.seq);

  return {
    ok: true,
    value: {
      jobId: (rawJobId as string).trim(),
      kind: rawKind as JobKind,
      status: rawStatus as JobStatus,
      output: normalizedOutput,
      logs: normalizedLogs,
      finishedAtUtc: rawFinishedAtUtc === null ? null : normalizeIsoDate(rawFinishedAtUtc as string)
    },
    issues
  };
}

export function buildHealthReport(input: {
  service: string;
  version: string;
  contractVersion: string;
  checks: HealthCheck[];
  timestampUtc: string;
}): HealthReport {
  const checks = [...input.checks].sort((left, right) => left.name.localeCompare(right.name));
  const status = checks.some((check) => check.status === "error")
    ? "error"
    : checks.some((check) => check.status === "degraded")
      ? "degraded"
      : "ok";

  return {
    service: input.service,
    version: input.version,
    contractVersion: input.contractVersion,
    status,
    timestampUtc: normalizeIsoDate(input.timestampUtc) ?? new Date(0).toISOString(),
    checks
  };
}
