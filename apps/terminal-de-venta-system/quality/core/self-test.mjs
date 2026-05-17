import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { writeJson, readJson } from './safe-json.mjs';
import { normalizeGateResult, assertNoFakeGreen } from './gate-normalizer.mjs';
import { loadAutomationCatalog } from './automation-catalog.mjs';

function listFiles(root, predicate, out = []) {
  if (!fs.existsSync(root)) return out;
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) listFiles(full, predicate, out);
    else if (!predicate || predicate(full)) out.push(full);
  }
  return out;
}

function check(condition, label, details = {}) {
  return { ok: Boolean(condition), label, ...details };
}

export async function runSelfTest({ repoRoot, qualityRoot }) {
  const checks = [];
  checks.push(check(fs.existsSync(path.join(qualityRoot, 'prisma-quality.manifest.json')), 'manifest exists'));
  checks.push(check(fs.existsSync(path.join(qualityRoot, 'quality.config.json')), 'config exists'));
  const manifest = readJson(path.join(qualityRoot, 'prisma-quality.manifest.json'));
  checks.push(check(manifest.phase === 'phase-5-release-operator-readiness', 'manifest phase is phase 5', { phase: manifest.phase }));
  checks.push(check((manifest.gates || []).includes('Q30') && (manifest.gates || []).includes('Q31'), 'manifest includes Q30 and Q31'));
  let phase5Common = null;
  try {
    phase5Common = await import('../gates/_phase5_release_operator_readiness_common.mjs');
    checks.push(check((phase5Common.PHASE5_GATE_IDS || []).includes('Q31'), 'phase5 common includes Q31'));
    const q30 = await phase5Common.runPhase5Gate('Q30', { repoRoot });
    checks.push(check(q30.status !== 'BLOCKED', 'Q30 accepts direct quality CLI without root package scripts', { status: q30.status, blockers: q30.blockerCount }));
  } catch (error) {
    checks.push(check(false, 'phase5 calibration imports cleanly', { error: error?.message || String(error) }));
  }



  try {
    const advisoryRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'pqos-q26-advisory-'));
    const ccRoot = path.join(advisoryRoot, 'prisma-control-center');
    const wrappersDir = path.join(ccRoot, 'internal', 'wrappers');
    fs.mkdirSync(wrappersDir, { recursive: true });
    const launcherPairs = [
      ['01_LEVANTAR_TODO_LOCAL.cmd', 'local_up.ps1'],
      ['02_LEVANTAR_TODO_CLOUDFLARE.cmd', 'cloudflare_up.ps1'],
      ['03_LEVANTAR_TODO_LOCAL_Y_CLOUDFLARE.cmd', 'all_up.ps1'],
      ['04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd', 'health.ps1'],
      ['05_LEVANTAR_WEB_CONTROL_LOCAL.cmd', 'web_control_local.ps1'],
      ['06_LEVANTAR_WEB_CONTROL_LOCAL_Y_CLOUDFLARE.cmd', 'web_control_cloudflare.ps1'],
      ['07_ABRIR_PANEL_CONTROL_3150.cmd', 'panel_3150.ps1'],
      ['08_LEVANTAR_CHART_LAB_LOCAL.cmd', 'chart_lab_local.ps1'],
      ['09_KILL_EVERYTHING_PRISMA.cmd', 'kill_everything.ps1'],
    ];
    for (const [cmd, ps1] of launcherPairs) {
      fs.writeFileSync(path.join(ccRoot, cmd), `@echo off\nREM intentionally stale command for advisory calibration\nREM PRISMA_LAUNCHER_RUNS\n`, 'utf8');
      fs.writeFileSync(path.join(wrappersDir, ps1), `# ${ps1}\n# PRISMA_LAUNCHER_RUNS legacy marker\n# ports 3000 3100 3110 3120 3130 3140 3150 3200\n# F:/descargasf\n`, 'utf8');
    }
    const q26 = await phase5Common.runPhase5Gate('Q26', { repoRoot: advisoryRoot });
    checks.push(check(q26.status !== 'BLOCKED', 'Q26 downgrades wrapper drift to advisory warnings by default', { status: q26.status, blockers: q26.blockerCount, warnings: q26.warningCount }));
  } catch (error) {
    checks.push(check(false, 'Q26 advisory calibration fixture', { error: error?.message || String(error) }));
  }


  checks.push(check(fs.existsSync(path.join(qualityRoot, 'scripts', 'repair_phase5_warnings.py')), 'phase5 warning repair script exists'));
  const phase5DocText = fs.readFileSync(path.join(qualityRoot, 'docs', 'phase-5-release-operator-readiness.md'), 'utf8').toLowerCase();
  checks.push(check(phase5DocText.includes('rollback') && phase5DocText.includes('repair_phase5_warnings.py'), 'phase5 docs include warning repair rollback path'));

  const nowIdRegex = /^\d{8}_\d{6}_\d{3}$/;
  const kernelText = fs.readFileSync(path.join(qualityRoot, 'core', 'kernel.mjs'), 'utf8');
  checks.push(check(kernelText.includes('getMilliseconds'), 'runId includes milliseconds to avoid same-second overwrite'));

  const catalog = loadAutomationCatalog(qualityRoot);
  checks.push(check(catalog.ok, 'automation catalog has at least 100 unique improvements', { total: catalog.total, implemented: catalog.implemented, error: catalog.error }));

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pqos-self-test-'));
  const jsonPath = path.join(tmp, 'sample.json');
  writeJson(jsonPath, { ok: true });
  const jsonText = fs.readFileSync(jsonPath, 'utf8');
  checks.push(check(JSON.parse(jsonText).ok === true, 'writeJson creates parseable JSON'));
  checks.push(check(!jsonText.endsWith('\\n'), 'writeJson does not append literal backslash-n'));

  const normalized = normalizeGateResult({ id: 'QX', status: 'PASS', blockers: ['must block'], warnings: ['watch it'], evidence: ['proof'] }, 'QX');
  checks.push(check(normalized.gateId === 'QX', 'normalizer maps id to gateId'));
  checks.push(check(normalized.status === 'BLOCKED', 'normalizer converts blockers to BLOCKED'));
  checks.push(check(normalized.findings.length === 2, 'normalizer converts blockers/warnings to findings'));
  checks.push(check(assertNoFakeGreen(normalized) === null, 'normalized blocked gate passes anti-fake-green audit'));

  const gateFiles = listFiles(path.join(qualityRoot, 'gates'), (file) => file.endsWith('.mjs') && !path.basename(file).startsWith('_'));
  for (const gateFile of gateFiles) {
    try {
      const mod = await import(pathToFileURL(gateFile).href);
      checks.push(check(typeof mod.run === 'function' || typeof mod.default === 'function', `gate exports run/default: ${path.basename(gateFile)}`));
    } catch (error) {
      checks.push(check(false, `gate imports cleanly: ${path.basename(gateFile)}`, { error: error?.message || String(error) }));
    }
  }

  const profileFiles = listFiles(path.join(qualityRoot, 'profiles'), (file) => file.endsWith('.json'));
  const declaredGates = new Set(gateFiles.map((file) => path.basename(file, '.mjs')));
  for (const profileFile of profileFiles) {
    const profile = readJson(profileFile);
    const missing = (profile.gates || []).filter((gateId) => !declaredGates.has(gateId));
    checks.push(check(missing.length === 0, `profile gates exist: ${path.basename(profileFile)}`, { missing }));
  }

  const ok = checks.every((item) => item.ok);
  return { ok, repoRoot, qualityRoot, checks };
}
