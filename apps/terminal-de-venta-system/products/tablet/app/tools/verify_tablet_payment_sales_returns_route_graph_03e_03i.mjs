import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const read = rel => fs.readFileSync(path.join(root, rel), "utf8");
const exists = rel => fs.existsSync(path.join(root, rel));
function assert(ok, msg){ if(!ok){ console.error(`[FAIL] ${msg}`); process.exitCode = 1; } else console.log(`[OK] ${msg}`); }
const redirects = {
  "app/checkout/page.tsx": "/pos",
  "app/returns/page.tsx": "/sales/today",
  "app/sales/page.tsx": "/sales/today",
  "app/inventory/page.tsx": "/stock",
  "app/existencias/page.tsx": "/stock",
};
for (const [file, target] of Object.entries(redirects)){
  assert(exists(file), `exists ${file}`);
  assert(read(file).includes(`redirect("${target}")`), `${file} redirects to ${target}`);
}
const nav = read("components/tablet-shell/tablet-nav.ts");
const labels = [...nav.matchAll(/label:\s*"([^"]+)"/g)].map(m => m[1]);
assert(labels.length === 6, "nav has exactly six labels");
for (const required of ["Inicio","Vender","Ventas de hoy","Catálogo","Existencias","Turno"]) assert(labels.includes(required), `nav includes ${required}`);
for (const forbidden of ["Cobro","Devoluciones","Sincronización","Exportar","Sync","Outbox"]) assert(!labels.includes(forbidden), `nav excludes ${forbidden}`);
const sources = [
  "components/pos/pos-screen.tsx",
  "components/pos/pos-payment-panel.tsx",
  "components/pos/pos-sale-success.tsx",
  "components/sales/sales-today-screen.tsx",
  "components/sales/sales-ticket-detail-screen.tsx",
  "components/returns/return-from-ticket-screen.tsx",
].map(read).join("\n");
for (const visible of ["Cobro dentro de Vender","Confirmar venta","Ticket cerrado","Ventas de hoy","Hacer devolución","Confirmar devolución"]) assert(sources.includes(visible), `visible flow copy ${visible}`);
if(process.exitCode) process.exit(process.exitCode);
console.log("[OK] route graph verified");
