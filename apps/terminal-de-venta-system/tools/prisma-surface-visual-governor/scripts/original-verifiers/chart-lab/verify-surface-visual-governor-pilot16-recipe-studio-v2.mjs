#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
let repoRoot = process.cwd();
let out = null;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--repo') repoRoot = args[++i];
  else if (args[i] === '--out') out = args[++i];
}

function exists(rel) { return fs.existsSync(path.join(repoRoot, rel)); }
function read(rel) { return fs.readFileSync(path.join(repoRoot, rel), 'utf8'); }
function lower(rel) { return read(rel).toLowerCase(); }

const checks = [];
const failures = [];
const warnings = [];
function check(name, ok, detail = {}) {
  checks.push({ name, status: ok ? 'PASS' : 'FAIL', ...detail });
  if (!ok) failures.push({ name, ...detail });
}

const page = 'products/chart-lab/app/app/recipe-studio-v2/page.tsx';
const css = 'products/chart-lab/app/app/recipe-studio-v2/prisma-recipe-studio-v2.module.css';
const latest = 'products/chart-lab/app/public/surface-visual-governor/recipe-studio-v2/latest/index.json';
const pilot = 'products/chart-lab/app/public/surface-visual-governor/recipe-studio-v2/pilot-16/index.json';
const enforcer = 'tools/prisma-surface-governor/route-budget-enforcer/prisma.route-budget.policy.json';

check('route page exists', exists(page), { file: page });
check('css module exists', exists(css), { file: css });
check('latest public manifest exists', exists(latest), { file: latest });
check('pilot public manifest exists', exists(pilot), { file: pilot });
check('route budget enforcer policy exists', exists(enforcer), { file: enforcer });

if (exists(page)) {
  const t = lower(page);
  for (const marker of ['recipe studio v2', 'route budget enforcer', 'validate', 'copy', 'recipe-export/latest']) {
    check(`page marker ${marker}`, t.includes(marker), { marker });
  }
  for (const denied of ['tablet-pos', '.sqlite', '.sqlite3']) {
    check(`page public denied token absent ${denied}`, !t.includes(denied), { denied });
  }
}

if (exists(css)) {
  const t = lower(css);
  check('css has chart lab governor marker', t.includes('recipe-studio'), { file: css });
  for (const denied of ['storm-cloud-operations-real.jpg', 'obsidian-cloud-motion.svg', 'webgl', '@react-three', 'pixi', 'backdrop-filter', 'blur(']) {
    check(`css denied active term absent ${denied}`, !t.includes(denied), { denied });
  }
}

for (const rel of [latest, pilot]) {
  if (exists(rel)) {
    const t = lower(rel);
    for (const denied of ['<LOCAL_PATH>', '<LOCAL_PATH>', '.sqlite', '.sqlite3', 'tablet-pos', 'databasepaths']) {
      check(`public manifest denied token absent ${denied}`, !t.includes(denied), { file: rel, denied });
    }
  }
}

const result = {
  status: failures.length ? 'FAIL' : 'PASS',
  generated_at: new Date().toISOString(),
  repo_root: repoRoot,
  checks,
  failures,
  warnings,
  route: '/recipe-studio-v2'
};

const json = JSON.stringify(result, null, 2);
if (out) {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, json, 'utf8');
}
console.log(json);
process.exit(result.status === 'PASS' ? 0 : 1);
