#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
let failed = false;
function ok(message) { console.log(`OK ${message}`); }
function fail(message) { console.error(`FAIL ${message}`); failed = true; }
function read(rel) { return fs.readFileSync(path.join(root, rel), "utf8"); }

const source = read("src/lib/tablet-home/operational-priority.ts");
const fixture = JSON.parse(read("tools/fixtures/tablet_operational_priorities_03c_cases.json"));

const requiredNeedles = [
  "buildTabletOperationalPriorities",
  "getHighestOperationalPriority",
  "connection_conflict",
  "connection_failed",
  "connection_pending",
  "catalog_empty",
  "stock_pressure",
  "quiet_day",
  "sortPriorities(priorities).slice(0, 4)",
  "reasonSignals"
];
for (const needle of requiredNeedles) {
  source.includes(needle) ? ok(`priority source includes ${needle}`) : fail(`priority source missing ${needle}`);
}

const weightByKey = new Map();
for (const match of source.matchAll(/key:\s*"([^"]+)"[\s\S]*?weight:\s*(\d+)/g)) {
  weightByKey.set(match[1], Number(match[2]));
}
const requiredWeights = {
  shift_closed: 90,
  connection_conflict: 95,
  connection_failed: 88,
  connection_pending: 72,
  catalog_empty: 82,
  stock_pressure: 64,
  quiet_day: 20
};
for (const [key, expectedWeight] of Object.entries(requiredWeights)) {
  const actual = weightByKey.get(key);
  actual === expectedWeight ? ok(`priority ${key} weight ${actual}`) : fail(`priority ${key} expected weight ${expectedWeight}, got ${actual}`);
}

if (!Array.isArray(fixture.cases) || fixture.cases.length < 7) {
  fail("priority fixture must cover at least 7 operational states");
} else {
  ok(`priority fixture cases ${fixture.cases.length}`);
}

for (const item of fixture.cases) {
  if (!item.name || !item.input || !item.expectedFirstKey || !item.expectedTitle) {
    fail(`priority fixture malformed: ${JSON.stringify(item)}`);
    continue;
  }
  if (!source.includes(`key: "${item.expectedFirstKey}"`)) fail(`${item.name} references missing key ${item.expectedFirstKey}`);
  if (!source.includes(item.expectedTitle)) fail(`${item.name} expected title not present in source: ${item.expectedTitle}`);
  ok(`priority fixture ${item.name}`);
}

if (!read("src/lib/tablet-home/home-view-model.ts").includes("buildTabletOperationalPriorities(snapshot)")) {
  fail("home view-model does not consume operational priorities");
} else {
  ok("home view-model consumes operational priorities");
}

if (failed) process.exit(1);
ok("operational priorities static matrix passed");
