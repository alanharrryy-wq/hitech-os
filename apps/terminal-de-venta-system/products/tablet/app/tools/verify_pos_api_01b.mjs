import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const checks = [
  ["app/api/pos/products/search/route.ts", "searchProducts"],
  ["app/api/pos/products/search/route.ts", "GET /api/pos/products/search"],
  ["app/api/pos/products/resolve/route.ts", "resolveProduct"],
  ["app/api/pos/products/resolve/route.ts", "GET /api/pos/products/resolve"],
  ["app/api/pos/sales/complete/route.ts", "posEngineRepository.completeLocalSale"],
  ["app/api/pos/sales/complete/route.ts", "POST /api/pos/sales/complete"],
  ["app/api/pos/sales/today/route.ts", "getTodaySalesSummary"],
  ["app/api/pos/sales/today/route.ts", "GET /api/pos/sales/today"],
  ["src/server/pos-api/responses.ts", "ok: true"],
  ["src/server/pos-api/responses.ts", "ok: false"],
  ["src/server/pos-api/validators.ts", "readCompleteSaleInput"],
  ["src/server/pos-api/validators.ts", "DEFAULT_POS_API_BUSINESS_ID"],
  ["src/server/pos-api/product-queries.prisma.ts", "searchProducts"],
  ["src/server/pos-api/product-queries.prisma.ts", "resolveProduct"],
  ["src/server/pos-api/sales-summary.prisma.ts", "topProducts"],
  ["src/server/pos-api/errors.ts", "INSUFFICIENT_STOCK"],
  ["docs/pos/STANDALONE_CORE_01B_API.md", "Acceptance criteria"],
  ["docs/qa/pos-01b/acceptance.md", "POS-01B-AC-001"]
];

let failed = false;
for (const [rel, marker] of checks) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) {
    console.error(`[pos-01b] missing ${rel}`);
    failed = true;
    continue;
  }
  const text = fs.readFileSync(file, "utf8");
  if (!text.includes(marker)) {
    console.error(`[pos-01b] missing marker ${rel}: ${marker}`);
    failed = true;
  } else {
    console.log(`[pos-01b] ok ${rel}: ${marker}`);
  }
}

if (failed) {
  console.error("[pos-01b] Verify failed.");
  process.exit(1);
}
console.log("[pos-01b] Verify OK.");
