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

const repo = findAppRoot(process.cwd());
const required = [
  "prisma/schema.prisma",
  "products/pc/app/src/server/repositories/pricing-policy.repository.ts",
  "products/pc/app/src/server/services/pricing-policy.service.ts",
  "products/pc/app/components/pricing/pricing-policy-workspace.tsx",
  "products/pc/app/app/api/backoffice/pricing/workspace/route.ts",
  "products/pc/app/app/api/backoffice/pricing/[entity]/route.ts",
  "products/pc/app/app/api/backoffice/pricing/[entity]/[entityId]/route.ts",
  "shared/licensing/feature-keys.ts",
  "shared/contracts/pc-tablet-catalog-delta.v1.json",
  "shared/twin-kernel/src/sync/catalog-delta.ts"
];

const failures = [];
const read = (rel) => {
  const file = path.join(repo, rel);
  if (!fs.existsSync(file)) {
    failures.push(`missing:${rel}`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
};

for (const rel of required) {
  const content = read(rel);
  if (content && !content.includes("PRISMA_PRICING_OWNER_V1") && !rel.endsWith(".json") && !rel.includes("catalog-delta.ts")) {
    failures.push(`marker_missing:${rel}`);
  }
}

const migration = read("prisma/migrations/20260720_pricing_policy_owner/migration.sql");
if (!migration.includes('CREATE UNIQUE INDEX "PricingAuthorizationRule_id_businessId_key" ON "PricingAuthorizationRule"("id", "businessId");')) {
  failures.push("migration_composite_parent_key_missing:PricingAuthorizationRule(id,businessId)");
}

const schema = read("prisma/schema.prisma");
for (const model of ["PromotionRule", "DiscountPolicy", "PricingAuthorizationRule", "PricingAuthorizationRequest"]) {
  if (!schema.includes(`model ${model} {`)) failures.push(`schema_model_missing:${model}`);
}
for (const field of ["idempotencyKey", "version"]) {
  if (!schema.includes(field)) failures.push(`schema_field_missing:${field}`);
}

const repoSource = read("products/pc/app/src/server/repositories/pricing-policy.repository.ts");
for (const token of ["auditEvent.create", "outboxEvent.create", "PRICING_VERSION_CONFLICT", "readOne", "idempotencyKey"]) {
  if (!repoSource.includes(token)) failures.push(`repository_contract_missing:${token}`);
}

const features = read("shared/licensing/feature-keys.ts");
for (const key of ["pricing.read", "pricing.price-lists.write", "pricing.taxes.write", "pricing.promotions.write", "pricing.discounts.write", "pricing.authorization.request", "pricing.authorization.decide", "pricing.audit.read"]) {
  if (!features.includes(`"${key}"`)) failures.push(`feature_missing:${key}`);
}

const mobileChanges = process.env.PRISMA_PRICEIMPL_CHANGED_FILES?.split("|").filter(Boolean).filter((item) => item.includes("/products/mobile/"));
if (mobileChanges?.length) failures.push(`mobile_scope_violation:${mobileChanges.join(",")}`);

const result = {
  verifier: "verify_pricing_policy_owner_01",
  status: failures.length ? "FAIL" : "PASS",
  failures
};
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exit(1);
