import { summarizeFindings } from './severity.mjs';

export function decide(profile, gateResults) {
  const findings = gateResults.flatMap(g => g.findings || []);
  const summary = summarizeFindings(findings, profile);
  const errored = gateResults.some(g => g.status === 'ERROR');
  const blockedGate = gateResults.some(g => g.status === 'BLOCKED');

  let decision = 'READY_TO_COMMIT';

  if (profile === 'pr') decision = 'READY_TO_PR';
  if (profile === 'release') decision = 'READY_TO_RELEASE';
  if (profile === 'runtime') decision = 'READY_TO_RUNTIME';
  if (profile === 'scenario') decision = 'READY_TO_SCENARIO';
  if (profile === 'phase3') decision = 'READY_TO_SCENARIO';
  if (profile === 'cloudflare') decision = 'READY_TO_CLOUDFLARE_CHECK';
  if (profile === 'diagnose') decision = 'DIAGNOSIS_READY';
  if (profile === 'watch') decision = 'WATCHING';

  if (summary.blockers.length || errored || blockedGate) decision = 'BLOCKED';

  const exitCode = decision === 'BLOCKED' ? 1 : 0;

  return {
    schemaVersion: '1.0',
    profile,
    decision,
    status: summary.warnings.length ? 'READY_WITH_WARNINGS' : 'READY',
    exitCode,
    blockerCount: summary.blockers.length,
    warningCount: summary.warnings.length,
    infoCount: summary.info.length,
    worstSeverity: summary.worst,
    blockers: summary.blockers,
    warnings: summary.warnings
  };
}
