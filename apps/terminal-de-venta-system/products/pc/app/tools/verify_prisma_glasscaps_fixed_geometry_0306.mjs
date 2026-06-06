import fs from 'node:fs';
import path from 'node:path';

const pcRoot = process.cwd();
const targets = [
  {
    name: 'app router',
    page: path.join(pcRoot, 'app/referencia-visual/liquid-glass-capsules/page.tsx'),
    css: path.join(pcRoot, 'app/referencia-visual/liquid-glass-capsules/liquid-glass-capsules.module.css'),
  },
  {
    name: 'legacy visual route',
    page: path.join(pcRoot, 'referencia-visual/liquid-glass-capsules/page.tsx'),
    css: path.join(pcRoot, 'referencia-visual/liquid-glass-capsules/liquid-glass-capsules.module.css'),
    optional: true,
  },
];

const requiredShapeClasses = [
  'geoCircleSky',
  'geoRectRose',
  'geoTriangleAmber',
  'geoSquareIndigo',
  'geoCapsuleMint',
];

const failures = [];
const notes = [];

function read(file, optional = false) {
  if (!fs.existsSync(file)) {
    if (optional) return '';
    failures.push(`missing file: ${file}`);
    return '';
  }
  return fs.readFileSync(file, 'utf8');
}

function assertIncludes(haystack, needle, label) {
  if (!haystack.includes(needle)) failures.push(`${label}: missing ${needle}`);
}

function assertRegex(haystack, regex, label) {
  if (!regex.test(haystack)) failures.push(`${label}: failed ${regex}`);
}

for (const target of targets) {
  const page = read(target.page, target.optional);
  const css = read(target.css, target.optional);
  if (target.optional && (!page || !css)) {
    notes.push(`${target.name}: optional route not present, skipped`);
    continue;
  }

  assertIncludes(page, 'motionBackplate', `${target.name} page`);
  assertIncludes(page, 'PrismaGlassCapsule', `${target.name} page`);
  assertIncludes(page, 'PrismaGlassTopDock', `${target.name} page`);
  for (const cls of requiredShapeClasses) assertIncludes(page, cls, `${target.name} page`);

  assertRegex(css, /\.motionBackplate\s*\{[\s\S]*?position:\s*fixed;/, `${target.name} CSS fixed backplate`);
  assertRegex(css, /\.motionBackplate\s*\{[\s\S]*?background:\s*#efe7db;/, `${target.name} CSS background color`);
  assertRegex(css, /\.motionBackplate\s*\{[\s\S]*?pointer-events:\s*none;/, `${target.name} CSS pointer events`);
  assertIncludes(css, 'clip-path: polygon', `${target.name} CSS triangle`);

  const solidColors = ['#1e8cff', '#ff4f9a', '#ffb000', '#5138ff', '#24d8a7'];
  for (const color of solidColors) assertIncludes(css, color, `${target.name} solid color ${color}`);

  const backplateChunk = css.match(/\.motionBackplate\s*\{[\s\S]*?\}/)?.[0] ?? '';
  if (backplateChunk.includes('radial-gradient') || backplateChunk.includes('linear-gradient')) {
    failures.push(`${target.name}: motionBackplate must use flat background, no gradient`);
  }

  const geometryChunk = css.match(/\.geoCircleSky[\s\S]*?\.topDockWrap|\.geoCircleSky[\s\S]*?\.hero/)?.[0] ?? css;
  if (geometryChunk.includes('animation:')) failures.push(`${target.name}: geometry must stay static, found animation`);
}

if (failures.length) {
  console.error('PRISMA fixed geometry verifier FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('PRISMA fixed geometry verifier PASS');
for (const note of notes) console.log(`NOTE ${note}`);
console.log('Fixed solid geometry background is present; pills can scroll over static shapes.');
