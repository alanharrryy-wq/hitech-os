#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
function read(rel) { return fs.readFileSync(path.join(root, rel), "utf8"); }
function assert(condition, message) { if (!condition) { console.error(`FAIL ${message}`); process.exit(1); } }
function exists(rel) { assert(fs.existsSync(path.join(root, rel)), `missing ${rel}`); }

const required = [
  "app/api/mobile/pulse-timeline/route.ts",
  "src/lib/prisma-app/prisma-mobile-pulse-timeline.ts",
  "src/components/prisma-app/PrismaMobilePulseTimeline.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "docs/prisma-app/PRISMA_APP_MOBILE_24_PULSE_TIMELINE.md",
  "docs/prisma-app/qa/prisma-app-mobile-24-pulse-timeline-scenarios.json",
  "docs/prisma-app/qa/prisma-app-mobile-24-pulse-timeline-regression-corpus.jsonl"
];
for (const rel of required) exists(rel);

const lib = read("src/lib/prisma-app/prisma-mobile-pulse-timeline.ts");
const component = read("src/components/prisma-app/PrismaMobilePulseTimeline.tsx");
const dashboard = read("src/components/prisma-app/PrismaMobileDashboard.tsx");
const css = read("src/components/prisma-app/prisma-mobile-dashboard.module.css");
const route = read("app/api/mobile/pulse-timeline/route.ts");
const pkg = JSON.parse(read("package.json"));
const scenarios = JSON.parse(read("docs/prisma-app/qa/prisma-app-mobile-24-pulse-timeline-scenarios.json"));
const corpusLines = read("docs/prisma-app/qa/prisma-app-mobile-24-pulse-timeline-regression-corpus.jsonl").trim().split(/\r?\n/).filter(Boolean);

assert(lib.includes("PRISMA_APP_MOBILE_24_PULSE_TIMELINE"), "contract id missing");
assert(lib.includes("buildPrismaMobilePulseTimeline"), "builder missing");
assert(lib.includes("buildPrismaMobileDecisionLedger"), "decision ledger handoff missing");
assert(lib.includes("buildPrismaMobileActionInbox"), "action inbox handoff missing");
assert(lib.includes("buildPrismaMobileCommandCenter"), "command center handoff missing");
assert(component.includes("timeline.nowCheckpoint.checklist"), "checkpoint checklist missing");
assert(component.includes("timeline.events.map"), "events renderer missing");
assert(dashboard.includes("PrismaMobilePulseTimeline"), "dashboard does not mount pulse timeline");
assert(css.includes("PRISMA_APP_MOBILE_24_PULSE_TIMELINE START"), "css marker missing");
assert(route.includes("endpoint: \"pulse_timeline\""), "route endpoint missing");
assert(pkg.version === "0.24.0", "package version must be 0.24.0");
assert(pkg.scripts["verify:pulse-timeline"] === "node tools/verify_prisma_app_mobile_24_pulse_timeline.mjs", "verify script missing");
assert(Array.isArray(scenarios.scenarios) && scenarios.scenarios.length >= 384, "scenarios below 384");
assert(corpusLines.length >= 3200, "corpus below 3200 lines");
for (const line of corpusLines.slice(0, 5)) JSON.parse(line);

const forbidden = ["demo", "mock", "lorem", "placeholder", "TODO: fake"];
for (const word of forbidden) {
  assert(!component.toLowerCase().includes(word), `forbidden copy in component: ${word}`);
}

console.log("OK PRISMA_APP_MOBILE_24_PULSE_TIMELINE verified");
