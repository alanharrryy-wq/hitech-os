#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "app/api/mobile/action-inbox/route.ts",
  "src/lib/prisma-app/prisma-mobile-action-inbox.ts",
  "src/components/prisma-app/PrismaMobileActionInbox.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/index.ts",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "docs/prisma-app/PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX.md",
  "docs/prisma-app/qa/prisma-app-mobile-21-owner-action-inbox-scenarios.json",
  "docs/prisma-app/qa/prisma-app-mobile-21-owner-action-inbox-regression-corpus.jsonl"
];

function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) throw new Error(`Falta archivo ${rel}`);
  return fs.readFileSync(file, "utf8");
}

function assertIncludes(rel, needle) {
  const text = read(rel);
  if (!text.includes(needle)) throw new Error(`${rel} no incluye ${needle}`);
}

for (const rel of required) read(rel);
assertIncludes("src/lib/prisma-app/prisma-mobile-action-inbox.ts", "PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX");
assertIncludes("src/lib/prisma-app/prisma-mobile-action-inbox.ts", "buildPrismaMobileActionInbox");
assertIncludes("src/lib/prisma-app/prisma-mobile-action-inbox.ts", "ownerMessage");
assertIncludes("src/components/prisma-app/PrismaMobileActionInbox.tsx", "Bandeja del dueño");
assertIncludes("src/components/prisma-app/PrismaMobileActionInbox.tsx", "Acciones operativas priorizadas");
assertIncludes("src/components/prisma-app/PrismaMobileDashboard.tsx", "<PrismaMobileActionInbox clientSnapshot={clientSnapshot} />");
assertIncludes("app/api/mobile/action-inbox/route.ts", "action_inbox");
assertIncludes("src/components/prisma-app/prisma-mobile-dashboard.module.css", "PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX START");
assertIncludes("package.json", "verify:action-inbox");

const forbidden = ["demo", "fixture sintético", "lorem", "todo", "mock"];
const uiTexts = [
  "src/components/prisma-app/PrismaMobileActionInbox.tsx",
  "src/lib/prisma-app/prisma-mobile-action-inbox.ts",
  "app/api/mobile/action-inbox/route.ts"
];
for (const rel of uiTexts) {
  const text = read(rel).toLowerCase();
  for (const word of forbidden) {
    if (text.includes(word)) throw new Error(`${rel} conserva texto prohibido: ${word}`);
  }
}

const scenarios = JSON.parse(read("docs/prisma-app/qa/prisma-app-mobile-21-owner-action-inbox-scenarios.json"));
if (!Array.isArray(scenarios.scenarios) || scenarios.scenarios.length < 300) throw new Error("QA scenarios insuficientes para v21");
const corpusLines = read("docs/prisma-app/qa/prisma-app-mobile-21-owner-action-inbox-regression-corpus.jsonl").trim().split(/\r?\n/);
if (corpusLines.length < 2400) throw new Error("Corpus regression insuficiente para v21");
for (const line of corpusLines.slice(0, 25)) JSON.parse(line);
console.log("OK PRISMA_APP_MOBILE_21_OWNER_ACTION_INBOX verified");
