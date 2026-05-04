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
function read(rel) { return readFileSync(resolve(tabletRoot, rel), "utf8"); }

const posScreen = read("components/pos/pos-screen.tsx");
const ticket = read("components/pos/pos-ticket-panel.tsx");
const held = read("src/lib/pos/held-carts.ts");

const checks = [];
function check(name, ok) { checks.push({ name, ok: Boolean(ok) }); }

check("04G guardado de tickets sigue instalado", held.includes("POS_HELD_CARTS_STORAGE_KEY") && held.includes("addHeldCart"));
check("04G se opera por boton touch guardar", ticket.includes('data-prisma-component="HoldCartButton"') && ticket.includes("onClick={onHold}"));
check("04G ya no exige atajos de teclado", !ticket.includes("F4") && !ticket.includes("F6") && !posScreen.includes("PosPaymentKeyboardBridge"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error(JSON.stringify({ ok: false, tabletRoot, failed, checks }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, tabletRoot, package: "PRISMA_TABLET_POS_GOLDEN_FLOW_HOLD_CARTS_04G", checks }, null, 2));
