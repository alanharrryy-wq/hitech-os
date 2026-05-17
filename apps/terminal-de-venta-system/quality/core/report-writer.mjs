        import fs from 'node:fs';
        import path from 'node:path';
        import { sha256File } from './checksums.mjs';
        export function writeReports(ctx, gateResults, decision, envSnapshot) {
          const findings = gateResults.flatMap(g => g.findings || []);
          const report = { schemaVersion: '1.0', runId: ctx.runId, profile: ctx.profile, repoRoot: ctx.repoRoot, generatedAt: new Date().toISOString(), decision, gates: gateResults, findings };
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_REPORT.json'), JSON.stringify(report, null, 2) + '\\n', 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_DECISION.json'), JSON.stringify(decision, null, 2) + '\\n', 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_FINDINGS.json'), JSON.stringify(findings, null, 2) + '\\n', 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'ENVIRONMENT_SNAPSHOT.json'), JSON.stringify(envSnapshot, null, 2) + '\\n', 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'COMMANDS_RUN.json'), JSON.stringify(ctx.commandsRun || [], null, 2) + '\\n', 'utf8');
          const blockers = findings.filter(f => ['S0', 'S1'].includes(f.severity) || (ctx.profile === 'release' && f.severity === 'S2'));
          const warnings = findings.filter(f => ['S2', 'S3'].includes(f.severity) && !blockers.includes(f));
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_BLOCKERS.md'), markdownFindings('Blockers', blockers), 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_WARNINGS.md'), markdownFindings('Warnings', warnings), 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_REPORT.md'), markdownReport(report), 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'PHASE_EXIT_REPORT.md'), phaseExit(report), 'utf8');
          const files = ['QUALITY_REPORT.json','QUALITY_DECISION.json','QUALITY_FINDINGS.json','QUALITY_EVIDENCE_LEDGER.jsonl','QUALITY_REPORT.md','QUALITY_BLOCKERS.md','QUALITY_WARNINGS.md','PHASE_EXIT_REPORT.md','ENVIRONMENT_SNAPSHOT.json','COMMANDS_RUN.json'];
          const rows = ['file,sha256'];
          for (const f of files) { const p = path.join(ctx.runDir, f); if (fs.existsSync(p)) rows.push(`${f},${sha256File(p)}`); }
          fs.writeFileSync(path.join(ctx.runDir, 'CHECKSUMS.csv'), rows.join('\\n') + '\\n', 'utf8');
          fs.writeFileSync(path.join(ctx.runDir, 'QUALITY_RUN_SUMMARY.txt'), `${decision.decision}
Run: ${ctx.runDir}
Blockers: ${decision.blockerCount}
Warnings: ${decision.warningCount}
`, 'utf8');
        }
        function markdownFindings(title, findings) { if (!findings.length) return `# ${title}

None.
`; return `# ${title}

` + findings.map(f => `## ${f.severity} ${f.title}

- Layer: ${f.layer}
- Detail: ${f.detail}
- File: ${f.file || 'n/a'}
- Recommendation: ${f.recommendation || 'Review evidence.'}
`).join('\\n'); }
        function markdownReport(report) { const lines = [`# PRISMA Quality Report`, ``, `- Run: \`${report.runId}\``, `- Profile: \`${report.profile}\``, `- Decision: \`${report.decision.decision}\``, `- Blockers: \`${report.decision.blockerCount}\``, `- Warnings: \`${report.decision.warningCount}\``, ``, `## Gates`]; for (const g of report.gates) lines.push(`- **${g.gateId}** ${g.status}: ${g.summary}`); lines.push('', '## Findings'); if (!report.findings.length) lines.push('No findings.'); for (const f of report.findings) lines.push(`- **${f.severity} ${f.layer}** ${f.title}: ${f.detail}`); return lines.join('\\n') + '\\n'; }
        function phaseExit(report) { return `# Phase Exit Report

Phase: Phase 1 Foundation, Kernel, Contracts & Evidence

Decision: \`${report.decision.decision}\`

This phase exit is valid only for local-first static gates. Runtime, sandbox scenarios, trace graph, drift intelligence, Control Center UI and CI governor are reserved for later phases.
`; }
