import type { EvidenceLink } from "./contracts";

const SENSITIVE_PATTERNS = [
  /authorization\s*[:=]\s*[^\s,;]+/gi,
  /bearer\s+[a-z0-9._~-]+/gi,
  /cookie\s*[:=]\s*[^\s,;]+/gi,
  /password\s*[:=]\s*[^\s,;]+/gi,
  /api[_-]?key\s*[:=]\s*[^\s,;]+/gi,
  /secret\s*[:=]\s*[^\s,;]+/gi,
  /private\s+key/gi,
  /\.env\b/gi
];

export function sanitizeEvidenceText(value: unknown): string {
  const text = String(value ?? "sin detalle").slice(0, 320);
  return SENSITIVE_PATTERNS.reduce((current, pattern) => current.replace(pattern, "[redacted]"), text);
}

export function evidence(id: string, label: string, source: string, summary: unknown): EvidenceLink {
  return {
    id,
    label,
    source,
    summary: sanitizeEvidenceText(summary),
    sensitivity: "safe"
  };
}

export function hasEvidence(evidenceItems: EvidenceLink[]): boolean {
  return evidenceItems.some((item) => item.summary.trim().length > 0 && item.sensitivity !== "redacted");
}

