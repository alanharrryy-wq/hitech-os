import { summarizeFindings } from './severity.mjs';
export function decide(profile, gateResults) {
  const findings = gateResults.flatMap(g => g.findings || []);
  const summary = summarizeFindings(findings, profile);
  const errored = gateResults.some(g => g.status === 'ERROR');
  const blockedGate = gateResults.some(g => g.status === 'BLOCKED');
  let decision = profile === 'pr' ? 'READY_TO_PR' : profile === 'release' ? 'READY_TO_RELEASE' : profile === 'diagnose' ? 'DIAGNOSIS_READY' : profile === 'watch' ? 'WATCHING' : 'READY_TO_COMMIT';
  if (summary.blockers.length || errored || blockedGate) decision = 'BLOCKED';
  return { schemaVersion: '1.0', profile, decision, status: summary.warnings.length ? 'READY_WITH_WARNINGS' : 'READY', exitCode: decision === 'BLOCKED' ? 1 : 0, blockerCount: summary.blockers.length, warningCount: summary.warnings.length, infoCount: summary.info.length, worstSeverity: summary.worst, blockers: summary.blockers, warnings: summary.warnings };
}
