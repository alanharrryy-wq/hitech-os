import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(here, "..");
const catalogPath = path.join(appRoot, "shared", "licensing", "plan-catalog.canonical.json");

function fail(message) {
  console.error(`FAIL_LICENSE_COMMERCIAL_PRICING: ${message}`);
  process.exit(1);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

const catalog = JSON.parse(fs.readFileSync(catalogPath, "utf8"));
const policy = catalog.commercialPolicy ?? {};
const plans = Array.isArray(catalog.plans) ? catalog.plans : [];

assert(catalog.schemaVersion === "1.1.0", "schemaVersion must be 1.1.0");
assert(policy.status === "CANONICAL_LIST_PRICE_V1", "commercial policy status mismatch");
assert(policy.effectiveFrom === "2026-08-14", "effective date mismatch");
assert(policy.market === "MX", "market must be MX");
assert(policy.currency === "MXN", "currency must be MXN");
assert(policy.taxTreatment === "PLUS_APPLICABLE_IVA", "tax treatment must remain IVA-exclusive");
assert(policy.billingScope === "PER_LICENSE_ASSIGNMENT_WITH_PLAN_LIMITS", "billing scope mismatch");
assert(policy?.grandfathering?.existingSignedContracts === "PRESERVE_CONTRACTED_PRICE_UNTIL_RENEWAL", "grandfathering policy missing");
assert(policy?.grandfathering?.firstCustomerPriceMustNotBeInferred === true, "first customer historical price must not be inferred");
assert(policy?.mobile?.standaloneSku === false, "Mobile must not become a standalone SKU without a canonical entitlement");
assert(policy?.positioning?.visualExperience === "PREMIUM_GOVERNED_MULTI_SURFACE", "visual positioning contract missing");
assert(policy?.positioning?.visualExperienceAffectsEntitlements === false, "visual positioning must not mutate entitlements");

const expected = {
  TABLET_SOLO: { monthly: 399, quarterly: 1149, semiannual: 2199, annual: 3999 },
  TABLET_PRO: { monthly: 599, quarterly: 1699, semiannual: 3299, annual: 5999 },
  TABLET_PC_MANAGED: { monthly: 999, quarterly: 2849, semiannual: 5499, annual: 9999 }
};

const vendible = plans.filter((plan) => plan?.vendible === true && plan?.internal !== true);
assert(vendible.length === 3, `expected exactly 3 vendible plans, got ${vendible.length}`);

for (const [planCode, prices] of Object.entries(expected)) {
  const plan = plans.find((item) => item?.plan === planCode);
  assert(plan, `missing canonical plan ${planCode}`);
  assert(plan.vendible === true, `${planCode} must remain vendible`);
  assert(plan.internal === false, `${planCode} must remain external/customer-facing`);
  assert(plan?.commercial?.priceVersion === "2026-08-14.v1", `${planCode} price version mismatch`);
  for (const [period, amount] of Object.entries(prices)) {
    assert(plan?.commercial?.listPriceMxn?.[period] === amount, `${planCode}.${period} expected ${amount}`);
  }
  assert(Array.isArray(plan.features) && plan.features.length > 0, `${planCode} features missing`);
  assert(plan.limits && Number.isInteger(plan.limits.maxDevices), `${planCode} limits missing`);
}

const dev = plans.find((item) => item?.plan === "DEVELOPMENT");
assert(dev, "DEVELOPMENT plan missing");
assert(dev.vendible === false && dev.internal === true, "DEVELOPMENT must remain internal and non-vendible");
assert(dev.commercial === undefined, "DEVELOPMENT must not receive commercial pricing");

const forbiddenStandaloneMobile = plans.some((plan) => /MOBILE/.test(String(plan?.plan ?? "")) && plan?.vendible === true);
assert(!forbiddenStandaloneMobile, "standalone Mobile SKU detected without explicit canonical entitlement approval");

for (const plan of vendible) {
  const monthly = plan.commercial.listPriceMxn.monthly;
  const quarterly = plan.commercial.listPriceMxn.quarterly;
  const semiannual = plan.commercial.listPriceMxn.semiannual;
  const annual = plan.commercial.listPriceMxn.annual;
  assert(quarterly < monthly * 3, `${plan.plan} quarterly price must encode a term discount`);
  assert(semiannual < monthly * 6, `${plan.plan} semiannual price must encode a term discount`);
  assert(annual < monthly * 12, `${plan.plan} annual price must encode a term discount`);
}

console.log("PASS_LICENSE_COMMERCIAL_PRICING");
console.log(`catalog=${path.relative(appRoot, catalogPath).replaceAll(path.sep, "/")}`);
console.log(`vendiblePlans=${vendible.map((plan) => plan.plan).join(",")}`);
console.log(`priceVersion=2026-08-14.v1 currency=${policy.currency} tax=${policy.taxTreatment}`);
