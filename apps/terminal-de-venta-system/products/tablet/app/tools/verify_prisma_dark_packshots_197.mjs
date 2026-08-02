import fs from "node:fs";
import path from "node:path";

const repo = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const appRoot = path.join(repo, "apps", "terminal-de-venta-system");
const mediaRoot = path.join(repo, "tools", "_local", "data", "terminal-de-venta-system", "product-media");
const manifestPath = path.join(mediaRoot, "manifest", "PACKSHOT_CATALOG.json");

const checks = [];
function check(name, condition, detail = "") {
  checks.push({ name, pass: Boolean(condition), detail });
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
check("manifest dark only", manifest.mode === "dark_only", manifest.mode);
check("197 manifest entries", manifest.items?.length === 197, String(manifest.items?.length));
check("186 selectable unique visuals", manifest.items?.filter((item) => item.selectable !== false).length === 186);
check("11 duplicate aliases", manifest.items?.filter((item) => item.duplicateOfAssetId).length === 11);

for (const item of manifest.items ?? []) {
  check(`runtime ${item.canonicalName}`, fs.existsSync(path.join(mediaRoot, "catalog", item.canonicalName)));
  check(`thumbnail ${item.canonicalName}`, fs.existsSync(path.join(mediaRoot, "thumbnails", item.canonicalName)));
}

const requiredFiles = [
  "products/pc/app/src/server/product-media/managed-library.ts",
  "products/pc/app/app/product-media/[...segments]/route.ts",
  "products/pc/app/components/catalog/product-media-workspace.tsx",
  "products/pc/app/components/catalog/product-media-workspace.module.css",
  "products/tablet/app/src/server/product-media/managed-library.ts",
  "products/tablet/app/app/product-media/[...segments]/route.ts"
];
for (const relative of requiredFiles) check(`file ${relative}`, fs.existsSync(path.join(appRoot, relative)));
check("file tools/prisma_packshots/build_prisma_dark_packshots.py", fs.existsSync(path.join(repo, "tools", "prisma_packshots", "build_prisma_dark_packshots.py")));

const validators = fs.readFileSync(path.join(appRoot, "products/tablet/app/src/server/pos-api/validators.ts"), "utf8");
check("tablet catalog ceiling 5000", validators.includes('searchParams.get("limit"), 5000, 5000'));

const repository = fs.readFileSync(path.join(appRoot, "products/pc/app/src/server/repositories/product-media.repository.ts"), "utf8");
check("pc media workspace ceiling 5000", repository.includes("LIMIT 5000"));

const resolver = fs.readFileSync(path.join(appRoot, "products/tablet/app/components/pos/pos-packshots.ts"), "utf8");
check("tablet managed dark route", resolver.includes("/product-media/catalog"));
check("tablet resolver has no light public path", !resolver.includes("/products/packshots/light"));

const failed = checks.filter((item) => !item.pass);
console.log(JSON.stringify({ status: failed.length ? "FAIL" : "PASS", checks: checks.length, failed }, null, 2));
process.exit(failed.length ? 1 : 0);
