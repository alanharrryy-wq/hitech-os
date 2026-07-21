import type { UpstreamProbe } from "../mobile-data-plane/types";

const URL_PATTERN = /\bhttps?:\/\/[^\s)"']+/gi;
const IPV4_PATTERN = /\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b/g;
const WINDOWS_PATH_PATTERN = /\b[A-Za-z]:\\[^\r\n|]+/g;
const LOOPBACK_PATTERN = /\b(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?\b/gi;

export function sanitizeMobileDiagnosticText(value: string | null | undefined): string | undefined {
  if (!value) return undefined;
  return value
    .replace(URL_PATTERN, "[source]")
    .replace(IPV4_PATTERN, "[address]")
    .replace(WINDOWS_PATH_PATTERN, "[local-path]")
    .replace(LOOPBACK_PATTERN, "[loopback]")
    .slice(0, 320);
}

export function sanitizeMobileWarnings(values: string[]): string[] {
  return Array.from(
    new Set(
      values
        .map((value) => sanitizeMobileDiagnosticText(value))
        .filter((value): value is string => Boolean(value))
    )
  );
}

export function sanitizeMobileProbes(probes: UpstreamProbe[]): UpstreamProbe[] {
  return probes.map((probe) => ({
    id: probe.id,
    ok: probe.ok,
    url: `source://${probe.id}`,
    ...(probe.status === undefined ? {} : { status: probe.status }),
    ...(probe.latencyMs === undefined ? {} : { latencyMs: probe.latencyMs }),
    ...(probe.error ? { error: sanitizeMobileDiagnosticText(probe.error) } : {})
  }));
}
