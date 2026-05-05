import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

function findTabletRoot() {
  const cwd = process.cwd();
  const candidates = [
    cwd,
    resolve(cwd, "products/tablet/app"),
    resolve(cwd, "apps/terminal-de-venta-system/products/tablet/app")
  ];
  for (const candidate of candidates) {
    if (existsSync(resolve(candidate, "components/pos/pos-screen.tsx"))) return candidate;
  }
  console.error(JSON.stringify({ ok: false, error: "TABLET_ROOT_NOT_FOUND", cwd, candidates }, null, 2));
  process.exit(1);
}

const tabletRoot = findTabletRoot();
const files = {
  posScreen: resolve(tabletRoot, "components/pos/pos-screen.tsx"),
  ticket: resolve(tabletRoot, "components/pos/pos-ticket-panel.tsx"),
  darkCart: resolve(tabletRoot, "components/prisma-dark-pos/prisma-cart-panel.tsx"),
  keyboard: resolve(tabletRoot, "components/pos/pos-payment-keyboard-bridge.tsx"),
  ux: resolve(tabletRoot, "docs/ux/PRISMA_TABLET_POS_TOUCH_ONLY_ACTIONS_04H.md"),
  qa: resolve(tabletRoot, "docs/qa/PRISMA_TABLET_POS_TOUCH_ONLY_ACTIONS_04H_ACCEPTANCE.md")
};

function read(filePath) { return readFileSync(filePath, "utf8"); }
const posScreen = read(files.posScreen);
const ticket = read(files.ticket);
const darkCart = read(files.darkCart);
const ux = read(files.ux);
const qa = read(files.qa);

const checks = [];
function check(name, ok) { checks.push({ name, ok: Boolean(ok) }); }
function noFunctionKeyCopy(text) { return !/\bF[2-9]\b/.test(text); }

check("keyboard bridge file removed", !existsSync(files.keyboard));
check("pos screen no keyboard bridge import", !posScreen.includes("PosPaymentKeyboardBridge"));
check("pos screen marked touch only 04h", posScreen.includes('data-prisma-golden-flow="touch-only-actions-04h"'));
check("ticket no visible function keys", noFunctionKeyCopy(ticket));
check("dark pos reference no visible function keys", noFunctionKeyCopy(darkCart));
check("checkout cta remains touchable", ticket.includes("COBRAR") && ticket.includes("Tocar"));
check("held cart restore is explicit", ticket.includes("Recuperar") && !ticket.includes('index === 0 ? "F6"'));
check("04h ux doc installed", ux.includes("Touch Only Actions 04H"));
check("04h acceptance installed", qa.includes("Acceptance 04H"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error(JSON.stringify({ ok: false, tabletRoot, failed, checks }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, tabletRoot, package: "PRISMA_TABLET_POS_TOUCH_ONLY_ACTIONS_04H", checks }, null, 2));
