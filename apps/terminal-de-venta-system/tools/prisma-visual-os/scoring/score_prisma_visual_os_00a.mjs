#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function arg(name, fallback) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 ? process.argv[idx + 1] : fallback;
}

const root = path.resolve(arg('--root', process.cwd()));
const outDir = path.resolve(arg('--out', process.env.PRISMA_VOS_OUT || 'F:/descargasf'));
const visualRoot = path.join(root, 'products/shared-ui/prisma/visual-os');

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(visualRoot, file), 'utf8'));
}

const controls = readJson('prisma-visual-os.controls.json');
const presets = readJson('prisma-visual-os.presets.json');
const recipes = readJson('prisma-visual-os.recipes.json');
const scorecard = readJson('prisma-visual-os.scorecard.json');

const surfaceFiles = {
  tabletPosCss: 'products/tablet/app/components/pos/pos.module.css',
  tabletShellCss: 'products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css',
  pcPackage: 'products/pc/app/package.json',
  mobilePackage: 'products/mobile/app/package.json',
  sharedPrismaTheme: 'products/shared-ui/prisma/tokens/prisma-theme.css'
};

const existing = Object.fromEntries(
  Object.entries(surfaceFiles).map(([key, rel]) => [key, fs.existsSync(path.join(root, rel))])
);

const controlCount = controls.controls.length;
const presetCount = Object.keys(presets.presets || {}).length;
const recipeCount = recipes.recipes?.length || 0;
const requiredFilesPresent = Object.values(existing).filter(Boolean).length;
const staticScore = Math.round(
  (controlCount === 12 ? 22 : 8) +
  (presetCount >= 6 ? 18 : 8) +
  (recipeCount >= 8 ? 18 : 8) +
  (scorecard.axes?.length >= 6 ? 16 : 6) +
  (requiredFilesPresent * 5.2)
);

const result = {
  generatedAt: new Date().toISOString(),
  root,
  package: 'PRISMA_VISUAL_OS_CONTROL_PLANE_00A_20260503_v01',
  score: Math.min(staticScore, 100),
  pass: staticScore >= 82,
  controls: controlCount,
  presets: presetCount,
  recipes: recipeCount,
  scoreAxes: scorecard.axes?.length || 0,
  existingSurfaceFiles: existing,
  nextRecommendedPackage: 'PRISMA_VISUAL_OS_POS_TOUCH_BINDING_00B',
  notes: [
    '00A is a static governance gate, not a screenshot-based visual QA run.',
    '00B should bind POS selectors to the Visual OS tokens and capture Tablet /pos evidence.',
    'Keep master controls constrained; do not add free-form cosmetic toggles.'
  ]
};

fs.mkdirSync(outDir, { recursive: true });
const stamp = new Date().toISOString().replace(/[-:T]/g, '').slice(2, 12);
const jsonPath = path.join(outDir, `prisma_visual_os_score_00a_${stamp}.json`);
const mdPath = path.join(outDir, `prisma_visual_os_score_00a_${stamp}.md`);
fs.writeFileSync(jsonPath, JSON.stringify(result, null, 2) + '\n', 'utf8');
fs.writeFileSync(mdPath, [
  '# PRISMA Visual OS Score 00A',
  '',
  `- Score: **${result.score}**`,
  `- Pass: **${result.pass ? 'SI' : 'NO'}**`,
  `- Controls: ${controlCount}`,
  `- Presets: ${presetCount}`,
  `- Recipes: ${recipeCount}`,
  '',
  '## Surface files detected',
  ...Object.entries(existing).map(([key, ok]) => `- ${key}: ${ok ? 'OK' : 'MISSING'}`),
  '',
  '## Next',
  `- ${result.nextRecommendedPackage}`,
  ''
].join('\n'), 'utf8');

console.log(`[VOS SCORE] ${result.score} pass=${result.pass}`);
console.log(`[VOS SCORE] wrote ${jsonPath}`);
console.log(`[VOS SCORE] wrote ${mdPath}`);
