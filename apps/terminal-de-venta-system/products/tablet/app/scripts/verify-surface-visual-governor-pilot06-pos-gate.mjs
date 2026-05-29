/* PRISMA Surface Visual Governor · Pilot 06 POS Final Gate verifier */
import fs from 'node:fs';
import path from 'node:path';

const root = process.env.PRISMA_REPO_ROOT || '<LOCAL_PATH>';
function mustReadJson(rel) {
  const p = path.join(root, rel);
  if (!fs.existsSync(p)) throw new Error(`Missing ${rel}`);
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}
function mustExist(rel) {
  const p = path.join(root, rel);
  if (!fs.existsSync(p)) throw new Error(`Missing ${rel}`);
}

const base = 'products/tablet/app/public/surface-visual-governor/pos-final-gate/latest';
mustExist('products/tablet/app/app/pos/page.tsx');
mustExist('products/tablet/app/app/checkout/page.tsx');
mustExist(`${base}/index.json`);
mustExist(`${base}/pos.compatibility.gate.json`);
mustExist(`${base}/pos.visual-budget.json`);

const index = mustReadJson(`${base}/index.json`);
const gate = mustReadJson(`${base}/pos.compatibility.gate.json`);
const budget = mustReadJson(`${base}/pos.visual-budget.json`);

const failures = [];
if (index.pos_modified_by_this_pilot !== false) failures.push('index must state POS is not modified by this pilot');
if (index.checkout_protected !== true) failures.push('checkout must be protected');
if (gate.allowed_only_if.light_only !== true) failures.push('POS gate must be light_only');
if (gate.allowed_only_if.touch_first !== true) failures.push('POS gate must be touch_first');
if (gate.allowed_only_if.blur_budget_px_max > 1) failures.push('POS blur budget must be <= 1px');
for (const key of ['webgl','pixi_vapor','dark_storm','storm_cloud_default','heavy_backdrop_blur','background_animation_over_checkout','background_competing_with_product_or_payment']) {
  if (gate.forbidden_runtime_effects[key] !== false) failures.push(`Forbidden runtime effect must be false: ${key}`);
}
if (budget.budget.webgl !== 0) failures.push('Budget webgl must be 0');
if (budget.budget.pixi !== 0) failures.push('Budget pixi must be 0');
if (budget.budget.blur_px.max > 1) failures.push('Budget blur max must be <= 1');

if (failures.length) {
  console.error(JSON.stringify({status:'FAIL', failures}, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({status:'PASS', pilot:'06_pos_final_gate_audit', findings:index.pos_scan?.findings?.length || 0}, null, 2));
