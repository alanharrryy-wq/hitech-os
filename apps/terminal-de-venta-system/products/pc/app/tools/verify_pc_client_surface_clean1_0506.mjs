import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const checks = [];
function file(rel) { return path.join(appRoot, rel); }
function text(rel) { return readFileSync(file(rel), "utf8"); }
function ok(name, pass, detail = "") { checks.push({ name, pass, detail }); }

const appShell = text("components/layout/app-shell.tsx");
ok("AppShell no importa PrismaDarkSelector", !appShell.includes("PrismaDarkSelector"));
ok("AppShell footer no apunta a /referencia-visual", !appShell.includes('href="/referencia-visual"'));
ok("AppShell filtra lab/internal en secundaria", appShell.includes('item.status !== "internal"') && appShell.includes('item.status !== "lab"'));

const layout = text("app/layout.tsx");
ok("Layout fuerza prisma-light", layout.includes('root.dataset.prismaSkin = "light"') && layout.includes('root.dataset.theme = "prisma-light"'));
ok("Layout ya no resuelve dark por localStorage", !layout.includes('prefers-color-scheme: dark'));

const navigation = text("src/composition/navigation.ts");
ok("Navigation tiene helper de visibilidad cliente", navigation.includes("isClientVisibleRouteStatus"));
ok("Navigation excluye rutas lab", navigation.includes('status !== "lab"'));

const decision = text("src/uiux/decision-model.ts");
ok("Subnav cliente no muestra Chart Lab", !decision.includes('label: "Chart Lab"'));
ok("Ayuda cliente no apunta a referencia visual", !decision.includes('href: "/referencia-visual"'));

ok("Hub laboratorio existe", existsSync(file("app/laboratorio-pc/page.tsx")));
ok("Chart Lab aislado existe", existsSync(file("app/laboratorio-pc/chart-lab/page.tsx")));
ok("Dashboard governor aislado existe", existsSync(file("app/laboratorio-pc/dashboard-governor/page.tsx")));
ok("Referencia visual aislada existe", existsSync(file("app/laboratorio-pc/referencia-visual/page.tsx")));

const refRedirect = text("app/referencia-visual/page.tsx");
ok("/referencia-visual redirige al laboratorio", refRedirect.includes('redirect("/laboratorio-pc/referencia-visual")'));
const chartRedirect = text("app/prisma-insights/chart-lab/page.tsx");
ok("/prisma-insights/chart-lab redirige al laboratorio", chartRedirect.includes('redirect("/laboratorio-pc/chart-lab?preview=charts")'));

const catalogService = text("src/lib/services/catalog.ts");
ok("Catalog service captura error Prisma", catalogService.includes("try {") && catalogService.includes("buildDataNotice(error)"));
ok("Catalog service no expone paths locales crudos", catalogService.includes("<LOCAL_PATH>") && catalogService.includes("<LOCAL_DB>"));

const table = text("components/ui/table-simple.tsx");
ok("TableSimple tiene emptyMessage", table.includes("emptyMessage") && table.includes("colSpan"));

const failed = checks.filter((check) => !check.pass);
console.log(JSON.stringify({ ok: failed.length === 0, total: checks.length, failed, checks }, null, 2));
if (failed.length) process.exit(1);
