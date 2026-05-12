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
  const workspaces = ['products/tablet/app', 'products/pc/app', 'products/mobile/app', 'products/chart-lab/app'];
  const scriptMatrix = workspaceScriptMatrix(ctx.repoRoot, workspaces);
  const routeChecks = [
    { layer: 'Tablet', path: 'products/tablet/app/app/api/health/route.ts', required: true },
    { layer: 'PC', path: 'products/pc/app/app/api/backoffice/audit/recent/route.ts', required: false },
    { layer: 'PC', path: 'products/pc/app/app/api/backoffice/dashboard/route.ts', required: false },
    { layer: 'Mobile', path: 'products/mobile/app/app/api/mobile/health/route.ts', required: false },
    { layer: 'Mobile', path: 'products/mobile/app/app/api/mobile/snapshot/route.ts', required: false },
    { layer: 'ChartLab', path: 'products/chart-lab/app/app/page.tsx', required: false }
  ].map(check => ({ ...check, exists: pathExists(path.join(ctx.repoRoot, check.path)) }));

  const evidence = [createEvidence(ctx, 'Q5', 'operational_flows_surface', 'Operational flow route and workspace script surface', { scriptMatrix, routeChecks })];
  const findings = [];
  for (const row of scriptMatrix) {
    if (!row.exists) findings.push(finding({ id: `Q5_WORKSPACE_MISSING_${row.workspace.replaceAll('/','_')}`, severity: 'S1', layer: 'Runtime', title: 'Workspace package missing', detail: `${row.workspace}/package.json was not found.`, file: row.packagePath, evidence, recommendation: 'Restore workspace package.json or update quality.config.json.' }));
    if (row.exists && !row.hasDev) findings.push(finding({ id: `Q5_DEV_SCRIPT_MISSING_${row.workspace.replaceAll('/','_')}`, severity: 'S3', layer: 'Runtime', title: 'Workspace dev script missing', detail: `${row.workspace} has no dev script.`, file: row.packagePath, evidence, recommendation: 'Add a dev script or document why this workspace is not runnable.' }));
    if (row.exists && !row.hasBuild) findings.push(finding({ id: `Q5_BUILD_SCRIPT_MISSING_${row.workspace.replaceAll('/','_')}`, severity: 'S3', layer: 'Runtime', title: 'Workspace build script missing', detail: `${row.workspace} has no build script.`, file: row.packagePath, evidence, recommendation: 'Add a build script or declare this workspace as non-buildable.' }));
  }
  for (const check of routeChecks.filter(c => c.required && !c.exists)) {
    findings.push(finding({ id: `Q5_REQUIRED_ROUTE_MISSING_${check.layer}`, severity: 'S1', layer: check.layer, title: 'Required operational route missing', detail: `${check.path} was not found.`, file: check.path, evidence, recommendation: 'Restore route or update Phase 2 runtime expectations.' }));
  }
  return { gateId: 'Q5', title: 'Operational Flows Surface', status: findings.some(f => ['S0','S1'].includes(f.severity)) ? 'BLOCKED' : 'READY', summary: `${routeChecks.filter(r => r.exists).length}/${routeChecks.length} operational route signals found.`, findings, evidence };
}
