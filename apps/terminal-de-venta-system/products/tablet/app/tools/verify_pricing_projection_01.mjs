// PRISMA_PRICING_OWNER_V1
import fs from "node:fs";
import path from "node:path";

function findAppRoot(start) {
  let cursor = path.resolve(start);
  for (let depth = 0; depth < 10; depth += 1) {
    const hasSchema = fs.existsSync(path.join(cursor, "prisma", "schema.prisma"));
    const hasProducts = fs.existsSync(path.join(cursor, "products"));
    const hasShared = fs.existsSync(path.join(cursor, "shared"));
    if (hasSchema && hasProducts && hasShared) return cursor;
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  throw new Error(`PRISMA_APP_ROOT_NOT_FOUND:${start}`);
}

const app = findAppRoot(process.cwd());
const failures = [];
const read = (rel) => {
  const file = path.join(app, rel);
  if (!fs.existsSync(file)) {
    failures.push(`missing:${rel}`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
};

const schema = read("products/tablet/app/prisma/schema.prisma");
if (!schema.includes("model PricingProjectionRecord {")) failures.push("tablet_projection_model_missing");

const pull = read("products/tablet/app/src/server/sync/catalog-pull.ts");
for (const token of ["PromotionRule", "DiscountPolicy", "PricingAuthorizationRule", "upsertPricingProjectionRecord"]) {
  if (!pull.includes(token)) failures.push(`tablet_pull_missing:${token}`);
}
if (!pull.includes("safeToContinueSelling: true")) failures.push("tablet_local_first_guard_missing");

const contract = JSON.parse(read("shared/contracts/pc-tablet-catalog-delta.v1.json") || "{}");
for (const entity of ["PromotionRule", "DiscountPolicy", "PricingAuthorizationRule"]) {
  if (!contract.entities?.includes(entity)) failures.push(`contract_entity_missing:${entity}`);
}

const result = {
  verifier: "verify_pricing_projection_01",
  status: failures.length ? "FAIL" : "PASS",
  localFirst: true,
  failures
};
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exit(1);
