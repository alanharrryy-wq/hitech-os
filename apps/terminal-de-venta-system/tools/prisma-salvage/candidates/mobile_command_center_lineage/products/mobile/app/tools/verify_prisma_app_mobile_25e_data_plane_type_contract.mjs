import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const read = (relativePath) => readFileSync(join(root, relativePath), "utf8");
const fail = (message) => {
  console.error(`FAIL ${message}`);
  process.exitCode = 1;
};
const pass = (message) => console.log(`OK ${message}`);

const payloadBuilders = read("src/lib/prisma-app/mobile-data-plane/payload-builders.ts");
const alertsPolicy = read("src/lib/prisma-app/mobile-data-plane/alerts-policy.ts");
const corpus = read("docs/prisma-app/qa/prisma-app-mobile-25e-type-contract-regression-corpus.jsonl").trim().split(/\r?\n/).filter(Boolean);

const requiredPayloadBuilderPatterns = [
  ["snapshot return type", /export function buildSnapshotPayload\(state: MobileDataPlaneState\): PrismaMobileSnapshotPayload/],
  ["summary return type", /export function buildSummaryPayload\(state: MobileDataPlaneState\): PrismaMobileSummaryPayload/],
  ["health literal union", /const health: PrismaMobileSummaryPayload\["health"\]/],
  ["alerts payload type", /export function buildAlertsPayload\(state: MobileDataPlaneState\): PrismaMobileAlertsPayload/],
  ["branches payload type", /export function buildBranchesPayload\(state: MobileDataPlaneState\): PrismaMobileBranchesPayload/],
  ["snapshot contract import", /import type \{ PrismaMobileSnapshotPayload \} from "\.\.\/prisma-mobile-snapshot-contract";/]
];

const requiredAlertPatterns = [
  ["state pick uses salesToday", /Pick<MobileDataPlaneState, "salesToday" \| "inventory" \| "outbox" \| "pc" \| "config" \| "warnings">/],
  ["ticket check uses salesToday", /input\.salesToday\.tickets === 0/]
];

for (const [name, pattern] of requiredPayloadBuilderPatterns) {
  if (!pattern.test(payloadBuilders)) fail(`payload-builders missing ${name}`);
}
for (const [name, pattern] of requiredAlertPatterns) {
  if (!pattern.test(alertsPolicy)) fail(`alerts-policy missing ${name}`);
}
if (/\binput\.sales\b/.test(alertsPolicy)) fail("alerts-policy still references input.sales");
if (/health: string/.test(payloadBuilders)) fail("payload-builders still allows health:string widening");

if (corpus.length < 2500) fail(`corpus too small: ${corpus.length}`);
const legalHealth = new Set(["sano", "revisar", "urgente", "offline"]);
let parsed = 0;
for (const line of corpus) {
  const item = JSON.parse(line);
  if (!legalHealth.has(item.expectedHealth)) fail(`invalid expectedHealth ${item.expectedHealth}`);
  if (!item.state || !Object.prototype.hasOwnProperty.call(item.state, "salesToday")) fail("state vector missing salesToday");
  if (Object.prototype.hasOwnProperty.call(item.state, "sales")) fail("state vector uses legacy sales key");
  parsed += 1;
}
if (process.exitCode) process.exit(process.exitCode);
pass(`PRISMA_APP_MOBILE_25E_DATA_PLANE_TYPE_CONTRACT verified ${parsed} type vectors`);
