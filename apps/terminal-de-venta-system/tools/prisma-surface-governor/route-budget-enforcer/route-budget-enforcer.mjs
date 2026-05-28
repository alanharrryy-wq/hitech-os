#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function normalizeText(value) {
  return String(value ?? '').toLowerCase();
}

function textFromFile(file) {
  if (!fs.existsSync(file)) return null;
  return fs.readFileSync(file, 'utf8');
}

function hasTerm(textLower, term) {
  return textLower.includes(String(term).toLowerCase());
}

function evaluateText({ text, budgetClass, policy }) {
  const budget = policy.budget_classes[budgetClass];
  if (!budget) {
    return {
      status: 'FAIL',
      findings: [{ severity: 'fail', type: 'unknown_budget_class', budgetClass, message: `Unknown budget class: ${budgetClass}` }],
      warnings: []
    };
  }

  const textLower = normalizeText(text);
  const findings = [];
  const warnings = [];

  for (const marker of budget.required_all || []) {
    if (!hasTerm(textLower, marker)) {
      findings.push({
        severity: 'fail',
        type: 'missing_required_marker',
        budgetClass,
        marker,
        message: `Required route-budget marker missing for ${budgetClass}: ${marker}`
      });
    }
  }

  const requiredAny = budget.required_any || [];
  if (requiredAny.length && !requiredAny.some((marker) => hasTerm(textLower, marker))) {
    findings.push({
      severity: 'fail',
      type: 'missing_required_any_marker',
      budgetClass,
      markers: requiredAny,
      message: `At least one route-budget marker is required for ${budgetClass}: ${requiredAny.join(', ')}`
    });
  }

  for (const term of budget.denied || []) {
    if (hasTerm(textLower, term)) {
      findings.push({
        severity: 'fail',
        type: 'denied_term',
        budgetClass,
        term,
        message: `Denied visual/runtime term for ${budgetClass}: ${term}`
      });
    }
  }

  for (const term of budget.warn || []) {
    if (hasTerm(textLower, term)) {
      warnings.push({
        severity: 'warn',
        type: 'warn_term',
        budgetClass,
        term,
        message: `Allowed but notable term for ${budgetClass}: ${term}`
      });
    }
  }

  return { status: findings.length ? 'FAIL' : 'PASS', findings, warnings, budget };
}

function scanPublicGovernor({ repoRoot, policy }) {
  const roots = [
    'products/chart-lab/app/public/surface-visual-governor',
    'products/pc/app/public/surface-visual-governor',
    'products/tablet/app/public/surface-visual-governor',
    'products/mobile/app/public/surface-visual-governor',
    'products/web/app/public/surface-visual-governor'
  ];

  const findings = [];
  const denied = policy.global_public_denied || [];
  const exts = new Set(['.json', '.md', '.txt', '.css', '.js', '.mjs', '.ts', '.tsx']);

  function walk(dir) {
    if (!fs.existsSync(dir)) return;
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        walk(full);
      } else if (exts.has(path.extname(entry.name).toLowerCase())) {
        const rel = path.relative(repoRoot, full);
        const text = fs.readFileSync(full, 'utf8').toLowerCase();
        for (const term of denied) {
          if (text.includes(String(term).toLowerCase())) {
            findings.push({ severity: 'fail', type: 'public_denied_term', file: rel, term });
          }
        }
      }
    }
  }

  for (const root of roots) walk(path.join(repoRoot, root));
  return findings;
}

function evaluateRoutes({ repoRoot, policy }) {
  const routeResults = [];
  for (const route of policy.routes || []) {
    if (route.skip) {
      routeResults.push({ pilot: route.pilot, budget_class: route.budget_class, path: route.path, status: 'PASS', skipped: true, findings: [], warnings: [] });
      continue;
    }
    const abs = path.isAbsolute(route.path) ? route.path : path.join(repoRoot, route.path);
    if (!fs.existsSync(abs)) {
      routeResults.push({
        pilot: route.pilot,
        budget_class: route.budget_class,
        path: route.path,
        status: route.optional ? 'SKIP' : 'FAIL',
        missing: true,
        findings: route.optional ? [] : [{ severity: 'fail', type: 'missing_target', file: route.path }],
        warnings: route.optional ? [{ severity: 'warn', type: 'missing_target', file: route.path }] : []
      });
      continue;
    }
    const text = textFromFile(abs);
    const result = evaluateText({ text, budgetClass: route.budget_class, policy });
    routeResults.push({ pilot: route.pilot, budget_class: route.budget_class, path: route.path, ...result });
  }
  return routeResults;
}

export function runEnforcer({ repoRoot, policyPath } = {}) {
  const root = path.resolve(repoRoot || process.cwd());
  const pPath = policyPath || path.join(__dirname, 'prisma.route-budget.policy.json');
  const policy = readJson(pPath);

  const samples = {
    cleanPos: evaluateText({
      text: '/* route-budget: pos light safe productive shell */ .pos { background-image: url("/surface-visual-governor/pos-light-safe-shell/latest/atmosphere-assets/backgrounds/tablet-soft-gray-clouds.svg"); }',
      budgetClass: 'pos_light_safe',
      policy
    }),
    dirtyPos: evaluateText({
      text: '.pos { background-image: url("storm-cloud-operations-real.jpg"); backdrop-filter: blur(14px); }',
      budgetClass: 'pos_light_safe',
      policy
    }),
    cleanPublic: evaluateText({
      text: '/* route-budget: public sober light */ .public { background: #f8fafc; }',
      budgetClass: 'public_sober',
      policy
    }),
    posGateManifest: evaluateText({
      text: '{"route_budget":"pos governance gate protected final","denied_terms":["storm-cloud-operations-real.jpg","obsidian-cloud-motion.svg"],"status":"documented_not_active"}',
      budgetClass: 'pos_governance_gate',
      policy
    })
  };

  const route_results = evaluateRoutes({ repoRoot: root, policy });
  const public_findings = scanPublicGovernor({ repoRoot: root, policy });

  const failures = [];
  for (const [name, sample] of Object.entries(samples)) {
    if (name === 'dirtyPos') {
      if (sample.status !== 'FAIL') {
        failures.push({ severity: 'fail', type: 'sample_expected_fail_missing', sample: name });
      }
      continue;
    }
    if (sample.findings?.length) failures.push(...sample.findings.map((f) => ({ ...f, sample: name })));
  }

  for (const route of route_results) {
    if (route.status === 'FAIL') failures.push(...(route.findings || []).map((f) => ({ ...f, pilot: route.pilot, path: route.path })));
  }
  failures.push(...public_findings);

  const warnings_count = route_results.reduce((acc, r) => acc + (r.warnings?.length || 0), 0)
    + Object.values(samples).reduce((acc, r) => acc + (r.warnings?.length || 0), 0);

  return {
    status: failures.length ? 'FAIL' : 'PASS',
    generated_at: new Date().toISOString(),
    repo_root: root,
    enforcer_hotfix: '02_semantic_governance_context',
    samples,
    public_findings,
    route_results,
    failures,
    failures_count: failures.length,
    warnings_count
  };
}

if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}` || process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  let repoRoot = process.cwd();
  let out = null;
  let policyPath = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--repo') repoRoot = args[++i];
    else if (args[i] === '--out') out = args[++i];
    else if (args[i] === '--policy') policyPath = args[++i];
  }
  const result = runEnforcer({ repoRoot, policyPath });
  const json = JSON.stringify(result, null, 2);
  if (out) {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, json, 'utf8');
  }
  console.log(json);
  process.exit(result.status === 'PASS' ? 0 : 1);
}
