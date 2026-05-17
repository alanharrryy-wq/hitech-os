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
import { normalizeGateResult, assertNoFakeGreen } from './gate-normalizer.mjs';
import { runSelfTest } from './self-test.mjs';

function parseArgs(argv) {
  const args = { profile: 'commit', outDir: null, repoRoot: null, diagnoseLatest: false, selfTest: false, listProfiles: false, help: false, version: false };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--profile') args.profile = argv[++index];
    else if (arg === '--out-dir') args.outDir = argv[++index];
    else if (arg === '--repo-root') args.repoRoot = argv[++index];
    else if (arg === '--diagnose-latest') args.diagnoseLatest = true;
    else if (arg === '--self-test') args.selfTest = true;
    else if (arg === '--list-profiles') args.listProfiles = true;
    else if (arg === '--version') args.version = true;
    else if (arg === '--help' || arg === '-h') args.help = true;
  }
  return args;
}

function runId() {
  const date = new Date();
  const pad = (value, width = 2) => String(value).padStart(width, '0');
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(date.getDate())}_${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}_${pad(date.getMilliseconds(), 3)}`;
}

function latestRun(outDir) {
  if (!fs.existsSync(outDir)) return null;
  const runs = fs.readdirSync(outDir).filter((name) => name.startsWith('PRISMA_QUALITY_OS_')).sort().reverse();
  return runs.length ? path.join(outDir, runs[0]) : null;
}

function helpText() {
  return `PRISMA Quality Operating System\n\nUsage:\n  node quality/bin/prisma-quality.mjs --profile phase5 --repo-root . --out-dir F:\\descargasf\n\nOptions:\n  --profile <name>       Profile to run. Default: commit\n  --repo-root <path>     Repository root that contains quality/\n  --out-dir <path>       Output directory for PRISMA_QUALITY_OS_* runs\n  --self-test            Validate the bundle itself\n  --diagnose-latest      Print the latest run summary\n  --list-profiles        List available profiles\n  --version              Print PQOS version\n  --help                 Show this help\n`;
}

function listProfiles(qualityRoot) {
  const profilesDir = path.join(qualityRoot, 'profiles');
  if (!fs.existsSync(profilesDir)) return [];
  return fs.readdirSync(profilesDir).filter((name) => name.endsWith('.json')).sort().map((name) => path.basename(name, '.json'));
}

function addSelfAuditFindings(result) {
  const fakeGreenIssue = assertNoFakeGreen(result);
  if (!fakeGreenIssue) return result;
  const findings = result.findings || [];
  findings.push(finding({
    id: `${result.gateId}_SELF_AUDIT_CONTRACT_VIOLATION`,
    severity: 'S1',
    layer: 'Quality',
    title: 'Gate result violates no-fake-green contract',
    detail: fakeGreenIssue,
    recommendation: 'Normalize the gate result so blocked gates have findings and ready gates have evidence.'
  }));
  return { ...result, status: 'BLOCKED', findings };
}

export async function runCli(argv) {
  const args = parseArgs(argv);
  const repoRoot = path.resolve(args.repoRoot || process.cwd());
  const qualityRoot = path.join(repoRoot, 'quality');
  if (args.help) {
    console.log(helpText());
    return 0;
  }
  const config = readJson(path.join(qualityRoot, 'quality.config.json'));
  const manifest = readJson(path.join(qualityRoot, 'prisma-quality.manifest.json'));
  const outDir = path.resolve(args.outDir || config.defaultOutDir || manifest.defaultOutDir || 'F:/descargasf');
  if (args.version) {
    console.log(manifest.systemVersion || 'unknown');
    return 0;
  }
  if (args.listProfiles) {
    console.log(listProfiles(qualityRoot).join('\n'));
    return 0;
  }
  if (args.selfTest) {
    const self = await runSelfTest({ repoRoot, qualityRoot });
    for (const item of self.checks) console.log(`${item.ok ? 'PASS' : 'FAIL'} ${item.label}`);
    console.log(`PQOS self-test ${self.ok ? 'OK' : 'FAILED'}: ${self.checks.filter((item) => item.ok).length}/${self.checks.length} checks passed.`);
    return self.ok ? 0 : 1;
  }
  if (args.diagnoseLatest) {
    const latest = latestRun(outDir);
    if (!latest) {
      console.log('No previous PRISMA_QUALITY_OS_* run found.');
      return 1;
    }
    const decisionPath = path.join(latest, 'QUALITY_DECISION.json');
    const reportPath = path.join(latest, 'QUALITY_REPORT.md');
    console.log(`Latest run: ${latest}`);
    if (fs.existsSync(decisionPath)) console.log(fs.readFileSync(decisionPath, 'utf8'));
    if (fs.existsSync(reportPath)) console.log(fs.readFileSync(reportPath, 'utf8').slice(0, 8000));
    return 0;
  }

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
      if (!fs.existsSync(gateFile)) throw new Error(`Gate file not found: ${gateFile}`);
      const mod = await import(pathToFileURL(gateFile).href);
      const raw = await mod.run(ctx);
      let result = normalizeGateResult(raw, gateId);
      result.startedAt = result.startedAt || startedAt;
      result.endedAt = result.endedAt || new Date().toISOString();
      if (result.status === 'READY' && (!result.evidence || result.evidence.length === 0)) {
        result.status = 'BLOCKED';
        result.findings = result.findings || [];
        result.findings.push(finding({ id: `${result.gateId}_NO_EVIDENCE`, severity: 'S1', layer: 'Quality', title: 'PASS without evidence is forbidden', detail: `${result.gateId} attempted READY without evidence.`, recommendation: 'Make the gate write evidence before returning READY.' }));
      }
      result = addSelfAuditFindings(result);
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
