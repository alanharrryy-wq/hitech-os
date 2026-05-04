import fs from "node:fs";
import path from "node:path";

const root = process.argv[2] || process.cwd();
const component = path.join(root, "src/components/prisma-app/PrismaMobileHealthRadar.tsx");
const css = path.join(root, "src/components/prisma-app/prisma-mobile-dashboard.module.css");

function fail(message) {
  console.error(`FAIL ${message}`);
  process.exit(1);
}

function ok(message) {
  console.log(`OK ${message}`);
}

if (!fs.existsSync(component)) fail(`missing ${component}`);
if (!fs.existsSync(css)) fail(`missing ${css}`);

const componentText = fs.readFileSync(component, "utf8");
const cssText = fs.readFileSync(css, "utf8");

if (!componentText.includes("makeStableHealthRadarKey")) fail("stable key helper missing");
ok("stable key helper");

if (!componentText.includes("section.key") || !componentText.includes("itemIndex")) fail("keys do not include section and index");
ok("section-index keys");

if (/key=\{\s*`?\$?\{?\s*item\.(status|value|label)/.test(componentText)) fail("unsafe item-only key remains");
ok("no item-only keys");

if (componentText.includes("tablet: OK")) fail("literal duplicate key smell remains");
ok("no tablet OK literal");

if (!cssText.includes("PRISMA_APP_MOBILE_HEALTH_RADAR_KEYS_HOTFIX_01")) fail("css marker missing");
ok("css marker");

if (!cssText.includes("healthRadarPanel") || !cssText.includes("healthRadarItem")) fail("health radar styles missing");
ok("health radar styles");

console.log("NODE READY prisma mobile health radar keys 01 6 checks");
