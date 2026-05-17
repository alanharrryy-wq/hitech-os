import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const qualityRoot = path.resolve(__dirname, '..');
const repoRoot = path.dirname(qualityRoot);
const outDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pqos-smoke-out-'));

function run(args, expectCode = 0) {
  const result = spawnSync(process.execPath, [path.join(qualityRoot, 'bin', 'prisma-quality.mjs'), ...args], {
    cwd: repoRoot,
    encoding: 'utf8'
  });
  if (result.status !== expectCode) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`Command failed (${result.status} != ${expectCode}): ${args.join(' ')}`);
  }
  return result;
}

function latestRun() {
  const runs = fs.readdirSync(outDir).filter((name) => name.startsWith('PRISMA_QUALITY_OS_')).sort().reverse();
  if (!runs.length) throw new Error('No run output found');
  return path.join(outDir, runs[0]);
}

run(['--self-test', '--repo-root', repoRoot]);
run(['--profile', 'automation', '--repo-root', repoRoot, '--out-dir', outDir], 0);
let dir = latestRun();
for (const name of ['QUALITY_DECISION.json', 'QUALITY_REPORT.json', 'QUALITY_OUTPUT_VALIDATION.json', 'QUALITY_AUTOMATION_SUMMARY.json']) {
  JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
}
const decision = JSON.parse(fs.readFileSync(path.join(dir, 'QUALITY_DECISION.json'), 'utf8'));
if (decision.decision !== 'READY_TO_COMMIT' && decision.decision !== 'READY_TO_AUTOMATION') {
  throw new Error(`Unexpected automation decision: ${decision.decision}`);
}
const automation = JSON.parse(fs.readFileSync(path.join(dir, 'QUALITY_AUTOMATION_SUMMARY.json'), 'utf8'));
if ((automation.implemented || 0) < 100) throw new Error('Automation catalog under 100 implemented improvements');

run(['--profile', 'phase5', '--repo-root', repoRoot, '--out-dir', outDir], 0);
dir = latestRun();
const phase5Decision = JSON.parse(fs.readFileSync(path.join(dir, 'QUALITY_DECISION.json'), 'utf8'));
if (phase5Decision.decision === 'BLOCKED') throw new Error(`Phase5 should not block the quality-only fixture: ${phase5Decision.blockerCount} blockers`);
if ((phase5Decision.blockerCount || 0) !== 0) throw new Error('Phase5 fixture produced blockers');
const reportText = fs.readFileSync(path.join(dir, 'QUALITY_REPORT.md'), 'utf8');
if (reportText.includes('\\n')) throw new Error('Markdown report contains literal backslash-n');
if (reportText.includes('**undefined**')) throw new Error('Markdown report still has undefined gate id');
const summaryText = fs.readFileSync(path.join(dir, 'QUALITY_RUN_SUMMARY.txt'), 'utf8');
if (!summaryText.includes('Blockers: 0')) throw new Error('Run summary did not record zero blockers');
console.log('PQOS bundle smoke OK');
