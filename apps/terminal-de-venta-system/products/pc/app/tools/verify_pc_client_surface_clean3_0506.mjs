#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const layout = path.join(root, 'app', 'layout.tsx');
const cleaner = path.join(root, 'app', 'prisma-dev-issue-badge-cleaner.tsx');
const doc = path.join(root, 'docs', 'pc-client-surface-clean3-0506.md');

const checks = [];
function check(name, ok) { checks.push({ name, ok: !!ok }); }
function read(file) { return fs.existsSync(file) ? fs.readFileSync(file, 'utf8') : ''; }

const layoutText = read(layout);
const cleanerText = read(cleaner);
const docText = read(doc);

check('cleaner component exists', fs.existsSync(cleaner));
check('layout imports PrismaDevIssueBadgeCleaner', /PrismaDevIssueBadgeCleaner/.test(layoutText));
check('layout renders PrismaDevIssueBadgeCleaner', /<PrismaDevIssueBadgeCleaner\s*\/>/.test(layoutText));
check('cleaner is client component', /^"use client";/.test(cleanerText.trim()));
check('cleaner targets Issue badges', /ISSUE_BADGE_PATTERN/.test(cleanerText) && /issues\?/i.test(cleanerText));
check('cleaner targets compact Next dev mark', /NEXT_DEV_MARK_PATTERN/.test(cleanerText));
check('cleaner limits to bottom-left', /nearLeft/.test(cleanerText) && /nearBottom/.test(cleanerText));
check('cleaner avoids broad portal hiding', !/nextjs-portal[^\n]*display\s*:\s*none/i.test(cleanerText));
check('cleaner uses MutationObserver', /MutationObserver/.test(cleanerText));
check('documentation installed', /Limpieza visual PC/.test(docText));

const failed = checks.filter(c => !c.ok);
for (const c of checks) console.log(`${c.ok ? 'PASS' : 'FAIL'} ${c.name}`);
if (failed.length) {
  console.error(`clean3 verifier failed: ${failed.length}/${checks.length}`);
  process.exit(1);
}
console.log(`clean3 verifier PASS: ${checks.length}/${checks.length}`);
