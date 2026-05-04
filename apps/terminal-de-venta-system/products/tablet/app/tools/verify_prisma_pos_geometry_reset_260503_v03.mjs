import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const files = [
  'components/pos/pos.module.css',
  'components/tablet-shell/prisma-tablet-shell.module.css'
];
const required = [
  'PRISMA_POS_GEOMETRY_RESET_260503_V03_BEGIN',
  'transform: none !important'
];
const forbidden = [
  'PRISMA_POS_VISUAL_DOM_BINDING_LOCK_260503_V02_BEGIN',
  'PRISMA_POS_LAYOUT_CONTAINMENT_REPAIR_260503_V01_BEGIN',
  'PRISMA_POS_VISUAL_DOM_ALIGNMENT_LOCK_260503',
  'PRISMA_POS_VISUAL_FORCE_LOCK_260503_BEGIN'
];
for (const rel of files) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) throw new Error(`Missing ${rel}`);
  const text = fs.readFileSync(abs, 'utf8');
  for (const token of required) {
    if (!text.includes(token)) throw new Error(`${rel} missing ${token}`);
  }
  for (const token of forbidden) {
    if (text.includes(token)) throw new Error(`${rel} still contains forbidden visual lock ${token}`);
  }
}
console.log('OK PRISMA_POS_GEOMETRY_RESET_260503_v03 verified no bad visual locks and geometry reset present');
