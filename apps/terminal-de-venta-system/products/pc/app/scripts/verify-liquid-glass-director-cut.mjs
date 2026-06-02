import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const fail = [];
const pass = [];

function ok(name, condition, detail = '') {
  if (condition) pass.push({ name, detail });
  else fail.push({ name, detail });
}

function file(...parts) {
  return path.join(root, ...parts);
}

function read(p) {
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
}

function readJson(p) {
  try { return JSON.parse(read(p)); } catch { return {}; }
}

const pagePath = file('products','pc','app','app','referencia-visual','liquid-glass','page.tsx');
const oglPath = file('products','pc','app','app','referencia-visual','liquid-glass','liquid-glass-ogl-aura.tsx');
const cssPath = file('products','pc','app','app','prisma-liquid-glass.module.css');
const rootPackagePath = file('package.json');
const lockPath = file('pnpm-lock.yaml');
const page = read(pagePath);
const ogl = read(oglPath);
const css = read(cssPath);
const rootPackage = readJson(rootPackagePath);
const lock = read(lockPath);
const rootDeps = { ...(rootPackage.dependencies || {}), ...(rootPackage.devDependencies || {}) };
const targetLibs = [
  '@radix-ui/react-dialog',
  '@radix-ui/react-dropdown-menu',
  '@radix-ui/react-scroll-area',
  '@radix-ui/react-select',
  '@radix-ui/react-tabs',
  '@radix-ui/react-tooltip',
  '@radix-ui/react-slot',
  '@vanilla-extract/css',
  'ogl',
];

const familyBoardStart = page.indexOf('className={styles.familyBoard}');
const warningBandStart = page.indexOf('className={styles.warningBand}');
const familyBoardBlock = familyBoardStart >= 0 && warningBandStart > familyBoardStart
  ? page.slice(familyBoardStart, warningBandStart)
  : '';
const tabsListStart = page.indexOf('<Tabs.List');
const tabsListEnd = page.indexOf('</Tabs.List>');
const tabsListBlock = tabsListStart >= 0 && tabsListEnd > tabsListStart
  ? page.slice(tabsListStart, tabsListEnd)
  : '';

ok('page exists', fs.existsSync(pagePath));
ok('ogl component exists', fs.existsSync(oglPath));
ok('css exists', fs.existsSync(cssPath));
ok('page is client component', page.includes('"use client"'));
ok('page imports Radix ScrollArea', page.includes('@radix-ui/react-scroll-area'));
ok('page imports Radix Select', page.includes('@radix-ui/react-select'));
ok('page imports Radix Tabs', page.includes('@radix-ui/react-tabs'));
ok('page imports Radix Tooltip', page.includes('@radix-ui/react-tooltip'));
ok('page imports Radix Slot', page.includes('@radix-ui/react-slot'));
ok('page imports OGL aura component', page.includes('LiquidGlassOglAura'));
ok('page uses ScrollArea root and viewport', page.includes('<ScrollArea.Root') && page.includes('<ScrollArea.Viewport'));
ok('page uses Tabs.Root', page.includes('<Tabs.Root'));
ok('page keeps Tabs.Trigger inside Tabs.List', tabsListBlock.includes('<Tabs.Trigger asChild'));
ok('page has no Tabs.Trigger inside familyBoard', familyBoardBlock && !familyBoardBlock.includes('<Tabs.Trigger'));
ok('card action is non-button keyboard control', familyBoardBlock.includes('role="button"') && familyBoardBlock.includes('tabIndex={0}') && familyBoardBlock.includes('onKeyDown={(event) =>'));
ok('card action updates active family', familyBoardBlock.includes('onClick={() => setActiveId(family.id)}') && familyBoardBlock.includes('setActiveId(family.id);'));
ok('page uses Select trigger asChild', page.includes('<Select.Trigger asChild'));
ok('page uses Tooltip provider/content', page.includes('<Tooltip.Provider') && page.includes('<Tooltip.Content'));
ok('page does not use native button tags for family panels', !page.includes('<button') && !page.includes('</button>'));
ok('page tags glass panels', page.includes('data-lg-glass-panel="family-pill"') && page.includes('data-lg-glass-panel="family-card"'));
ok('page includes RGB family variables', page.includes('accentRgb') && page.includes('--family-accent-rgb'));
ok('page uses fix8 director marker', page.includes('radix-vanilla-ogl-fix8'));
ok('page includes cleaned Spanish text', !page.includes('versiÃ³n') && !page.includes('Â·') && !page.includes('�'));
ok('css has fixed background', css.includes('.fixedBackground') && css.includes('position: fixed'));
ok('css has shell scroll class', css.includes('.shellViewport') || css.includes('.shellScroller'));
ok('css has Radix scroll styling', css.includes('.scrollbar') && css.includes('.scrollThumb'));
ok('css has RGB glass variables', css.includes('--family-accent-rgb') && css.includes('--active-family-accent-rgb'));
ok('css has global button override escape', css.includes('[data-lg-glass-panel="family-pill"]'));
ok('css has no encoding artifacts', !css.includes('Â') && !css.includes('Ã') && !css.includes('�'));
ok('ogl imports ogl package', ogl.includes("from \"ogl\""));
ok('ogl is client component', ogl.includes('"use client"'));

for (const lib of targetLibs) {
  const inDeps = Boolean(rootDeps[lib]);
  const inLock = lock.includes(`${lib}@`) || lock.includes(`/${lib}@`) || lock.includes(lib);
  ok(`target lib available: ${lib}`, inDeps || inLock, 'Expected dependency in package.json or pnpm-lock.yaml');
}

const summary = {
  ok: fail.length === 0,
  pass_count: pass.length,
  fail_count: fail.length,
  pass,
  fail,
};
console.log(JSON.stringify(summary, null, 2));
process.exit(summary.ok ? 0 : 1);
