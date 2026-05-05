import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const checks = [];
function file(rel) { return readFileSync(join(root, rel), "utf8"); }
function ok(name, condition) { checks.push({ name, ok: Boolean(condition) }); }

const nav = file("components/tablet-shell/tablet-nav.ts");
const shell = file("components/tablet-shell/prisma-tablet-shell.tsx");
const css = file("components/tablet-shell/prisma-tablet-shell.module.css");
const pos = file("components/pos/pos-screen.tsx");
const ticket = file("components/pos/pos-ticket-panel.tsx");
const qa = file("docs/qa/PRISMA_TABLET_FLOW_GUIDED_SIDEBAR_04I_ACCEPTANCE.md");

ok("nav exporta getVisibleTabletNavItems", nav.includes("export function getVisibleTabletNavItems"));
ok("nav inicio regresa solo Inicio", nav.includes('if (stage === "inicio")') && nav.includes('return [navByHref("/")]'));
ok("nav detecta pendientes contextuales", nav.includes("hasPendingWork(snapshot)") && nav.includes('navByHref("/sync")'));
ok("nav detecta estado contextual", nav.includes("hasSystemAttention(snapshot)") && nav.includes('navByHref("/release-gate")'));
ok("shell usa visibleNavItems", shell.includes("const visibleNavItems = getVisibleTabletNavItems") && shell.includes("visibleNavItems.map"));
ok("shell declara data-prisma-flow-stage", shell.includes("data-prisma-flow-stage={flowStage}"));
ok("shell marca GuidedSidebarNav", shell.includes('data-prisma-component="GuidedSidebarNav"'));
ok("css contiene marker 04I", css.includes("PRISMA_TABLET_FLOW_GUIDED_SIDEBAR_04I"));
ok("css especializa inicio", css.includes('data-prisma-flow-stage="inicio"'));
ok("pos ya no importa keyboard bridge", !pos.includes("PosPaymentKeyboardBridge"));
ok("keyboard bridge eliminado", !existsSync(join(root, "components/pos/pos-payment-keyboard-bridge.tsx")));
ok("ticket no muestra F2 F3 F4 F5 F6", !/F[2-6]/.test(ticket));
ok("ticket muestra acciones touch", ticket.includes("Tocar") && ticket.includes("Guardar") && ticket.includes("Limpiar") && ticket.includes("Recuperar"));
ok("qa documenta inicio limpio", qa.includes("sidebar renderiza solo `Inicio`"));

const failed = checks.filter((check) => !check.ok);
console.log(JSON.stringify({ ok: failed.length === 0, checks }, null, 2));
if (failed.length) process.exit(1);
