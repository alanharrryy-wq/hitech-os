import { readFileSync } from "node:fs";

const checks = [];
function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), ...(detail ? { detail } : {}) });
}

function includes(file, text) {
  return file.includes(text);
}

const search = readFileSync("components/pos/pos-product-search.tsx", "utf8");
const list = readFileSync("components/pos/pos-product-list.tsx", "utf8");
const css = readFileSync("components/pos/pos.module.css", "utf8");
const doc = readFileSync("docs/pos/PRISMA_TABLET_POS_DENSITY_SEARCH_CARDS_05C.md", "utf8");

check("search component marks 05C density", includes(search, "data-prisma-search-density=\"05C\""));
check("search component exposes expanded state", includes(search, "data-prisma-search-expanded"));
check("search expands when query/loading/error exist", includes(search, "Boolean(query.trim()) || loading || Boolean(error)"));
check("visible product card no longer renders SKU label", !includes(list, "SKU {product.sku}"));
check("visible product card no longer renders CB label", !includes(list, "CB {product.barcode}"));
check("product name still rendered", includes(list, "className={styles.productName}"));
check("product category badges preserved", includes(list, "productMetaRail"));
check("price and add button preserved", includes(list, "formatMoney(product.priceCents)") && includes(list, "onAdd(product)"));
check("css has 05C marker", includes(css, "PRISMA_TABLET_POS_DENSITY_SEARCH_CARDS_05C::START"));
check("css removes search outer panel", includes(css, "background: transparent !important") && includes(css, "box-shadow: none !important"));
check("css hides actions by default", includes(css, "max-height: 0 !important") && includes(css, "pointer-events: none !important"));
check("css reveals actions on focus", includes(css, ".searchCard:focus-within .searchActions"));
check("css reveals actions on expanded state", includes(css, ".searchCard[data-prisma-search-expanded=\"true\"] .searchActions"));
check("css compacts category chips", includes(css, ".categoryButtonActive") && includes(css, "min-height: 44px !important"));
check("css keeps reduced motion", includes(css, "prefers-reduced-motion"));
check("doc created", includes(doc, "PRISMA Tablet POS Density Search Cards 05C"));

const ok = checks.every((item) => item.ok);
console.log(JSON.stringify({ ok, checks }, null, 2));
if (!ok) process.exit(1);
