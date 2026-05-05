#!/usr/bin/env node
import fs from 'node:fs';

function clamp(v, min = 0, max = 100) { return Math.min(max, Math.max(min, Number.isFinite(v) ? v : min)); }
function score(c, surface = 'tablet_pos') {
  const controls = Object.fromEntries(Object.entries(c || {}).map(([k, v]) => [k, clamp(Number(v))]));
  const readability = Math.round(((controls.contrast ?? 82) * .65) + ((100 - Math.max(0, (controls.blur ?? 18) - 38)) * .2) + ((100 - Math.max(0, (controls.neon ?? 42) - 58)) * .15));
  const operationBase = surface === 'tablet_pos' ? 78 : surface === 'pc_backoffice' ? 72 : 74;
  const density = controls.density ?? 55;
  const motionValue = controls.motion ?? 30;
  const operation = Math.round(operationBase + (density > 30 && density < 78 ? 10 : -8) + (motionValue < 58 ? 8 : -10));
  const premium = Math.round(((controls.glass ?? 70) + (controls.depth ?? 70) + (controls.shadow ?? 68) + (controls.shine ?? 60) + (controls.edge ?? 70)) / 5);
  const motion = Math.round(100 - Math.max(0, motionValue - 34) * 1.15);
  const safety = Math.round((readability * .55) + (operation * .35) + (motion * .1));
  const overall = Math.max(0, Math.min(100, Math.round((readability * .28) + (operation * .25) + (premium * .26) + (motion * .1) + (safety * .11))));
  const verdict = readability < 58 || operation < 55 || safety < 58 ? 'BLOCKED' : overall < 78 ? 'WARN' : 'READY';
  return { overall, readability, operation, premium, motion, safety, verdict };
}
const file = process.argv[2];
if (!file) { console.error('Usage: node score_prisma_studio_pro_00s.mjs <payload-or-recipe.json>'); process.exit(2); }
const data = JSON.parse(fs.readFileSync(file, 'utf8'));
const result = score(data.controls || data, data.surface || 'tablet_pos');
console.log(JSON.stringify(result, null, 2));
process.exit(result.verdict === 'BLOCKED' ? 3 : 0);
