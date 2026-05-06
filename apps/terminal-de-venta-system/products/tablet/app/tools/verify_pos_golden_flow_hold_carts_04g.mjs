import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const posScreen = readFileSync(resolve(root, "components/pos/pos-screen.tsx"), "utf8");
const ticket = readFileSync(resolve(root, "components/pos/pos-ticket-panel.tsx"), "utf8");
const held = readFileSync(resolve(root, "src/lib/pos/held-carts.ts"), "utf8");

const checks = [];
function check(name, ok) { checks.push({ name, ok: Boolean(ok) }); }

check("04G guardado de tickets sigue instalado", held.includes("POS_HELD_CARTS_STORAGE_KEY") && held.includes("addHeldCart"));
check("04G se opera por boton touch guardar", ticket.includes('data-prisma-component="HoldCartButton"') && ticket.includes("onClick={onHold}"));
check("04G ya no exige atajos de teclado", !ticket.includes("F4") && !ticket.includes("F6") && !posScreen.includes("PosPaymentKeyboardBridge"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error(JSON.stringify({ ok: false, failed, checks }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, package: "PRISMA_TABLET_POS_GOLDEN_FLOW_HOLD_CARTS_04G_SUPERSEDED_BY_04H", checks }, null, 2));
