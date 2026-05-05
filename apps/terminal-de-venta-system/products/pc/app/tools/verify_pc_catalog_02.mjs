#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const args = process.argv.slice(2);
const rootArgIndex = args.indexOf("--root");
const root = path.resolve(rootArgIndex >= 0 && args[rootArgIndex + 1] ? args[rootArgIndex + 1] : process.cwd());

const requiredFiles = [
  "app/catalog/page.tsx",
  "app/catalog/loading.tsx",
  "app/catalog/error.tsx",
  "components/catalog/catalog-dashboard.tsx",
  "src/modules/catalog/types.ts",
  "src/server/repositories/catalog.repository.ts",
  "src/server/services/catalog.service.ts",
  "src/server/validators/catalog-quality.ts",
  "docs/modules/catalog.md"
];

function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}

const files = requiredFiles.map((rel) => {
  const abs = path.join(root, rel);
  const exists = fs.existsSync(abs);
  const size = exists ? fs.statSync(abs).size : 0;
  return { rel, exists, size };
});

const missing = files.filter((file) => !file.exists).map((file) => file.rel);
const empty = files.filter((file) => file.exists && file.size <= 0).map((file) => file.rel);
const findings = [];

if (missing.length) findings.push({ severity: "BLOCKER", code: "MISSING_FILES", message: `Faltan archivos: ${missing.join(", ")}` });
if (empty.length) findings.push({ severity: "BLOCKER", code: "EMPTY_FILES", message: `Archivos vacíos: ${empty.join(", ")}` });

if (!missing.includes("app/catalog/page.tsx")) {
  const page = read("app/catalog/page.tsx");
  if (page.includes("ModuleOverviewPage")) findings.push({ severity: "BLOCKER", code: "CATALOG_STILL_OVERVIEW", message: "La ruta /catalog sigue usando ModuleOverviewPage." });
  if (!page.includes("getCatalogWorkspace")) findings.push({ severity: "BLOCKER", code: "CATALOG_NO_SERVICE", message: "La ruta /catalog no consume servicio de catálogo." });
}

if (!missing.includes("src/server/repositories/catalog.repository.ts")) {
  const repo = read("src/server/repositories/catalog.repository.ts");
  for (const token of ["prisma", "product.findMany", "barcodes", "stockSnapshots"]) {
    if (!repo.includes(token)) findings.push({ severity: "BLOCKER", code: "REPOSITORY_MISSING_TOKEN", message: `Repositorio no contiene ${token}.` });
  }
}

if (!missing.includes("src/server/services/catalog.service.ts")) {
  const service = read("src/server/services/catalog.service.ts");
  for (const token of ["CatalogRepository", "buildCatalogIssues", "missingBarcodeCount", "duplicateBarcodeCount", "fallback_empty"]) {
    if (!service.includes(token)) findings.push({ severity: "BLOCKER", code: "SERVICE_MISSING_TOKEN", message: `Servicio no contiene ${token}.` });
  }
}

if (!missing.includes("src/server/validators/catalog-quality.ts")) {
  const validator = read("src/server/validators/catalog-quality.ts");
  for (const token of ["hasMissingBarcode", "findDuplicateBarcodes", "isPriceStale", "buildCatalogIssues"]) {
    if (!validator.includes(token)) findings.push({ severity: "BLOCKER", code: "VALIDATOR_MISSING_TOKEN", message: `Validador no contiene ${token}.` });
  }
}

if (!missing.includes("components/catalog/catalog-dashboard.tsx")) {
  const component = read("components/catalog/catalog-dashboard.tsx");
  for (const label of ["Búsqueda operativa", "Incidencias de catálogo", "Ficha del SKU", "Sin barcode", "Duplicados"]) {
    if (!component.includes(label)) findings.push({ severity: "BLOCKER", code: "UI_LABEL_MISSING", message: `UI no contiene ${label}.` });
  }
}

const ok = findings.every((finding) => finding.severity !== "BLOCKER");
const result = {
  verifier: "verify_pc_catalog_02",
  iteration: "pc_i02_catalogo",
  state: ok ? "PASS" : "FAIL",
  ok,
  root,
  route: "/catalog",
  files,
  missing,
  empty,
  findings,
  checkedAt: new Date().toISOString()
};

console.log(JSON.stringify(result, null, 2));
process.exit(ok ? 0 : 1);
