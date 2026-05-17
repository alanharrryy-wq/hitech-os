import fs from 'node:fs';
import path from 'node:path';
import { createEvidence } from '../core/evidence-writer.mjs';
import { finding } from '../core/result-types.mjs';
import { pathExists, listFiles, readTextSafe, rel, toPosix } from '../core/paths.mjs';
function includesAny(text, terms) { const lower = String(text).toLowerCase(); return terms.some(t => lower.includes(String(t).toLowerCase())); }

    export async function run(ctx) {
      const prismaRoot = path.join(ctx.repoRoot, ctx.config.roots.prisma);
      const schemaPath = path.join(prismaRoot, 'schema.prisma');
      const migrationRoot = path.join(prismaRoot, 'migrations');
      const migrationFiles = pathExists(migrationRoot) ? listFiles(migrationRoot, { maxBytes: 1048576, extensions: ['.sql'], ignore: ctx.config.ignore }) : [];
      const destructive = [];
      const destructiveRegex = new RegExp('\\bDROP\\s+TABLE\\b|\\bDROP\\s+COLUMN\\b|\\bALTER\\s+TABLE[\\s\\S]{0,160}\\bDROP\\b', 'i');
      for (const f of migrationFiles) if (destructiveRegex.test(readTextSafe(f))) destructive.push(rel(ctx, f));
      const evidence = [createEvidence(ctx, 'Q3', 'schema_migration_safety', 'Schema and migration static safety inspection', { schemaExists: pathExists(schemaPath), migrationCount: migrationFiles.length, destructive })];
      const findings = [];
      if (!pathExists(schemaPath)) findings.push(finding({ id: 'Q3_SCHEMA_MISSING', severity: 'S1', layer: 'Core', title: 'schema.prisma missing', detail: 'Prisma schema was not found.', file: rel(ctx, schemaPath), recommendation: 'Restore schema.prisma or update PQOS config.' }));
      for (const f of destructive) findings.push(finding({ id: `Q3_DESTRUCTIVE_${findings.length+1}`, severity: 'S1', layer: 'Core', title: 'Potential destructive migration detected', detail: `Destructive SQL signal found in ${f}.`, file: f, recommendation: 'Document and isolate destructive changes. Real DB remains inspect-only.' }));
      return { gateId: 'Q3', title: 'Schema & Migration Safety Static', status: findings.length ? 'BLOCKED' : 'READY', summary: `Schema ${pathExists(schemaPath) ? 'found' : 'missing'}, ${migrationFiles.length} migration SQL files scanned.`, findings, evidence };
    }
