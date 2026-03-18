export interface SmokeCheckResult {
  readonly id: string;
  readonly passed: boolean;
  readonly details: string;
}

export function evaluateSmokeChecks(paths: Readonly<Record<string, boolean>>): readonly SmokeCheckResult[] {
  return Object.entries(paths).map(([id, passed]) => ({
    id,
    passed,
    details: passed ? "present" : "missing"
  }));
}
