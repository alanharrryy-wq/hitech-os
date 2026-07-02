import fs from "node:fs";
import path from "node:path";

const repo = process.cwd();
const root = path.join(repo, "apps", "terminal-de-venta-system");
const read = (rel) => fs.readFileSync(path.join(root, rel), "utf8");

const nav = read("products/tablet/app/components/tablet-shell/tablet-nav.ts");
const shell = read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx");
const contracts = read("products/tablet/app/src/navigation/tablet-page-contracts.ts");

const failures = [];
const ok = (name, condition) => {
  if (!condition) failures.push(name);
};

ok("tablet-nav imports TABLET_FINAL_NAVIGATION", nav.includes("TABLET_FINAL_NAVIGATION"));
ok("tablet-nav imports TABLET_PAGE_CONTRACTS", nav.includes("TABLET_PAGE_CONTRACTS"));
ok("TABLET_NAV_ITEMS derived from contracts", nav.includes("export const TABLET_NAV_ITEMS: TabletNavItem[] = TABLET_FINAL_NAVIGATION"));
ok("getVisibleTabletNavItems still exported", nav.includes("export function getVisibleTabletNavItems"));
ok("visible nav returns TABLET_NAV_ITEMS", nav.includes("return TABLET_NAV_ITEMS"));
ok("final tablet routes are represented by presentation map", ["/pos", "/shift", "/stock", "/sales/today", "/returns", "/sync", "/settings/license"].every((href) => nav.includes(`"${href}"`)));
ok("lab/internal/reference routes not represented as nav hrefs in tablet-nav", ![
  'href: "/visual-os"',
  'href: "/referencia-visual"',
  'href: "/release-gate"',
  'href: "/screen-standard-preview"',
  'href: "/prisma-dark-pos-reference"',
  'href: "/prisma-visual-catalog"',
  'href: "/events/outbox"'
].some((needle) => nav.includes(needle)));

ok("shell top navigation uses visibleNavItems directly", shell.includes("const primaryTopItems = visibleNavItems;"));
ok("shell dock uses product routes", shell.includes('["/pos", "/shift", "/stock", "/sales/today", "/returns", "/sync"]'));
ok("shell top/dock no longer promote root/catalog lists", !shell.includes('["/", "/pos", "/catalog"'));
ok("brand points to selling route", shell.includes('href="/pos" aria-label="Ir a vender en PRISMA POS"'));
ok("store chip points to canonical stock route", shell.includes('href="/stock"'));

ok("contracts still define lab routes as non-final", contracts.includes("TABLET_FINAL_NAVIGATION") && contracts.includes("visibility: 'lab'") && contracts.includes("finalMenu: false"));

if (failures.length) {
  console.error("FAIL TABLET_SHELL_PRODUCT_NAVIGATION_WIRING_0207");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PASS TABLET_SHELL_PRODUCT_NAVIGATION_WIRING_0207");
console.log("Tablet unified shell navigation consumes TABLET_FINAL_NAVIGATION and no longer promotes lab/reference/root/catalog as final shell navigation.");
