#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const cssPath = path.join(root, 'products/pc/app/app/suppliers-ux-v08.css');
const css = fs.readFileSync(cssPath, 'utf8');
const checks = [
  ['marker fix14 start', css.includes('PRISMA_PROVEEDORES_LETTERFALL_FIX_14_START')],
  ['marker fix14 end', css.includes('PRISMA_PROVEEDORES_LETTERFALL_FIX_14_END')],
  ['summary cards explicitly cancel global metric span', /supplier-summary-grid-v07\s*>\s*\.metric-card[\s\S]{0,900}grid-column:\s*auto\s*/.test(css)],
  ['metric-card-v07 selector covered', /supplier-summary-grid-v07\s*>\s*\.metric-card-v07[\s\S]{0,900}grid-column:\s*auto\s*/.test(css)],
  ['horizontal writing guard is important', /writing-mode:\s*horizontal-tb\s*/.test(css) && /text-orientation:\s*mixed\s*/.test(css)],
  ['global anywhere neutralized with important normal', /overflow-wrap:\s*normal\s*/.test(css)],
  ['long note fallback uses break-word important', /metric-note[\s\S]{0,500}overflow-wrap:\s*break-word\s*/.test(css)],
  ['desktop supplier shell guarded', /@media \(min-width:\s*1181px\)[\s\S]*grid-template-columns:\s*minmax\(232px,\s*260px\)\s*minmax\(0,\s*1fr\)\s*/.test(css)],
  ['summary grid stable desktop columns', /supplier-summary-grid-v07\s*\{[\s\S]{0,450}grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)\s*/.test(css)],
];
const failed = checks.filter(([, ok]) => !ok);
if (failed.length) {
  console.error('FAIL proveedores letterfall fix14');
  for (const [name] of failed) console.error('- ' + name);
  process.exit(1);
}
console.log('PASS proveedores letterfall fix14');
