import fs from "node:fs";
import path from "node:path";

const repo = process.cwd();
const pass = [];
const fail = [];
function ok(name, condition, detail = "") {
  if (condition) pass.push({ name, detail });
  else fail.push({ name, detail });
}
function read(rel) {
  return fs.readFileSync(path.join(repo, rel), "utf8");
}
function exists(rel) {
  return fs.existsSync(path.join(repo, rel));
}

const posCssRel = "products/tablet/app/app/pos/prisma-pos-light-safe-shell.module.css";
const checkoutCssRel = "products/tablet/app/app/checkout/prisma-checkout-light-safe-shell.module.css";
const posLayoutRel = "products/tablet/app/app/pos/layout.tsx";
const checkoutLayoutRel = "products/tablet/app/app/checkout/layout.tsx";
const tabletCssRel = "products/tablet/app/app/prisma-tablet-light-shell.module.css";
const pageRel = "products/tablet/app/app/page.tsx";

const posCss = read(posCssRel);
const checkoutCss = read(checkoutCssRel);
const tabletCss = read(tabletCssRel);
const posLayout = read(posLayoutRel);
const checkoutLayout = read(checkoutLayoutRel);
const page = read(pageRel);

ok("root tablet page declares Fuji Cloudglass", page.includes('data-prisma-background="tablet-fuji-cloudglass"'));
ok("tablet shell css points to Fuji asset", tabletCss.includes("tablet-fuji-cloudglass.jpg"));
ok("POS layout declares Fuji background", posLayout.includes('data-prisma-background="tablet-fuji-cloudglass"'));
ok("checkout layout declares Fuji background", checkoutLayout.includes('data-prisma-background="tablet-fuji-cloudglass"'));
ok("POS css has visible Fuji marker", posCss.includes("PRISMA_TABLET_FUJI_SURFACE_FIX1_START"));
ok("checkout css has visible Fuji marker", checkoutCss.includes("PRISMA_TABLET_FUJI_SURFACE_FIX1_START"));
ok("POS css points to route-local Fuji asset", posCss.includes("/surface-visual-governor/pos-light-safe-shell/latest/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg"));
ok("checkout css points to route-local Fuji asset", checkoutCss.includes("/surface-visual-governor/checkout-light-safe-shell/latest/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg"));
ok("POS css overrides CSS-module card panels", posCss.includes('[class*="catalogArea"]') && posCss.includes('[class*="productCard"]') && posCss.includes('[class*="ticketPanel"]'));
ok("checkout css overrides CSS-module card panels", checkoutCss.includes('[class*="catalogArea"]') && checkoutCss.includes('[class*="productCard"]') && checkoutCss.includes('[class*="ticketPanel"]'));
ok("POS css uses glass blur", posCss.includes("backdrop-filter: blur(22px)") || posCss.includes("backdrop-filter: blur(20px)"));
ok("checkout css uses glass blur", checkoutCss.includes("backdrop-filter: blur(22px)") || checkoutCss.includes("backdrop-filter: blur(20px)"));

const assetRels = [
  "products/tablet/app/public/surface-visual-governor/tablet-light-shell/latest/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg",
  "products/tablet/app/public/surface-visual-governor/tablet-light-shell/pilot-05/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg",
  "products/tablet/app/public/surface-visual-governor/pos-light-safe-shell/latest/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg",
  "products/tablet/app/public/surface-visual-governor/pos-light-safe-shell/pilot-07/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg",
  "products/tablet/app/public/surface-visual-governor/checkout-light-safe-shell/latest/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg",
  "products/tablet/app/public/surface-visual-governor/checkout-light-safe-shell/pilot-08/atmosphere-assets/backgrounds/tablet-fuji-cloudglass.jpg"
];
for (const rel of assetRels) ok(`asset exists ${rel}`, exists(rel), rel);

ok("no WebGL/Pixi terms in POS route shell", !/webgl|pixi/i.test(posCss));
ok("no WebGL/Pixi terms in checkout route shell", !/webgl|pixi/i.test(checkoutCss));
ok("no database path leaks in touched route CSS", !/\.db\b|sqlite|DATABASE_URL/i.test(posCss + checkoutCss + tabletCss));

const result = {
  verifier: "tablet-fuji-visible-fix1",
  status: fail.length ? "FAIL" : "PASS",
  pass,
  fail,
  checked: pass.length + fail.length
};
console.log(JSON.stringify(result, null, 2));
if (fail.length) process.exit(1);
