import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const checks = [];
function file(rel) { return readFileSync(join(root, rel), "utf8"); }
function ok(name, condition) { checks.push({ name, ok: Boolean(condition) }); }

const nav = file("components/tablet-shell/tablet-nav.ts");
const shell = file("components/tablet-shell/prisma-tablet-shell.tsx");
const css = file("components/tablet-shell/prisma-tablet-shell.module.css");
const runtime = file("components/tablet-runtime/tablet-runtime-status-strip.tsx");
const home = file("components/tablet-home/tablet-home-screen.tsx");
const homeCss = file("components/tablet-home/tablet-home.module.css");

ok("nav mantiene export getVisibleTabletNavItems", nav.includes("export function getVisibleTabletNavItems"));
ok("nav ya no esconde rutas en Inicio", !nav.includes('return [navByHref("/")]') && nav.includes("return TABLET_NAV_ITEMS"));
ok("nav incluye Vender permanente", nav.includes('href: "/pos"') && nav.includes('primary: true'));
ok("nav incluye Inicio, Turno, Ventas, Catalogo, Existencias", ["/", "/shift", "/sales/today", "/catalog", "/stock"].every((href) => nav.includes(`href: "${href}"`)));
ok("nav incluye Soporte completo", ["/sync", "/offline", "/release-gate", "/settings/license"].every((href) => nav.includes(`href: "${href}"`)));
ok("nav agrupa Operacion Consulta Soporte", nav.includes("TABLET_NAV_GROUP_LABELS") && nav.includes("Consulta rapida") && nav.includes("Soporte"));
ok("shell usa groupedNavItems", shell.includes("groupedNavItems") && shell.includes("NAV_GROUP_ORDER"));
ok("shell usa logo como toggle", shell.includes("prisma-tablet-sidebar-toggle") && shell.includes('data-prisma-component="BrandCollapseToggle"'));
ok("shell integra runtime strip compacto en header", shell.includes('data-prisma-component="TopCommandBar"') && shell.includes('variant="compact"'));
ok("shell ya no renderiza RuntimeStatusStrip debajo del header", !shell.includes("</header>\n          <TabletRuntimeStatusStrip"));
ok("runtime strip soporta variante compact", runtime.includes('variant?: "full" | "compact"') && runtime.includes("runtimeStripCompact"));
ok("css contiene marker 05A", css.includes("PRISMA_TABLET_FLOW_CLARITY_05A_NAV_TOPBAR_COLLAPSE"));
ok("css contiene hotfix global 05B", css.includes("PRISMA_TABLET_FLOW_CLARITY_05B_GLOBAL_SHELL_HOTFIX"));
ok("css collapse no depende solo de tablet-pos", css.includes('.sidebarToggleInput:checked + .shell[data-prisma-product="tablet"]') && css.includes('grid-template-columns: 76px minmax(0, 1fr)'));
ok("css topbar compacta aplica a todas las rutas Tablet", css.includes('.shell[data-prisma-product="tablet"] .header') && css.includes('.shell[data-prisma-product="tablet"] .runtimeStripCompact'));
ok("css controla overflow de header", css.includes('overflow: hidden') && css.includes('.shell[data-prisma-product="tablet"] .headerControls'));
ok("home agrega mapa de flujo", home.includes("workflowSteps") && home.includes("Herramientas disponibles"));
ok("home incluye herramientas ocultas", ["/catalog", "/stock", "/sync", "/offline", "/release-gate", "/settings/license"].every((href) => home.includes(`href: "${href}"`)));
ok("home css tiene marker 05A", homeCss.includes("PRISMA_TABLET_FLOW_CLARITY_05A_HOME_MAP"));
ok("reduced motion respetado", css.includes("prefers-reduced-motion") && homeCss.includes("prefers-reduced-motion"));

const failed = checks.filter((check) => !check.ok);
console.log(JSON.stringify({ ok: failed.length === 0, checks }, null, 2));
if (failed.length) process.exit(1);
