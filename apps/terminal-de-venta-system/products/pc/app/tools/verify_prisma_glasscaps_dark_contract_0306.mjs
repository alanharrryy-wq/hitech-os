import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const files = {
  componentCss: path.join(root, 'components/prisma-glass-capsule/prisma-glass-capsule.module.css'),
  componentTsx: path.join(root, 'components/prisma-glass-capsule/prisma-glass-capsule.tsx'),
  pageCss: path.join(root, 'referencia-visual/liquid-glass-capsules/liquid-glass-capsules.module.css'),
  pageTsx: path.join(root, 'referencia-visual/liquid-glass-capsules/page.tsx'),
};

function read(file) {
  if (!fs.existsSync(file)) throw new Error(`Missing file: ${file}`);
  return fs.readFileSync(file, 'utf8');
}

function assertContains(text, needle, label) {
  if (!text.includes(needle)) throw new Error(`Missing ${label}: ${needle}`);
}

function assertNotContains(text, needle, label) {
  if (text.includes(needle)) throw new Error(`Forbidden ${label}: ${needle}`);
}

const css = read(files.componentCss);
const tsx = read(files.componentTsx);
const pageCss = read(files.pageCss);
const pageTsx = read(files.pageTsx);
const failures = [];
function check(fn) { try { fn(); } catch (error) { failures.push(error.message); } }

check(() => assertContains(css, '--pgc-blur: 0.25px;', 'near-zero blur token'));
check(() => assertNotContains(css, '26px', 'old heavy blur'));
check(() => assertNotContains(css, '--pgc-context-accent', 'fixed global color accent token'));
check(() => assertNotContains(css, 'rgba(61, 214, 255, .34)', 'old global blue tint'));
check(() => assertContains(tsx, 'styles.edgeFrame', 'outer reactive edge frame span'));
check(() => assertContains(tsx, 'styles.volumeFrame', 'middle volume frame span'));
check(() => assertContains(tsx, 'styles.innerFrame', 'inner refractive frame span'));
check(() => assertContains(tsx, 'styles.lobeLens', 'localized lobe lens span'));
check(() => assertContains(css, '.edgeFrame', 'edge frame css'));
check(() => assertContains(css, 'padding: 2px;', '2px reactive edge line'));
check(() => assertContains(css, '.volumeFrame', 'volume frame css'));
check(() => assertContains(css, '.innerFrame', 'inner frame css'));
check(() => assertContains(css, '.lobeLens', 'lobe lens css'));
check(() => assertContains(css, 'backdrop-filter: blur(.35px)', 'localized lobe nearly-zero blur'));
check(() => assertContains(pageCss, '--pair-gap: min(1cm, 36px);', 'max 1cm pair gap'));
check(() => assertContains(pageCss, '--pair-space: 5cm;', '5cm pair spacing'));
check(() => assertContains(pageCss, '.motionBackplate', 'fixed dark backplate'));
check(() => assertContains(pageCss, 'position: fixed;', 'fixed background behavior'));
check(() => assertContains(pageCss, '.backText', 'background text'));
check(() => assertContains(pageCss, '.backTextMassive', 'multiple font sizes'));
check(() => assertContains(pageCss, '.backTextSmall', 'small font size'));
check(() => assertContains(pageTsx, 'const sixPills', 'six pill row data'));
const pillItems = [...pageTsx.matchAll(/label: '/g)].length;
check(() => { if (pillItems !== 6) throw new Error(`Expected 6 pills, got ${pillItems}`); });
const pairCount = [...pageTsx.matchAll(/styles\.geoPair/g)].length;
check(() => { if (pairCount < 9) throw new Error(`Expected at least 9 geometry pairs, got ${pairCount}`); });
check(() => assertContains(pageTsx, 'NO GLOBAL BLUE', 'background text contract'));
check(() => assertContains(pageCss, '-webkit-backdrop-filter: none;', 'stage panels do not blur the whole demo'));

if (failures.length) {
  console.error('PRISMA dark glass contract verifier FAIL');
  for (const failure of failures) console.error(' - ' + failure);
  process.exit(1);
}
console.log(JSON.stringify({ status: 'PASS', verifier: 'verify_prisma_glasscaps_dark_contract_0306', blurMaxPx: 0.35, pillCount: 6, geometryPairs: pairCount }, null, 2));
