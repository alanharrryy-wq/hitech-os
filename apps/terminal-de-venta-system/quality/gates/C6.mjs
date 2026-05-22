import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { customerSnapshot, diffSnapshots, loadPreviousCustomerSnapshot, writeRunJson } from '../core/customer-assurance.mjs';

export const gateId = 'C6';
export const title = 'Operational Drift Watchdog';

export async function run(ctx) {
  const snapshot = customerSnapshot(ctx);
  writeRunJson(ctx, 'CUSTOMER_ASSURANCE_SNAPSHOT.json', snapshot);
  const previous = loadPreviousCustomerSnapshot(ctx);
  const diff = previous.found ? diffSnapshots(previous.snapshot, snapshot) : { compared: false, changed: [], added: [], removed: [] };
  const evidence = [createEvidence(ctx, 'C6', 'operational_drift_snapshot', 'Critical customer readiness fingerprint and drift comparison', {
    currentSnapshot: snapshot,
    previousRunDir: previous.runDir,
    previousFound: previous.found,
    previousError: previous.error || null,
    diff
  })];
  const findings = [];
  if (!previous.found) {
    findings.push(finding({
      id: 'C6_NO_PREVIOUS_BASELINE',
      severity: 'S4',
      layer: 'Quality',
      title: 'No previous customer readiness baseline found',
      detail: 'This is expected on the first customer assurance run. The current run writes CUSTOMER_ASSURANCE_SNAPSHOT.json for future comparisons.',
      evidence,
      recommendation: 'Keep this run directory as the baseline if the rest of the profile is acceptable.'
    }));
  }
  for (const file of diff.changed || []) {
    findings.push(finding({
      id: `C6_CHANGED_${file.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: 'S3',
      layer: 'Quality',
      title: 'Critical customer readiness file changed since last baseline',
      detail: `${file} changed compared with the previous CUSTOMER_ASSURANCE_SNAPSHOT.json.`,
      file,
      evidence,
      recommendation: 'Review the change. If intentional, keep the new run as the next baseline.'
    }));
  }
  for (const file of diff.removed || []) {
    findings.push(finding({
      id: `C6_REMOVED_${file.replace(/[^A-Za-z0-9]+/g, '_')}`,
      severity: 'S2',
      layer: 'Quality',
      title: 'Critical customer readiness file disappeared since last baseline',
      detail: `${file} existed in the previous baseline and is missing now.`,
      file,
      evidence,
      recommendation: 'Restore the file or document the intentional removal before customer promotion.'
    }));
  }
  return {
    gateId: 'C6',
    title,
    status: findings.some((item) => ['S0', 'S1'].includes(item.severity)) ? 'BLOCKED' : findings.length ? 'READY_WITH_WARNINGS' : 'READY',
    summary: previous.found ? `${(diff.changed || []).length} changed, ${(diff.added || []).length} added, ${(diff.removed || []).length} removed critical files since previous baseline.` : 'Baseline created for future drift detection.',
    findings,
    evidence
  };
}
