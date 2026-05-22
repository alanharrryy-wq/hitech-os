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
  if (profile === 'automation') decision = 'READY_TO_AUTOMATION';
  if (profile === 'phase5') decision = 'READY_TO_PHASE5';
  if (profile === 'client-readiness') decision = 'READY_FOR_CUSTOMER_PROMOTION';
  if (profile === 'demo') decision = 'READY_FOR_CUSTOMER_DEMO';
  if (profile === 'first-run') decision = 'READY_FOR_FIRST_RUN';
  if (profile === 'support-pack') decision = 'CUSTOMER_SUPPORT_PACK_READY';
  if (profile === 'upgrade') decision = 'READY_FOR_CUSTOMER_UPGRADE';
  if (profile === 'pilot') decision = 'READY_FOR_CUSTOMER_PILOT';

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
