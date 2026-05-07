import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { basename, join, resolve } from "node:path";

const root = process.cwd();
const trashRoot = "F:\\Trash-old";

const docs = [
  "docs/PRISMA_MOBILE_FUTURE_EDIT_MAP.md",
  "docs/prisma-mobile-future-edit-map.json"
];

const scanFiles = [
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "src/components/prisma-app/PrismaMobileCommandCenter.tsx",
  "src/components/prisma-app/PrismaMobileMetricCard.tsx",
  "src/components/prisma-app/PrismaMobilePanels.tsx",
  "src/components/prisma-app/PrismaMobileActionInbox.tsx",
  "src/components/prisma-app/PrismaMobileDailyBrief.tsx",
  "src/components/prisma-app/PrismaMobileDecisionLedger.tsx",
  "src/components/prisma-app/PrismaMobilePulseTimeline.tsx",
  "src/components/prisma-app/PrismaMobileHealthRadar.tsx",
  "src/components/prisma-app/PrismaMobilePwaInstallCard.tsx",
  "src/components/prisma-app/PrismaMobilePwaInstallPage.tsx"
];

const expectedZones = [
  "mobile-app-shell",
  "mobile-brand-header",
  "mobile-logo",
  "mobile-status-chip",
  "mobile-command-card",
  "mobile-primary-metric",
  "mobile-kpi-grid",
  "mobile-kpi-card",
  "mobile-action-inbox",
  "mobile-review-first",
  "mobile-daily-brief",
  "mobile-decision-ledger",
  "mobile-pulse-timeline",
  "mobile-health-radar",
  "mobile-pwa-install",
  "mobile-offline-state",
  "mobile-sync-state",
  "mobile-error-state",
  "mobile-empty-state",
  "mobile-loading-state",
  "mobile-success-state"
];

const cssSections = [
  {
    file: "app/prisma-mobile-pulse-binding.css",
    sections: [
      "PRISMA Crystal Command Mobile: app binding"
    ]
  },
  {
    file: "src/components/prisma-app/prisma-mobile-dashboard.module.css",
    sections: [
      "PRISMA Crystal Command Mobile: tokens",
      "PRISMA Crystal Command Mobile: shell",
      "PRISMA Crystal Command Mobile: brand header",
      "PRISMA Crystal Command Mobile: command card",
      "PRISMA Crystal Command Mobile: KPI grid",
      "PRISMA Crystal Command Mobile: review-first panel",
      "PRISMA Crystal Command Mobile: PWA install",
      "PRISMA Crystal Command Mobile: states",
      "PRISMA Crystal Command Mobile: responsive"
    ]
  },
  {
    file: "src/components/prisma-app/prisma-mobile-pwa.module.css",
    sections: [
      "PRISMA Crystal Command Mobile: PWA install",
      "PRISMA Crystal Command Mobile: states",
      "PRISMA Crystal Command Mobile: responsive"
    ]
  }
];

const obsoleteArtifacts = [
  "config/prisma-app/mobile-css-module-hotfix.json",
  "config/prisma-app/mobile-visual-profile.json",
  "docs/prisma-app/PRISMA_APP_MOBILE_CSS_MODULE_HOTFIX_20260506_v01.md",
  "docs/prisma-app/PRISMA_APP_MOBILE_VISUAL_WORKBENCH.md",
  "tools/verify_prisma_mobile_css_module_hotfix_20260506_v01.mjs",
  "tools/verify_prisma_mobile_soft_control_logo_20260506_v01.mjs",
  "tools/verify_prisma_mobile_visual_workbench_20260506_v01.mjs"
];

const failures = [];
const skipped = [];

function read(relPath) {
  return readFileSync(resolve(root, relPath), "utf8");
}

for (const doc of docs) {
  if (!existsSync(resolve(root, doc))) failures.push(`MISSING_DOC ${doc}`);
}

try {
  JSON.parse(read("docs/prisma-mobile-future-edit-map.json"));
} catch (error) {
  failures.push(`INVALID_JSON docs/prisma-mobile-future-edit-map.json: ${error.message}`);
}

const scanText = scanFiles
  .filter((file) => existsSync(resolve(root, file)))
  .map((file) => `${file}\n${read(file)}`)
  .join("\n\n");

for (const zone of expectedZones) {
  if (!scanText.includes(zone)) failures.push(`MISSING_ZONE ${zone}`);
}

for (const entry of cssSections) {
  const path = resolve(root, entry.file);
  if (!existsSync(path)) {
    failures.push(`MISSING_CSS ${entry.file}`);
    continue;
  }
  const text = read(entry.file);
  for (const section of entry.sections) {
    if (!text.includes(section)) failures.push(`MISSING_CSS_SECTION ${entry.file}: ${section}`);
  }
}

const layoutPath = resolve(root, "app/layout.tsx");
if (existsSync(layoutPath) && readFileSync(layoutPath, "utf8").includes("prisma-mobile-visual-workbench.css")) {
  failures.push("FORBIDDEN_IMPORT app/layout.tsx: prisma-mobile-visual-workbench.css");
}

for (const artifact of obsoleteArtifacts) {
  if (existsSync(resolve(root, artifact))) failures.push(`OBSOLETE_ARTIFACT_STILL_IN_APP ${artifact}`);
}

const uncertainWorkbench = resolve(root, "app/prisma-app/prisma-mobile-visual-workbench.css");
if (existsSync(uncertainWorkbench)) {
  skipped.push({
    file: "app/prisma-app/prisma-mobile-visual-workbench.css",
    reason: "left in place because cleanup rules forbid moving app/**; layout import must remain absent"
  });
}

let latestTrashManifest = null;
if (existsSync(trashRoot)) {
  const cleanupDirs = readdirSync(trashRoot)
    .filter((name) => name.startsWith("prisma_mobile_cleanup_"))
    .map((name) => join(trashRoot, name))
    .filter((path) => statSync(path).isDirectory())
    .sort();
  const latest = cleanupDirs.at(-1);
  if (latest) {
    const required = ["MANIFEST.md", "manifest.json", "checksums.sha256", "original_paths.csv"];
    const missing = required.filter((file) => !existsSync(join(latest, file)));
    if (missing.length) failures.push(`INCOMPLETE_TRASH_MANIFEST ${latest}: ${missing.join(", ")}`);
    latestTrashManifest = join(latest, "manifest.json");
  } else {
    failures.push(`MISSING_TRASH_CLEANUP_FOLDER ${trashRoot}\\prisma_mobile_cleanup_*`);
  }
} else {
  failures.push(`MISSING_TRASH_ROOT ${trashRoot}`);
}

if (latestTrashManifest) {
  try {
    JSON.parse(readFileSync(latestTrashManifest, "utf8"));
  } catch (error) {
    failures.push(`INVALID_TRASH_MANIFEST_JSON ${latestTrashManifest}: ${error.message}`);
  }
}

const result = {
  ok: failures.length === 0,
  checked_zones: expectedZones.length,
  checked_files: scanFiles.map((file) => basename(file)),
  trash_manifest: latestTrashManifest,
  skipped,
  failures
};

console.log(JSON.stringify(result, null, 2));

if (failures.length) process.exit(1);
