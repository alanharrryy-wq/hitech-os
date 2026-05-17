import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, toPosix } from '../core/paths.mjs';
import { workspaceScriptMatrix } from '../core/package-scripts.mjs';

function readSafe(p) { try { return fs.readFileSync(p, 'utf8'); } catch { return ''; } }
function readJsonSafe(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch (error) { return { __error: error.message || String(error) }; } }
function rel(ctx, p) { return toPosix(path.relative(ctx.repoRoot, p)); }

export async function run(ctx) {
  const surfaces = [
    { layer: 'Tablet', path: 'products/tablet/app/app/page.tsx', required: true },
    { layer: 'Tablet', path: 'products/tablet/app/app/layout.tsx', required: true },
    { layer: 'PC', path: 'products/pc/app/app/dashboard/page.tsx', required: false },
    { layer: 'PC', path: 'products/pc/app/app/page.tsx', required: false },
    { layer: 'Mobile', path: 'products/mobile/app/app/page.tsx', required: false },
    { layer: 'Mobile', path: 'products/mobile/app/app/prisma-command/page.tsx', required: false },
    { layer: 'ChartLab', path: 'products/chart-lab/app/app/page.tsx', required: false }
  ].map(s => ({ ...s, exists: pathExists(path.join(ctx.repoRoot, s.path)) }));
  const filesToScan = surfaces.filter(s => s.exists).map(s => path.join(ctx.repoRoot, s.path));
  const fillerSignals = [];
  for (const file of filesToScan) {
    const text = readSafe(file);
    if (/TODO|lorem ipsum|placeholder|coming soon|fake data only/i.test(text)) fillerSignals.push(rel(ctx, file));
  }
  const evidence = [createEvidence(ctx, 'Q14', 'ux_operability_static', 'UX operability surface scan for app entries and obvious filler signals', { surfaces, fillerSignals })];
  const findings = [];
  for (const s of surfaces.filter(x => x.required && !x.exists)) findings.push(finding({ id: `Q14_REQUIRED_SURFACE_MISSING_${s.layer}`, severity: 'S1', layer: s.layer, title: 'Required UI surface missing', detail: `${s.path} was not found.`, file: s.path, evidence, recommendation: 'Restore required app page/layout.' }));
  for (const f of fillerSignals) findings.push(finding({ id: `Q14_FILLER_SIGNAL_${findings.length+1}`, severity: 'S3', layer: 'UX', title: 'Possible filler UI signal', detail: `Possible placeholder/filler signal in ${f}.`, file: f, evidence, recommendation: 'Confirm the screen is production-intentional and not filler.' }));
  return { gateId: 'Q14', title: 'UX Operability Static', status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY', summary: `${surfaces.filter(s=>s.exists).length}/${surfaces.length} UI entry surfaces found.`, findings, evidence };
}
