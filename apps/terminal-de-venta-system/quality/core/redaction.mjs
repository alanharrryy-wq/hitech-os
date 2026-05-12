const PATTERNS = [
  /ghp_[A-Za-z0-9_]{20,}/g,
  /sk-[A-Za-z0-9_-]{20,}/g,
  /xox[baprs]-[A-Za-z0-9-]{20,}/g,
  /(authorization\s*[:=]\s*)[^\s]+/gi,
  /(password\s*[:=]\s*)[^\s]+/gi,
  /(token\s*[:=]\s*)[^\s]+/gi,
  /(secret\s*[:=]\s*)[^\s]+/gi
];
export function redact(value) {
  let s = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
  for (const pattern of PATTERNS) s = s.replace(pattern, (m, g1) => g1 ? `${g1}[REDACTED]` : '[REDACTED]');
  return s;
}
