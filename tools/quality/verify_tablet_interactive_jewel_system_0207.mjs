import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const failures = [];
const bangImportant = "!" + "important";

function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) {
    failures.push(`${rel} missing`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
}

function check(condition, message) {
  if (!condition) failures.push(message);
}

function has(rel, token) {
  const content = read(rel);
  if (!content.includes(token)) failures.push(`${rel} missing token: ${token}`);
}

const tileTsx = "apps/terminal-de-venta-system/products/tablet/app/components/tablet-action-tiles/tablet-action-tiles.tsx";
const tileCss = "apps/terminal-de-venta-system/products/tablet/app/components/tablet-action-tiles/tablet-action-tiles.module.css";
const posSearch = "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-product-search.tsx";
const posCss = "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css";
const stock = "apps/terminal-de-venta-system/products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx";
const stockCss = "apps/terminal-de-venta-system/products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css";
const shellCss = "apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css";

const css = read(tileCss);
const component = read(tileTsx);

for (const token of [
  "--tab-tile-ink",
  "--tab-tile-line",
  "--tab-tile-rim",
  ".tile:hover",
  ".tile:focus-visible",
  ".tile:active",
  ".disabled",
  "@media (prefers-reduced-motion: reduce)"
]) {
  check(css.includes(token), `${tileCss} missing jewel interaction token: ${token}`);
}

for (const tone of ["primary", "inventory", "success", "warning", "dangerQuiet", "jewel", "sync", "license", "neutral"]) {
  check(css.includes(`.tone_${tone}`), `${tileCss} missing tone ${tone}`);
}

for (const roleColor of ["#145bd8", "#087a67", "#0c7a4f", "#9a5d0e", "#b42342", "#6d4bd8", "#0d73a8", "#4553c7"]) {
  check(css.includes(roleColor), `${tileCss} missing distinct role color ${roleColor}`);
}

check(!css.includes(bangImportant), `${tileCss} contains priority CSS token`);
check(!/letter-spacing:\s*-\d/.test(css), `${tileCss} uses negative letter spacing`);

for (const token of [
  "data-quick-create-tile",
  "data-tile-state",
  "data-action-kind",
  "data-action-owner",
  "<a",
  "<button",
  "role=\"note\""
]) {
  check(component.includes(token), `${tileTsx} missing component token: ${token}`);
}

has(posSearch, "aria-expanded={searchExpanded}");
has(posSearch, "aria-controls={searchResultsId}");
has(posSearch, "id={searchInputId}");
has(posCss, ".posPremiumSearchCard[data-prisma-search-expanded=\"true\"]");
has(stock, "data-prisma-search-expanded");
has(stock, "aria-expanded={searchExpanded}");
has(stockCss, ".searchPanel[data-prisma-search-expanded=\"false\"]");
has(stockCss, ".searchPanel[data-prisma-search-expanded=\"true\"]");
has(shellCss, ".moreMenu summary:hover");
has(shellCss, ".moreMenu summary:focus-visible");
has(shellCss, ".moreMenu[open] summary");

if (failures.length) {
  console.error("FAIL TABLET_INTERACTIVE_JEWEL_SYSTEM_0207");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PASS TABLET_INTERACTIVE_JEWEL_SYSTEM_0207");
