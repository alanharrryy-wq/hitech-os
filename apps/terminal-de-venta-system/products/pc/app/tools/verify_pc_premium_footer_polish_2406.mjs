import fs from "node:fs";
import path from "node:path";

const repo = process.argv[2];
if (!repo) {
  console.error("Usage: node verify_pc_premium_footer_polish_2406.mjs <repo>");
  process.exit(2);
}

const pcRoot = path.join(repo, "apps", "terminal-de-venta-system", "products", "pc", "app");
const appShellPath = path.join(pcRoot, "components", "layout", "app-shell.tsx");
const premiumCssPath = path.join(pcRoot, "app", "prisma-pc-premium-visual-system.css");

const appShell = fs.readFileSync(appShellPath, "utf8");
const premiumCss = fs.readFileSync(premiumCssPath, "utf8");

const requiredShellTokens = [
  "pc-premium-footer-stack",
  "pc-premium-sidebar-status",
  "pc-premium-status-line",
  "pc-premium-footer-actions",
  "SidebarStatusDock",
  "Sin ruido visual abajo"
];

const requiredCssTokens = [
  "PCVIS_POL1_PREMIUM_FOOTER_BEGIN",
  "pc-premium-footer-stack",
  "pc-premium-sidebar-status",
  "pc-premium-status-line",
  "pc-premium-footer-actions",
  "grid-template-columns: minmax(0, 1fr) minmax(0, 1fr)",
  "position: sticky"
];

const missingShell = requiredShellTokens.filter((token) => !appShell.includes(token));
const missingCss = requiredCssTokens.filter((token) => !premiumCss.includes(token));

const broadFooterStackGlass = premiumCss.includes('html[data-prisma-surface="pc-backoffice"] .footer-stack > *');
const priorityOverride = appShell.includes("!important") || premiumCss.includes("!important");

if (missingShell.length || missingCss.length || broadFooterStackGlass || priorityOverride) {
  console.error(JSON.stringify({
    ok: false,
    missingShell,
    missingCss,
    broadFooterStackGlass,
    priorityOverride
  }, null, 2));
  process.exit(1);
}

console.log("PC PREMIUM FOOTER POLISH VERIFY OK");
