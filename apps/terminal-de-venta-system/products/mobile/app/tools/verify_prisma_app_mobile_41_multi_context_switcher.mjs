import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const required = [
  'src/components/prisma-app/PrismaMobileMultiContextSwitcher.tsx',
  'src/components/prisma-app/prisma-mobile-multi-context-switcher.module.css',
  'src/components/prisma-app/index.ts',
  'src/components/prisma-app/PrismaMobileDashboard.tsx',
  'docs/prisma-app/PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE.md'
];

const failures = [];
for (const rel of required) {
  if (!fs.existsSync(path.join(root, rel))) failures.push(`Missing required file: ${rel}`);
}

function read(rel) {
  return fs.existsSync(path.join(root, rel)) ? fs.readFileSync(path.join(root, rel), 'utf8') : '';
}

const component = read('src/components/prisma-app/PrismaMobileMultiContextSwitcher.tsx');
const css = read('src/components/prisma-app/prisma-mobile-multi-context-switcher.module.css');
const dashboard = read('src/components/prisma-app/PrismaMobileDashboard.tsx');
const index = read('src/components/prisma-app/index.ts');
const pkg = read('package.json');

const expectations = [
  [component.includes('PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE'), 'component lacks render-grade contract marker'],
  [component.includes('Mobile supervisa. Tablet opera. Core registra evidencia.'), 'component lacks canonical supervision boundary copy'],
  [component.includes('sourceLabel(clientSnapshot.source)'), 'component does not use existing source labels'],
  [component.includes('snapshot.dataQuality.sources'), 'component does not expose source quality context'],
  [component.includes('snapshot.branches.branches'), 'component does not derive contexts from real branch payload'],
  [component.includes('useState<VisualTheme>'), 'component lacks local theme state'],
  [css.includes('.obsidian') && css.includes('.silver') && css.includes('.graphite'), 'css lacks the three premium themes'],
  [css.includes('@keyframes mcsSheen') && css.includes('@keyframes mcsSpin') && css.includes('@keyframes mcsCta'), 'css lacks required microinteraction keyframes'],
  [dashboard.includes('PrismaMobileMultiContextSwitcher'), 'dashboard does not render multi-context switcher'],
  [index.includes('PrismaMobileMultiContextSwitcher'), 'component is not exported'],
  [pkg.includes('verify:multi-context-switcher'), 'package.json lacks verify script']
];
for (const [ok, message] of expectations) if (!ok) failures.push(message);

const forbidden = [
  'Mobile vende',
  'Mobile opera ventas',
  'PC obligatorio',
  'Tablet depende de Mobile',
  'fake green',
  'demo mode'
];
for (const marker of forbidden) {
  if (component.includes(marker) || css.includes(marker)) failures.push(`Forbidden boundary marker found: ${marker}`);
}

if (failures.length > 0) {
  console.error('PRISMA App Mobile 41 Multi-context Switcher verifier: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('PRISMA App Mobile 41 Multi-context Switcher verifier: PASS');
console.log(JSON.stringify({
  contract: 'PRISMA_APP_MOBILE_41_MULTI_CONTEXT_SWITCHER_RENDER_GRADE',
  scope: 'visual-ui-only',
  mobileRole: 'supervision-layer',
  tabletRole: 'operates-independently',
  filesChecked: required.length
}, null, 2));
