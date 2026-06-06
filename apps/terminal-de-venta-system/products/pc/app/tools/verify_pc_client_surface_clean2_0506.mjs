import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const checks = [];
function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}
function exists(rel) {
  return fs.existsSync(path.join(root, rel));
}
function check(name, ok, detail = "") {
  checks.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"} ${name}${detail ? ` :: ${detail}` : ""}`);
}

const rootPage = read("app/page.tsx");
check("home redirects to dashboard", /redirect\([\"']\/dashboard[\"']\)/.test(rootPage));
check("home no longer imports heavy business overview", !rootPage.includes("PrismaBusinessOverview"));

const lab = read("app/laboratorio-pc/page.tsx");
check("lab hub exists and is static", lab.includes('dynamic = "force-static"') && lab.includes("Interfaces oscuras centralizadas"));
check("lab hub links dashboard governor", lab.includes("/laboratorio-pc/dashboard-governor"));

const governor = read("app/laboratorio-pc/dashboard-governor/page.tsx");
check("dashboard governor imports CSSProperties type", governor.includes('import type { CSSProperties } from "react"'));
check("dashboard governor is lab surface", governor.includes('data-prisma-surface="pc-dashboard-lab"'));

for (const route of ["laboratorio-pc", "laboratorio-pc/dashboard-governor", "license-runtime", "metricas-dia", "movements", "ordenes-compra", "outbox-operativo"]) {
  check(`${route} loading exists`, exists(`app/${route}/loading.tsx`));
  check(`${route} error boundary exists`, exists(`app/${route}/error.tsx`));
}

const lic = read("app/license-runtime/page.tsx");
check("license runtime has timeout fallback", lic.includes("SCREEN_TIMEOUT_MS") && lic.includes("timeoutModel"));

const mov = read("app/movements/page.tsx");
check("movements has timeout fallback", mov.includes("SCREEN_TIMEOUT_MS") && mov.includes("fallbackOverview"));

const metricas = read("app/metricas-dia/page.tsx");
const ordenes = read("app/ordenes-compra/page.tsx");
const outbox = read("app/outbox-operativo/page.tsx");
check("decision routes are static", [metricas, ordenes, outbox].every((txt) => txt.includes('dynamic = "force-static"')));
check("ordenes uses own currentPath", ordenes.includes('currentPath="/ordenes-compra"'));
check("outbox uses own currentPath", outbox.includes('currentPath="/outbox-operativo"'));

const failed = checks.filter((item) => !item.ok);
console.log(`\nclean2 verification: ${checks.length - failed.length}/${checks.length} PASS`);
if (failed.length) process.exit(1);
