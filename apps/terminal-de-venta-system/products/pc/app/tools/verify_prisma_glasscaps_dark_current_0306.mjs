#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const pcApp = root.endsWith(path.join('products','pc','app')) ? root : path.join(root, 'products', 'pc', 'app');
function read(rel) {
  const p = path.join(pcApp, rel);
  if (!fs.existsSync(p)) throw new Error(`Missing file: ${rel}`);
  return fs.readFileSync(p, 'utf8');
}
function assert(cond, msg) { if (!cond) throw new Error(msg); }

const componentCss = read('components/prisma-glass-capsule/prisma-glass-capsule.module.css');
const componentTsx = read('components/prisma-glass-capsule/prisma-glass-capsule.tsx');
const appCss = read('app/referencia-visual/liquid-glass-capsules/liquid-glass-capsules.module.css');
const legacyCss = read('referencia-visual/liquid-glass-capsules/liquid-glass-capsules.module.css');
const appPage = read('app/referencia-visual/liquid-glass-capsules/page.tsx');
const legacyPage = read('referencia-visual/liquid-glass-capsules/page.tsx');

assert(componentTsx.includes('styles.edgeFrame') && componentTsx.includes('styles.volumeFrame') && componentTsx.includes('styles.innerFrame'), 'Component must render three real frames');
assert(componentCss.includes('.edgeFrame') && componentCss.includes('.volumeFrame') && componentCss.includes('.innerFrame'), 'CSS must define three frames');
assert(componentCss.includes('--pgc-blur: 0.06px;'), 'Base blur must be almost zero: 0.06px');
assert(componentCss.includes('blur(.08px) saturate'), 'Lobe lens must use almost-zero blur and stronger optical filtering');
assert(!componentCss.includes('rgba(212,245,255,.24)'), 'Thinking tone still has fixed blue border color');
assert(!componentCss.includes('rgba(245,253,255,.44)'), 'Thinking tone still has fixed blue strong border color');
assert(!componentCss.includes('--pgc-blur: 0.25px;'), 'Old 0.25px blur remains');
assert(!componentCss.includes('blur(.35px)'), 'Old .35px lobe blur remains');
assert(componentCss.includes('padding: 2px;'), 'Outer edge frame must keep 2px reactive line');
assert(componentCss.includes('-webkit-backdrop-filter') && componentCss.includes('backdrop-filter'), 'Need webkit and standard backdrop-filter');

for (const [name, css] of [['app', appCss], ['legacy', legacyCss]]) {
  assert(css.includes('position: fixed;'), `${name} backplate must be fixed`);
  assert(css.includes('z-index: 0;'), `${name} motionBackplate must be visible above page background`);
  assert(!css.includes('z-index: -2;'), `${name} must not bury backplate behind page background`);
  assert(css.includes('--pair-gap: .72cm;'), `${name} must use pair gap under 1cm`);
  assert(css.includes('--pair-space: 5cm;'), `${name} must keep 5cm space between pairs`);
  assert(css.includes('.geoPairJ') && css.includes('.geoPairK') && css.includes('.geoPairL'), `${name} must include extra color-pair positions`);
  assert(css.includes('.hero,\n.visualProof,\n.scrollProof {\n  position: relative;\n  z-index: 2;'), `${name} content sections must sit over fixed backplate`);
  assert(css.includes('.geoCircle { width: 1.44rem;'), `${name} geometry must be smaller than old large blocks`);
}

for (const [name, page] of [['app', appPage], ['legacy', legacyPage]]) {
  const labels = [...page.matchAll(/label: '([^']+)'/g)].map(m => m[1]);
  assert(labels.length === 6, `${name} must keep exactly six pills in the horizontal demo row`);
  for (const pair of ['geoPairA','geoPairB','geoPairC','geoPairD','geoPairE','geoPairF','geoPairG','geoPairH','geoPairI','geoPairJ','geoPairK','geoPairL']) {
    assert(page.includes(`styles.${pair}`), `${name} missing ${pair}`);
  }
  assert(page.includes('FIX6 current') || page.includes('Fix6 current'), `${name} copy must identify current-code fix6`);
}

console.log('PASS verify_prisma_glasscaps_dark_current_0306');
