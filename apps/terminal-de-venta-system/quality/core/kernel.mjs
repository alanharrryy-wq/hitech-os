import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';
import { readJson } from './safe-json.mjs';
import { ensureDir } from './paths.mjs';
import { decide } from './decision-engine.mjs';
import { writeReports } from './report-writer.mjs';
import { environmentSnapshot } from './environment-snapshot.mjs';
import { printSummary } from './console-summary.mjs';
import { finding } from './result-types.mjs';
function parseArgs(argv) { const args = { profile: 'commit', outDir: null, repoRoot: null, diagnoseLatest: false, selfTest: false }; for (let i = 0; i < argv.length; i++) { const a = argv[i]; if (a === '--profile') args.profile = argv[++i]; else if (a === '--out-dir') args.outDir = argv[++i]; else if (a === '--repo-root') args.repoRoot = argv[++i]; else if (a === '--diagnose-latest') args.diagnoseLatest = true; else if (a === '--self-test') args.selfTest = true; } return args; }
function runId() { const d = new Date(); const pad = (n) => String(n).padStart(2, '0'); return `${d.getFullYear()}${pad(d.getMonth()+1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`; }
function latestRun(outDir) { if (!fs.existsSync(outDir)) return null; const runs = fs.readdirSync(outDir).filter(n => n.startsWith('PRISMA_QUALITY_OS_')).sort().reverse(); return runs.length ? path.join(outDir, runs[0]) : null; }
export async function runCli(argv) {
  const args = parseArgs(argv);
  const repoRoot = path.resolve(args.repoRoot || process.cwd());
  const qualityRoot = path.join(repoRoot, 'quality');
  const config = readJson(path.join(qualityRoot, 'quality.config.json'));
  const manifest = readJson(path.join(qualityRoot, 'prisma-quality.manifest.json'));
  const outDir = path.resolve(args.outDir || config.defaultOutDir || manifest.defaultOutDir || 'F:/descargasf');
  if (args.selfTest) { console.log('PQOS self-test OK: manifest, config and kernel loaded.'); return 0; }
  if (args.diagnoseLatest) { const latest = latestRun(outDir); if (!latest) { console.log('No previous PRISMA_QUALITY_OS_* run found.'); return 1; } const decisionPath = path.join(latest, 'QUALITY_DECISION.json'); const reportPath = path.join(latest, 'QUALITY_REPORT.md'); console.log(`Latest run: ${latest}`); if (fs.existsSync(decisionPath)) console.log(fs.readFileSync(decisionPath, 'utf8')); if (fs.existsSync(reportPath)) console.log(fs.readFileSync(reportPath, 'utf8').slice(0, 8000)); return 0; }
  const id = runId();
  const runDir = path.join(outDir, `PRISMA_QUALITY_OS_${id}`);
  ensureDir(runDir);
  fs.writeFileSync(path.join(runDir, 'QUALITY_EVIDENCE_LEDGER.jsonl'), '', 'utf8');
  const ctx = { runId: id, repoRoot, qualityRoot, outDir, runDir, profile: args.profile, config, manifest, evidenceCounter: 1, commandsRun: [], partialGateResults: [] };
  const profilePath = path.join(qualityRoot, 'profiles', `${args.profile}.json`);
  if (!fs.existsSync(profilePath)) throw new Error(`Profile not found: ${args.profile}`);
  const profile = readJson(profilePath);
  const gateResults = [];
  for (const gateId of profile.gates || []) {
    const gateFile = path.join(qualityRoot, 'gates', `${gateId}.mjs`);
    const startedAt = new Date().toISOString();
    try {
      const mod = await import(pathToFileURL(gateFile).href);
      const result = await mod.run(ctx);
      result.startedAt = result.startedAt || startedAt;
      result.endedAt = result.endedAt || new Date().toISOString();
      if (result.status === 'READY' && (!result.evidence || result.evidence.length === 0)) { result.status = 'BLOCKED'; result.findings = result.findings || []; result.findings.push(finding({ id: `${result.gateId}_NO_EVIDENCE`, severity: 'S1', layer: 'Quality', title: 'PASS without evidence is forbidden', detail: `${result.gateId} attempted READY without evidence.`, recommendation: 'Make the gate write evidence before returning READY.' })); }
      gateResults.push(result);
      ctx.partialGateResults.push(result);
    } catch (error) {
      gateResults.push({ gateId, title: gateId, status: 'ERROR', summary: String(error.message || error), findings: [finding({ id: `${gateId}_ERROR`, severity: 'S1', layer: 'Quality', title: 'Gate execution failed', detail: String(error.stack || error) })], evidence: [], startedAt, endedAt: new Date().toISOString() });
    }
  }
  const env = environmentSnapshot(repoRoot);
  const decision = decide(args.profile, gateResults);
  writeReports(ctx, gateResults, decision, env);
  printSummary(ctx, decision);
  return decision.exitCode;
}
