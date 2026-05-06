#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const exists = (p) => fs.existsSync(path.join(root, p));
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");

const fail = (message, details = {}) => {
  console.error(JSON.stringify({
    ok: false,
    verifier: "PRISMA_APP_MOBILE_33_MANDO_CONTRACTS",
    message,
    details
  }, null, 2));
  process.exit(1);
};

const requireFile = (file) => {
  if (!exists(file)) fail(`Missing file: ${file}`);
  return read(file);
};

const requireAny = (file, snippets, label) => {
  const text = requireFile(file);
  if (!snippets.some((snippet) => text.includes(snippet))) {
    fail(`${file} missing ${label}`, { expectedAny: snippets });
  }
  return text;
};

const pkg = JSON.parse(requireFile("package.json"));

if (!pkg.scripts || pkg.scripts["verify:mando"] !== "node tools/verify_prisma_app_mobile_33_mando_contracts.mjs") {
  fail("package.json must expose verify:mando.");
}

if (!String(pkg.scripts["check:all"] || "").includes("verify:mando")) {
  fail("check:all must include verify:mando.");
}

const dashboard = requireFile("src/components/prisma-app/PrismaMobileDashboard.tsx");

if (!dashboard.includes("PrismaMobilePremiumNavigator")) {
  fail("Dashboard must keep Premium Navigator as the long-module owner.");
}

const navigatorCandidates = [
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "src/components/prisma-app/PrismaMobilePremiumNavigation.tsx",
  "src/components/prisma-app/prisma-mobile-premium-navigation.tsx",
  "src/components/prisma-app/prisma-mobile-premium-navigator.tsx"
];

const navigatorFiles = navigatorCandidates.filter((file) => exists(file));
if (!navigatorFiles.length) {
  fail("Premium navigator file not found.", { navigatorCandidates });
}

const navigatorText = navigatorFiles.map((file) => read(file)).join("\n");

const surfaces = [
  "PrismaMobileCommandCenter",
  "PrismaMobileActionInbox",
  "PrismaMobileDailyBrief",
  "PrismaMobileDecisionLedger",
  "PrismaMobilePulseTimeline",
  "PrismaMobileHealthRadar"
];

for (const surface of surfaces) {
  const componentFile = `src/components/prisma-app/${surface}.tsx`;
  if (!exists(componentFile)) {
    fail("Missing mando component file.", { surface, componentFile });
  }

  const ownedByDashboard = dashboard.includes(`<${surface}`);
  const ownedByNavigator = navigatorText.includes(`<${surface}`);

  if (ownedByDashboard) {
    fail("Mando surface must not be mounted directly in Dashboard.", {
      surface
    });
  }

  if (!ownedByNavigator) {
    fail("Mando surface must be owned by Premium Navigator.", {
      surface,
      navigatorFiles
    });
  }
}

requireAny("src/components/prisma-app/PrismaMobileCommandCenter.tsx",
  ["buildPrismaMobileCommandCenter", "CommandCenter", "command", "clientSnapshot"],
  "command center component contract"
);

requireAny("src/components/prisma-app/PrismaMobileActionInbox.tsx",
  ["buildPrismaMobileActionInbox", "recommendedAction", "priority", "action", "clientSnapshot"],
  "action inbox component contract"
);

requireAny("src/components/prisma-app/PrismaMobileDailyBrief.tsx",
  ["buildPrismaMobileDailyBrief", "DailyBrief", "brief", "readiness", "sections", "clientSnapshot"],
  "daily brief component contract"
);

requireAny("src/components/prisma-app/PrismaMobileDecisionLedger.tsx",
  ["buildPrismaMobileDecisionLedger", "DecisionLedger", "ledger", "entries", "clientSnapshot"],
  "decision ledger component contract"
);

requireAny("src/components/prisma-app/PrismaMobilePulseTimeline.tsx",
  ["buildPrismaMobilePulseTimeline", "PulseTimeline", "timeline", "events", "clientSnapshot"],
  "pulse timeline component contract"
);

requireAny("src/components/prisma-app/PrismaMobileHealthRadar.tsx",
  ["buildPrismaMobileHealthRadar", "HealthRadar", "radar", "axes", "watchlist", "clientSnapshot"],
  "health radar component contract"
);

requireAny("src/lib/prisma-app/prisma-mobile-command-center.ts",
  ["readinessScore", "decisionQueue", "dataQuality", "command", "summary"],
  "command center lib contract"
);

requireAny("src/lib/prisma-app/prisma-mobile-action-inbox.ts",
  ["priorityScore", "recommendedAction", "evidence", "lanes", "priority", "action"],
  "action inbox lib contract"
);

requireAny("src/lib/prisma-app/prisma-mobile-daily-brief.ts",
  ["readinessLabel", "sections", "ownerMessage", "headline", "summary", "brief", "riesgo", "resumen"],
  "daily brief lib contract"
);

requireAny("src/lib/prisma-app/prisma-mobile-decision-ledger.ts",
  ["entries", "evidence", "nextStep", "ledger", "decision"],
  "decision ledger lib contract"
);

requireAny("src/lib/prisma-app/prisma-mobile-pulse-timeline.ts",
  ["events", "nextCheck", "evidence", "timeline", "occurredAt"],
  "pulse timeline lib contract"
);

requireAny("src/lib/prisma-app/prisma-mobile-health-radar.ts",
  ["axes", "watchlist", "nextReview", "radar", "risk", "status"],
  "health radar lib contract"
);

requireFile("src/lib/prisma-app/prisma-mobile-view-model.ts");

const scenariosPath = "docs/prisma-app/qa/prisma-app-mobile-33-mando-runtime-scenarios.json";
if (!exists(scenariosPath)) {
  fail(`Missing ${scenariosPath}`);
}

const scenarios = JSON.parse(read(scenariosPath));
if (!Array.isArray(scenarios.states) || scenarios.states.length < 6) {
  fail("Scenario matrix must contain mando runtime states.", {
    count: scenarios.states?.length ?? 0
  });
}

for (const file of [
  "src/components/prisma-app/PrismaMobileCommandCenter.tsx",
  "src/components/prisma-app/PrismaMobileActionInbox.tsx",
  "src/components/prisma-app/PrismaMobileDailyBrief.tsx",
  "src/components/prisma-app/PrismaMobileDecisionLedger.tsx",
  "src/components/prisma-app/PrismaMobilePulseTimeline.tsx",
  "src/components/prisma-app/PrismaMobileHealthRadar.tsx"
]) {
  const text = read(file);
  if (text.includes("Math.random()")) fail("Unstable Math.random() found.", { file });
  if (text.includes("Date.now()")) fail("Unstable Date.now() found.", { file });
  if (/key=\{\s*index\s*\}/.test(text)) fail("Unstable key={index} found.", { file });
}

console.log(JSON.stringify({
  ok: true,
  verifier: "PRISMA_APP_MOBILE_33_MANDO_CONTRACTS",
  ownership: "premium-navigator-owned",
  navigatorSurfaces: surfaces.length,
  navigatorFiles,
  scenarioCount: scenarios.states.length
}, null, 2));
