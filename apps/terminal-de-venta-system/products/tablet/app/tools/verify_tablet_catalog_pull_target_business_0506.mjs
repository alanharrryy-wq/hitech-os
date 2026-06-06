import { readFileSync } from "node:fs";

const file = "src/server/sync/catalog-pull.ts";
const text = readFileSync(file, "utf8");
const failures = [];

function blockForFunction(source, name) {
  const needle = `async function ${name}`;
  const start = source.indexOf(needle);
  if (start < 0) return "";
  const brace = source.indexOf("{", start);
  if (brace < 0) return "";
  let depth = 0;
  for (let i = brace; i < source.length; i += 1) {
    const ch = source[i];
    if (ch === "{") depth += 1;
    if (ch === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  return "";
}

const fetchBlock = blockForFunction(text, "fetchCatalogDelta");

if (!fetchBlock) {
  failures.push("missing fetchCatalogDelta block");
}

if (!fetchBlock.includes("const sourceBusinessId = asString(input.pcBusinessId) || undefined;")) {
  failures.push("fetchCatalogDelta must compute sourceBusinessId from input.pcBusinessId only");
}

if (!fetchBlock.includes("const targetBusinessId = asString(input.targetBusinessId) || DEFAULT_POS_API_BUSINESS_ID;")) {
  failures.push("fetchCatalogDelta must compute targetBusinessId locally for the tablet target payload");
}

if (!/businessId\s*:\s*sourceBusinessId\s*,/.test(fetchBlock)) {
  failures.push("PC export payload businessId must use sourceBusinessId");
}

if (/businessId\s*:\s*[^\n,]*targetBusinessId/.test(fetchBlock)) {
  failures.push("PC export payload businessId must not fall back to tablet targetBusinessId");
}

if (!/targetBusinessId\s*,/.test(fetchBlock)) {
  failures.push("PC export payload must still send targetBusinessId separately");
}

if (!text.includes("const targetBusinessId = asString(input.targetBusinessId) || DEFAULT_POS_API_BUSINESS_ID;")) {
  failures.push("targetBusinessId default must remain available for checkpoint/application paths");
}

if (failures.length) {
  console.error("PRISMA_TABLET_CATALOG_PULL_TARGET_BUSINESS_0506 failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}

console.log("PASS: tablet catalog pull source/target business guard");
