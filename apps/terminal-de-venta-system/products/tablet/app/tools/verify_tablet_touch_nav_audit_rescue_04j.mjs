import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const files = {
  bridge: "components/pos/pos-payment-keyboard-bridge.tsx",
  pos: "components/pos/pos-screen.tsx",
  ticket: "components/pos/pos-ticket-panel.tsx",
  nav: "components/tablet-shell/tablet-nav.ts",
  shell: "components/tablet-shell/prisma-tablet-shell.tsx",
  css: "components/tablet-shell/prisma-tablet-shell.module.css"
};

function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}

function exists(rel) {
  return fs.existsSync(path.join(root, rel));
}

function check(label, ok) {
  if (!ok) {
    console.error(`FAIL ${label}`);
    process.exitCode = 1;
  } else {
    console.log(`OK ${label}`);
  }
}

const pos = read(files.pos);
const ticket = read(files.ticket);
const nav = read(files.nav);
const shell = read(files.shell);
const css = read(files.css);

check("keyboard bridge eliminado", !exists(files.bridge));
check("pos-screen no monta keyboard bridge", !pos.includes("PosPaymentKeyboardBridge"));
check("ticket sin teclas F", !["F2", "F3", "F4", "F5", "F6"].some((key) => ticket.includes(key)));
check("ticket usa acciones touch", ["Guardar ticket", "Cancelar venta", "Recuperar", "Opciones de ticket"].every((needle) => ticket.includes(needle)));
check("tablet nav incluye etapas de flujo", nav.includes("TabletFlowStage") && nav.includes("getTabletFlowStage"));
check("tablet nav incluye items finales visibles", nav.includes("getVisibleTabletNavItems") && nav.includes("return TABLET_NAV_ITEMS"));
check("shell usa topbar contextual y dock final", shell.includes("contextChips") && shell.includes('data-prisma-component="TabletBottomNav"') && !shell.includes('data-prisma-component="TopNavItem"'));
check("shell expone data flow stage", shell.includes("data-prisma-flow-stage"));
check("css incluye densidad compacta de topbar y dock", css.includes(".topbar") && css.includes(".bottomDockInner") && css.includes(".compactSellingShell") && css.includes("min-height: 52px"));
check("pos no reintroduce header gigante", shell.includes("compactSellingSurface") && shell.includes("!compactSellingSurface") && css.includes(".compactSellingShell .main"));

if (process.exitCode) {
  process.exit(process.exitCode);
}

console.log(JSON.stringify({ ok: true, package: "PRISMA_TABLET_TOUCH_NAV_AUDIT_RESCUE_04J", status: "ready" }, null, 2));
