import fs from 'node:fs';
import path from 'node:path';

const appRoot = process.cwd();
const projectRoot = path.resolve(appRoot, '..', '..', '..');
const runtime = path.join(appRoot, 'app', 'visual-os', '_tablet-gallery-runtime.tsx');
const docsAsset = path.join(projectRoot, 'docs', 'design', 'tablet-light-visual-preset-engine', 'assets', 'backgrounds', 'storm-cloud-operations-real.jpg');
const publicAsset = path.join(appRoot, 'public', 'visual-os', 'tablet-light-visual-preset-engine', 'assets', 'backgrounds', 'storm-cloud-operations-real.jpg');
const cssDocs = path.join(projectRoot, 'docs', 'design', 'tablet-light-visual-preset-engine', 'prisma-tablet-background-storm-glass-v8.css');
const publicUrl = '/visual-os/tablet-light-visual-preset-engine/assets/backgrounds/storm-cloud-operations-real.jpg';

function fail(message) {
  console.error('[V12 VERIFY FAIL]', message);
  process.exit(1);
}

function ok(message) {
  console.log('[V12 VERIFY OK]', message);
}

if (!fs.existsSync(runtime)) fail('runtime missing: ' + runtime);
const src = fs.readFileSync(runtime, 'utf8');

for (const marker of [
  'TABLET_VISUAL_OS_PUBLIC_BASE',
  'rewriteSrcDocRelativeAssetUrls',
  'ensureSrcDocBaseHref',
  '/visual-os/tablet-light-visual-preset-engine/'
]) {
  if (!src.includes(marker)) fail('runtime marker missing: ' + marker);
}

if (!fs.existsSync(docsAsset)) fail('docs storm asset missing: ' + docsAsset);
if (!fs.existsSync(publicAsset)) fail('public storm asset missing: ' + publicAsset);
if (fs.statSync(publicAsset).size < 100000) fail('public storm asset unexpectedly small');
if (!fs.existsSync(cssDocs)) fail('storm css missing: ' + cssDocs);

const css = fs.readFileSync(cssDocs, 'utf8');
if (!css.includes('./assets/backgrounds/storm-cloud-operations-real.jpg')) {
  fail('source css no longer exercises relative asset resolver');
}

const simulated = css
  .replace(/url\(\s*(["']?)(\.\/assets\/|assets\/)([^"')]+)\1\s*\)/gi, (_m, _q, prefix, rest) => {
    const cleanPrefix = String(prefix).replace(/^\.\//, '');
    return `url("/visual-os/tablet-light-visual-preset-engine/${cleanPrefix}${rest}")`;
  })
  .replace(/\b(src|href)=(["'])(\.\/assets\/|assets\/)([^"']+)\2/gi, (_m, attr, quote, prefix, rest) => {
    const cleanPrefix = String(prefix).replace(/^\.\//, '');
    return `${attr}=${quote}/visual-os/tablet-light-visual-preset-engine/${cleanPrefix}${rest}${quote}`;
  });

if (!simulated.includes(publicUrl)) fail('simulated rewrite did not produce public storm URL');

ok('runtime asset resolver markers present');
ok('storm image exists in docs and public');
ok('relative ./assets resolver scenario covered');
