import fs from 'node:fs';
import path from 'node:path';
import { sha256File } from './checksums.mjs';
import { writeJson } from './safe-json.mjs';
import { loadAutomationCatalog } from './automation-catalog.mjs';
import { validateRunOutputs } from './output-validator.mjs';

function profileMatrix(ctx) {
  const profilesDir = path.join(ctx.qualityRoot, 'profiles');
  const rows = [];
  if (!fs.existsSync(profilesDir)) return rows;
  for (const file of fs.readdirSync(profilesDir).filter((name) => name.endsWith('.json')).sort()) {
    try {
      const value = JSON.parse(fs.readFileSync(path.join(profilesDir, file), 'utf8'));
      rows.push({
        profile: value.profile || value.name || path.basename(file, '.json'),
        phase: value.phase || 'unknown',
        strict: Boolean(value.strict),
        gateCount: Array.isArray(value.gates) ? value.gates.length : 0,
        gates: value.gates || []
      });
    } catch (error) {
      rows.push({ profile: path.basename(file, '.json'), phase: 'parse-error', strict: false, gateCount: 0, gates: [], error: error?.message || String(error) });
    }
  }
  return rows;
}

function normalizeAudit(gateResults) {
  return gateResults.map((gate) => ({
    gateId: gate.gateId,
    title: gate.title,
    status: gate.status,
    legacyStatus: gate.legacyStatus || null,
    normalizedFrom: gate.normalizedFrom || null,
    findingCount: (gate.findings || []).length,
    evidenceCount: (gate.evidence || []).length,
    fakeGreenRisk: gate.status === 'READY' && (!(gate.evidence || []).length || (gate.findings || []).some((finding) => ['S0', 'S1'].includes(finding.severity)))
  }));
}

export function writeReports(ctx, gateResults, decision, envSnapshot) {
  const findings = gateResults.flatMap((gate) => gate.findings || []);
  const automationCatalog = loadAutomationCatalog(ctx.qualityRoot);
  const generatedAt = new Date().toISOString();
  const normalizationAudit = normalizeAudit(gateResults);
  const matrix = profileMatrix(ctx);
  const report = {
    schemaVersion: '1.1',
    runId: ctx.runId,
    profile: ctx.profile,
    repoRoot: ctx.repoRoot,
    qualityRoot: ctx.qualityRoot,
    generatedAt,
    decision,
    gates: gateResults,
    findings,
    automation: {
      ok: automationCatalog.ok,
      total: automationCatalog.total || 0,
      implemented: automationCatalog.implemented || 0,
      active: automationCatalog.active || 0,
      categories: automationCatalog.categories || {}
    }
  };

  const machineSummary = {
    schemaVersion: '1.0',
    runId: ctx.runId,
    profile: ctx.profile,
    generatedAt,
    decision: decision.decision,
    exitCode: decision.exitCode,
    blockerCount: decision.blockerCount,
    warningCount: decision.warningCount,
    infoCount: decision.infoCount,
    gateCount: gateResults.length,
    blockedGates: gateResults.filter((gate) => ['BLOCKED', 'ERROR'].includes(gate.status)).map((gate) => gate.gateId),
    warningGates: gateResults.filter((gate) => gate.status === 'READY_WITH_WARNINGS').map((gate) => gate.gateId),
    runDir: ctx.runDir,
    repoRoot: ctx.repoRoot
  };

  const runManifest = {
    schemaVersion: '1.0',
    runId: ctx.runId,
    generatedAt,
    profile: ctx.profile,
    repoRoot: ctx.repoRoot,
    qualityRoot: ctx.qualityRoot,
    outDir: ctx.outDir,
    runDir: ctx.runDir,
    manifestVersion: ctx.manifest?.systemVersion || 'unknown',
    phase: ctx.manifest?.phase || 'unknown',
    commandCount: (ctx.commandsRun || []).length,
    evidenceCounterFinal: ctx.evidenceCounter,
    profileGateIds: gateResults.map((gate) => gate.gateId)
  };

  writeJson(path.join(ctx.runDir, 'QUALITY_REPORT.json'), report);
  writeJson(path.join(ctx.runDir, 'QUALITY_DECISION.json'), decision);
  writeJson(path.join(ctx.runDir, 'QUALITY_FINDINGS.json'), findings);
  writeJson(path.join(ctx.runDir, 'ENVIRONMENT_SNAPSHOT.json'), envSnapshot);
  writeJson(path.join(ctx.runDir, 'COMMANDS_RUN.json'), ctx.commandsRun || []);
  writeJson(path.join(ctx.runDir, 'QUALITY_MACHINE_SUMMARY.json'), machineSummary);
  writeJson(path.join(ctx.runDir, 'QUALITY_AUTOMATION_SUMMARY.json'), automationCatalog);
  writeJson(path.join(ctx.runDir, 'QUALITY_RUN_MANIFEST.json'), runManifest);
  writeJson(path.join(ctx.runDir, 'QUALITY_PROFILE_MATRIX.json'), matrix);
  writeJson(path.join(ctx.runDir, 'QUALITY_NORMALIZATION_AUDIT.json'), normalizationAudit);

  const blockers = findings.filter((finding) => ['S0', 'S1'].includes(finding.severity) || (ctx.profile === 'release' && finding.severity === 'S2'));
  const warnings = findings.filter((finding) => ['S2', 'S3'].includes(finding.severity) && !blockers.includes(finding));
  fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_BLOCKERS.md'), markdownFindings('Blockers', blockers), 'utf8');
  fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_WARNINGS.md'), markdownFindings('Warnings', warnings), 'utf8');
  fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_REPORT.md'), markdownReport(report), 'utf8');
  fs.writeFileSync(path.join(ctx.runDir, 'PHASE_EXIT_REPORT.md'), phaseExit(report), 'utf8');
  fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_NEXT_ACTIONS.md'), nextActions(report), 'utf8');
  fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_RUN_SUMMARY.txt'), `${decision.decision}\nRun: ${ctx.runDir}\nBlockers: ${decision.blockerCount}\nWarnings: ${decision.warningCount}\n`, 'utf8');

  const validation = validateRunOutputs(ctx.runDir);
  writeJson(path.join(ctx.runDir, 'QUALITY_OUTPUT_VALIDATION.json'), validation);

  const files = [
    'QUALITY_REPORT.json',
    'QUALITY_DECISION.json',
    'QUALITY_FINDINGS.json',
    'QUALITY_EVIDENCE_LEDGER.jsonl',
    'QUALITY_REPORT.md',
    'QUALITY_BLOCKERS.md',
    'QUALITY_WARNINGS.md',
    'PHASE_EXIT_REPORT.md',
    'QUALITY_NEXT_ACTIONS.md',
    'ENVIRONMENT_SNAPSHOT.json',
    'COMMANDS_RUN.json',
    'QUALITY_MACHINE_SUMMARY.json',
    'QUALITY_AUTOMATION_SUMMARY.json',
    'QUALITY_RUN_MANIFEST.json',
    'QUALITY_PROFILE_MATRIX.json',
    'QUALITY_NORMALIZATION_AUDIT.json',
    'QUALITY_OUTPUT_VALIDATION.json',
    'QUALITY_RUN_SUMMARY.txt'
  ];
  const rows = ['file,sha256'];
  for (const file of files) {
    const filePath = path.join(ctx.runDir, file);
    if (fs.existsSync(filePath)) rows.push(`${file},${sha256File(filePath)}`);
  }
  fs.writeFileSync(path.join(ctx.runDir, 'CHECKSUMS.csv'), `${rows.join('\n')}\n`, 'utf8');
}

function markdownFindings(title, findings) {
  if (!findings.length) return `# ${title}\n\nNone.\n`;
  return `# ${title}\n\n${findings.map((finding) => `## ${finding.severity} ${finding.title}\n\n- Layer: ${finding.layer}\n- Detail: ${finding.detail}\n- File: ${finding.file || 'n/a'}\n- Recommendation: ${finding.recommendation || 'Review evidence.'}\n`).join('\n')}`;
}

function markdownReport(report) {
  const lines = [
    '# PRISMA Quality Report',
    '',
    `- Run: \`${report.runId}\``,
    `- Profile: \`${report.profile}\``,
    `- Decision: \`${report.decision.decision}\``,
    `- Blockers: \`${report.decision.blockerCount}\``,
    `- Warnings: \`${report.decision.warningCount}\``,
    `- Automation improvements: \`${report.automation.implemented}/${report.automation.total}\` implemented`,
    '',
    '## Gates'
  ];
  for (const gate of report.gates) lines.push(`- **${gate.gateId}** ${gate.status}: ${gate.summary}`);
  lines.push('', '## Findings');
  if (!report.findings.length) lines.push('No findings.');
  for (const finding of report.findings) lines.push(`- **${finding.severity} ${finding.layer}** ${finding.title}: ${finding.detail}`);
  return `${lines.join('\n')}\n`;
}

function phaseExit(report) {
  const phaseName = report.profile === 'phase5' || report.profile === 'release'
    ? 'Phase 5 Release & Operator Readiness'
    : `Profile ${report.profile}`;
  return `# Phase Exit Report\n\nPhase: ${phaseName}\n\nDecision: \`${report.decision.decision}\`\n\nBlockers: \`${report.decision.blockerCount}\`\nWarnings: \`${report.decision.warningCount}\`\n\nThis phase exit is valid only when JSON outputs parse cleanly, every READY gate has evidence, and blocked gates produce findings.\n`;
}

function nextActions(report) {
  const blocked = report.gates.filter((gate) => ['BLOCKED', 'ERROR'].includes(gate.status));
  const lines = ['# PRISMA Quality Next Actions', ''];
  if (!blocked.length) {
    lines.push('No blocking gates. Keep the generated evidence bundle with the release handoff.');
  } else {
    lines.push('Resolve gates in this order:');
    blocked.slice(0, 10).forEach((gate, index) => {
      const firstFinding = (gate.findings || [])[0];
      lines.push(`${index + 1}. **${gate.gateId}** - ${firstFinding?.title || gate.summary}`);
    });
  }
  lines.push('', 'Do not claim green unless QUALITY_DECISION.json is parseable and blockerCount is zero.');
  return `${lines.join('\n')}\n`;
}
