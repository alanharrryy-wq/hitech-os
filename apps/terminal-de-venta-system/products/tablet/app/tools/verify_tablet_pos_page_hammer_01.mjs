#!/usr/bin/env node
/* PRISMA_REPAIRALL1_POS_PAGE_HAMMER_GATE */
import fs from 'node:fs';
import path from 'node:path';
import { performance } from 'node:perf_hooks';

const baseUrl = process.env.PRISMA_POS_HAMMER_BASE_URL || 'http://127.0.0.1:3120';
const outputDir = process.env.PRISMA_POS_HAMMER_OUT || 'F:/descargasf';
const requests = Number(process.env.PRISMA_POS_HAMMER_REQUESTS || '24');
const workers = Number(process.env.PRISMA_POS_HAMMER_WORKERS || '6');
const timeoutMs = Number(process.env.PRISMA_POS_HAMMER_TIMEOUT_MS || '8000');
const maxP95Ms = Number(process.env.PRISMA_POS_HAMMER_MAX_P95_MS || '2500');
const minOk = Number(process.env.PRISMA_POS_HAMMER_MIN_OK || String(requests));

function percentile(values, p) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const idx = Math.max(0, Math.min(sorted.length - 1, Math.round((p / 100) * (sorted.length - 1))));
  return sorted[idx];
}

function withTimeout(promise, ms) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  return {
    signal: controller.signal,
    done: promise.finally(() => clearTimeout(timer)),
  };
}

async function one(url) {
  const started = performance.now();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: { 'user-agent': 'PRISMA-repairall1-pos-hammer/1.0' },
      cache: 'no-store',
    });
    const sample = await response.text();
    const ms = performance.now() - started;
    return {
      ok: response.status >= 200 && response.status < 500,
      status: response.status,
      ms: Number(ms.toFixed(2)),
      bytes: sample.length,
      hasHtml: sample.includes('<html') || sample.includes('<!DOCTYPE'),
      hasPrisma: sample.toLowerCase().includes('prisma'),
      error: null,
    };
  } catch (error) {
    const ms = performance.now() - started;
    return {
      ok: false,
      status: null,
      ms: Number(ms.toFixed(2)),
      bytes: 0,
      hasHtml: false,
      hasPrisma: false,
      error: `${error?.name || 'Error'}: ${error?.message || String(error)}`,
    };
  } finally {
    clearTimeout(timer);
  }
}

async function hammer(pathname) {
  const url = `${baseUrl}${pathname}`;
  const results = [];
  let cursor = 0;

  async function worker() {
    while (cursor < requests) {
      cursor += 1;
      results.push(await one(url));
    }
  }

  await Promise.all(Array.from({ length: workers }, () => worker()));
  const ok = results.filter((item) => item.ok);
  const hard = results.filter((item) => !item.ok);
  const times = results.map((item) => item.ms);
  const statusCounts = {};
  for (const item of results) {
    const key = String(item.status);
    statusCounts[key] = (statusCounts[key] || 0) + 1;
  }
  return {
    url,
    requests,
    workers,
    timeoutMs,
    okCount: ok.length,
    hardFailureCount: hard.length,
    statusCounts,
    p50Ms: percentile(times, 50),
    p95Ms: percentile(times, 95),
    maxMs: times.length ? Math.max(...times) : null,
    results,
  };
}

const started = new Date();
fs.mkdirSync(outputDir, { recursive: true });
const result = {
  marker: 'PRISMA_REPAIRALL1_POS_PAGE_HAMMER_GATE',
  startedAt: started.toISOString(),
  baseUrl,
  thresholds: { requests, workers, timeoutMs, maxP95Ms, minOk },
  routes: {
    pos: await hammer('/pos'),
    tabletHealth: await hammer('/api/health'),
    syncPanel: await hammer('/api/pos/sync/panel?limit=5'),
  },
};
result.finishedAt = new Date().toISOString();

const reportPath = path.join(outputDir, `repairall1-pos-hammer-${Date.now()}.json`);
fs.writeFileSync(reportPath, JSON.stringify(result, null, 2), 'utf8');

const failures = [];
for (const [name, route] of Object.entries(result.routes)) {
  if (route.okCount < minOk) failures.push(`${name}: okCount ${route.okCount} < ${minOk}`);
  if (route.hardFailureCount > 0) failures.push(`${name}: hardFailureCount ${route.hardFailureCount}`);
  if (route.p95Ms !== null && route.p95Ms > maxP95Ms) failures.push(`${name}: p95 ${route.p95Ms} > ${maxP95Ms}`);
}

console.log(JSON.stringify({ reportPath, failures, summary: result.routes }, null, 2));
if (failures.length) process.exit(1);
