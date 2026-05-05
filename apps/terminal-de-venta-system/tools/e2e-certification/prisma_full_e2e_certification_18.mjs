#!/usr/bin/env node
/*
PRISMA FULL E2E CERTIFICATION 18
Read-only certification runner for Tablet + PC + Mobile flows.
It writes reports under F:\descargasf by default and does not mutate app code.
*/
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const CERT_ID = 'PRISMA_FULL_E2E_CERTIFICATION_18_20260504_v01';

function argValue(name, fallback) {
  const idx = process.argv.indexOf(name);
  if (idx >= 0 && idx + 1 < process.argv.length) return process.argv[idx + 1];
  return fallback;
}
function hasFlag(name) { return process.argv.includes(name); }
function nowStamp() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  return `${String(d.getFullYear()).slice(2)}${pad(d.getMonth()+1)}${pad(d.getDate())}_${pad(d.getHours())}${pad(d.getMinutes())}`;
}
function ensureDir(p) { mkdirSync(p, { recursive: true }); }
function readJsonIfExists(path) {
  try { if (existsSync(path)) return JSON.parse(readFileSync(path, 'utf8')); } catch (_) {}
  return null;
}
function runCommand(name, cwd, command, args, timeoutMs = 120000) {
  const startedAt = new Date().toISOString();
  const result = spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    timeout: timeoutMs,
    shell: process.platform === "win32",
    windowsHide: true
  });
  const stdout = result.stdout || '';
  const stderr = result.stderr || '';
  const output = `${stdout}\n${stderr}`.trim();
  return {
    name, cwd, command, args, startedAt,
    durationMs: null,
    status: result.status,
    signal: result.signal,
    error: result.error ? String(result.error.message || result.error) : null,
    pass: result.status === 0,
    stdoutTail: stdout.split(/\r?\n/).slice(-25).join('\n'),
    stderrTail: stderr.split(/\r?\n/).slice(-25).join('\n'),
    outputTail: output.split(/\r?\n/).slice(-35).join('\n')
  };
}
async function httpCheck(name, url, timeoutMs = 12000) {
  const startedAt = new Date().toISOString();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { signal: controller.signal });
    const text = await res.text();
    return {
      name, url, startedAt,
      pass: res.ok,
      status: res.status,
      statusText: res.statusText,
      bodyStart: text.slice(0, 220).replace(/\s+/g, ' '),
      error: null
    };
  } catch (err) {
    return { name, url, startedAt, pass: false, status: null, statusText: null, bodyStart: '', error: String(err?.message || err) };
  } finally {
    clearTimeout(timer);
  }
}
function commandExists(cmd) {
  const probe = process.platform === 'win32'
    ? spawnSync('where', [cmd], { encoding: 'utf8', shell: false })
    : spawnSync('which', [cmd], { encoding: 'utf8', shell: false });
  return probe.status === 0;
}
function packageHasScript(appRoot, scriptName) {
  const pkg = readJsonIfExists(join(appRoot, 'package.json'));
  return Boolean(pkg?.scripts?.[scriptName]);
}
function statusFrom(results) {
  const blockers = [];
  const caveats = [];
  for (const r of results.requiredPaths) if (!r.exists) blockers.push(`missing path: ${r.path}`);
  for (const c of results.commands) if (c.required && !c.pass) blockers.push(`command failed: ${c.name}`);
  for (const h of results.http) if (h.required && !h.pass) caveats.push(`http failed: ${h.name} ${h.url}`);
  for (const m of results.manualChecks) if (m.required && !m.observed) caveats.push(`manual evidence pending: ${m.id}`);
  if (blockers.length) return { status: 'BLOCKED', blockers, caveats };
  if (caveats.length) return { status: 'READY_WITH_CAVEATS', blockers, caveats };
  return { status: 'READY', blockers, caveats };
}
function mdEscape(s) { return String(s ?? '').replace(/\|/g, '\\|'); }
function renderMarkdown(report) {
  const lines = [];
  lines.push(`# ${CERT_ID}`);
  lines.push('');
  lines.push(`**Status:** ${report.decision.status}`);
  lines.push(`**Generated:** ${report.generatedAt}`);
  lines.push(`**Root:** \`${report.root}\``);
  lines.push('');
  lines.push('## Decision');
  lines.push('');
  if (report.decision.blockers.length) {
    lines.push('### Blockers');
    for (const b of report.decision.blockers) lines.push(`- ${b}`);
    lines.push('');
  }
  if (report.decision.caveats.length) {
    lines.push('### Caveats');
    for (const c of report.decision.caveats) lines.push(`- ${c}`);
    lines.push('');
  }
  lines.push('## Required paths');
  lines.push('');
  lines.push('| Path | Result |');
  lines.push('|---|---|');
  for (const p of report.requiredPaths) lines.push(`| \`${mdEscape(p.path)}\` | ${p.exists ? 'OK' : 'MISSING'} |`);
  lines.push('');
  lines.push('## Commands');
  lines.push('');
  lines.push('| Name | Required | Exit | Result |');
  lines.push('|---|---:|---:|---|');
  for (const c of report.commands) lines.push(`| ${mdEscape(c.name)} | ${c.required ? 'yes' : 'no'} | ${c.status ?? 'n/a'} | ${c.pass ? 'OK' : 'FAIL'} |`);
  lines.push('');
  lines.push('## HTTP smoke');
  lines.push('');
  lines.push('| Surface | URL | Required | Result |');
  lines.push('|---|---|---:|---|');
  for (const h of report.http) lines.push(`| ${mdEscape(h.name)} | \`${mdEscape(h.url)}\` | ${h.required ? 'yes' : 'no'} | ${h.pass ? 'OK' : 'FAIL'} ${h.status ? '(' + h.status + ')' : ''} |`);
  lines.push('');
  lines.push('## Manual E2E checklist');
  lines.push('');
  for (const m of report.manualChecks) lines.push(`- [ ] **${m.id}** (${m.surface}) ${m.description}`);
  lines.push('');
  lines.push('## Flow verdict');
  lines.push('');
  lines.push('- Tablet is certified only when checkout creates sale, sale lines, stock movement, outbox event, daily report, and export evidence.');
  lines.push('- PC is certified only when catalog, stock, counts, procurement, KPI dashboard, sync ingest, and conflicts are shown with real or explicitly fixture-tagged data.');
  lines.push('- Mobile is certified only when ready, partial, offline, install, command center, action inbox, daily brief, timeline, and health radar are verified against live or documented fixture states.');
  lines.push('');
  lines.push('## Raw command tails');
  for (const c of report.commands) {
    if (!c.pass) {
      lines.push('');
      lines.push(`### ${c.name}`);
      lines.push('```text');
      lines.push(c.outputTail || c.error || 'no output');
      lines.push('```');
    }
  }
  return lines.join('\n');
}

const repoRoot = resolve(argValue('--repo-root', process.cwd()));
const systemRoot = resolve(argValue('--system-root', join(repoRoot, 'apps', 'terminal-de-venta-system')));
const outRoot = resolve(argValue('--out', 'F:\\descargasf'));
const skipCommands = hasFlag('--http-only');
const skipHttp = hasFlag('--no-http');
const full = hasFlag('--full');
const stamp = nowStamp();
const reportDir = join(outRoot, `prisma_full_e2e_certification_18_${stamp}`);
ensureDir(reportDir);

const tabletRoot = join(systemRoot, 'products', 'tablet', 'app');
const pcRoot = join(systemRoot, 'products', 'pc', 'app');
const mobileRoot = join(systemRoot, 'products', 'mobile', 'app');

const requiredPaths = [
  systemRoot,
  tabletRoot,
  pcRoot,
  mobileRoot,
  join(tabletRoot, 'package.json'),
  join(pcRoot, 'package.json'),
  join(mobileRoot, 'package.json'),
  join(tabletRoot, 'data', 'tablet-pos.db'),
  join(pcRoot, 'package.json'),
  join(mobileRoot, 'public', 'manifest.webmanifest'),
  join(mobileRoot, 'public', 'prisma-mobile-sw.js')
].map((path) => ({ path, exists: existsSync(path) }));

const commands = [];
if (!skipCommands) {
  const pnpmCmd = process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm';
  if (!commandExists(process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm')) {
    commands.push({ name: 'pnpm available', required: true, pass: false, status: null, outputTail: 'pnpm not found in PATH' });
  } else {
    commands.push({ ...runCommand('tablet typecheck', tabletRoot, pnpmCmd, ['run', 'typecheck'], 120000), required: true });
    commands.push({ ...runCommand('pc typecheck', pcRoot, pnpmCmd, ['run', 'typecheck'], 120000), required: true });
    commands.push({ ...runCommand('mobile typecheck', mobileRoot, pnpmCmd, ['run', 'typecheck'], 120000), required: true });

    const optionalScripts = [
      [tabletRoot, 'tablet verify:pos-checkout-02', 'verify:pos-checkout-02'],
      [tabletRoot, 'tablet verify:catalog-products-03', 'verify:catalog-products-03'],
      [pcRoot, 'pc verify:pc:mass-catalog', 'verify:pc:mass-catalog'],
      [mobileRoot, 'mobile verify:pwa', 'verify:pwa'],
      [mobileRoot, 'mobile verify:command-center', 'verify:command-center'],
      [mobileRoot, 'mobile verify:action-inbox', 'verify:action-inbox'],
      [mobileRoot, 'mobile verify:daily-brief', 'verify:daily-brief'],
      [mobileRoot, 'mobile verify:decision-ledger', 'verify:decision-ledger'],
      [mobileRoot, 'mobile verify:pulse-timeline', 'verify:pulse-timeline'],
      [mobileRoot, 'mobile verify:health-radar', 'verify:health-radar'],
      [mobileRoot, 'mobile verify:data-readiness', 'verify:data-readiness']
    ];
    for (const [cwd, name, script] of optionalScripts) {
      if (packageHasScript(cwd, script)) {
        commands.push({ ...runCommand(name, cwd, pnpmCmd, ['run', script], 120000), required: full });
      } else {
        commands.push({ name, cwd, command: pnpmCmd, args: ['run', script], pass: false, required: false, status: null, outputTail: `script missing: ${script}` });
      }
    }
    if (full && packageHasScript(tabletRoot, 'check:all')) commands.push({ ...runCommand('tablet check:all', tabletRoot, pnpmCmd, ['run', 'check:all'], 180000), required: true });
    if (full && packageHasScript(pcRoot, 'check:all')) commands.push({ ...runCommand('pc check:all', pcRoot, pnpmCmd, ['run', 'check:all'], 180000), required: true });
    if (full && packageHasScript(mobileRoot, 'check:all')) commands.push({ ...runCommand('mobile check:all', mobileRoot, pnpmCmd, ['run', 'check:all'], 240000), required: true });
  }
}

const http = [];
if (!skipHttp) {
  const specs = [
    ['tablet reference', 'http://127.0.0.1:3120/prisma-dark-pos-reference', true],
    ['tablet checkout', 'http://127.0.0.1:3120/checkout', false],
    ['tablet catalog', 'http://127.0.0.1:3120/catalog', false],
    ['pc home', 'http://127.0.0.1:3130/', true],
    ['pc catalog', 'http://127.0.0.1:3130/catalog', false],
    ['pc stock', 'http://127.0.0.1:3130/stock', false],
    ['pc dashboard', 'http://127.0.0.1:3130/dashboard', false],
    ['pc sync', 'http://127.0.0.1:3130/sync', false],
    ['mobile home', 'http://127.0.0.1:3140/', true],
    ['mobile app', 'http://127.0.0.1:3140/prisma-app', false],
    ['mobile install', 'http://127.0.0.1:3140/prisma-app/install', false],
    ['mobile offline', 'http://127.0.0.1:3140/prisma-app/offline', false]
  ];
  for (const [name, url, required] of specs) http.push({ ...(await httpCheck(name, url)), required });
}

const manualChecks = [
  { id: 'TABLET_SALE_E2E', surface: 'tablet', required: true, observed: false, description: 'Buscar producto, agregar carrito, cobrar, ver ticket cerrado, stock descontado, outbox creado, reporte del día actualizado y export con venta.' },
  { id: 'PC_BACKOFFICE_E2E', surface: 'pc', required: true, observed: false, description: 'Navegar catálogo, stock, conteos, compras, recepción, reabasto, auditoría, dashboard KPI y sync/conflictos con datos reales o fixtures declarados.' },
  { id: 'MOBILE_OWNER_E2E', surface: 'mobile', required: true, observed: false, description: 'Abrir Pulso, revisar Command Center, inbox, brief, ledger, timeline, radar, readiness y estados ready/partial/offline.' },
  { id: 'SYNC_CHAIN_E2E', surface: 'system', required: true, observed: false, description: 'Demostrar que una venta Tablet puede ser vista o representada por PC y Mobile, o queda como caveat explícito si sync sigue por fixtures.' }
];

const report = {
  certId: CERT_ID,
  generatedAt: new Date().toISOString(),
  root: repoRoot,
  systemRoot,
  reportDir,
  mode: { full, skipCommands, skipHttp },
  requiredPaths,
  commands,
  http,
  manualChecks
};
report.decision = statusFrom(report);

const jsonPath = join(reportDir, 'prisma_full_e2e_certification_18_report.json');
const mdPath = join(reportDir, 'prisma_full_e2e_certification_18_report.md');
writeFileSync(jsonPath, JSON.stringify(report, null, 2), 'utf8');
writeFileSync(mdPath, renderMarkdown(report), 'utf8');

console.log(`[${CERT_ID}] status=${report.decision.status}`);
console.log(`json=${jsonPath}`);
console.log(`markdown=${mdPath}`);
if (report.decision.blockers.length) {
  for (const b of report.decision.blockers) console.error(`BLOCKER ${b}`);
  process.exitCode = 2;
} else if (report.decision.caveats.length) {
  for (const c of report.decision.caveats) console.warn(`CAVEAT ${c}`);
  process.exitCode = 1;
} else {
  process.exitCode = 0;
}


