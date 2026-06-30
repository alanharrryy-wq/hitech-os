import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const mustExist = [
  "app/layout.tsx",
  "app/prisma-tablet-softglass-canonical.css",
  "components/tablet-shell/prisma-tablet-shell.tsx",
  "components/tablet-shell/prisma-tablet-shell.module.css",
  "components/pos/terminal-v2/pos-terminal-surface.tsx",
  "components/pos/terminal-v2/pos-terminal-surface.module.css",
  "components/pos/pos.module.css",
  "components/pos/pos-cobro-surface.module.css"
];

const read = (rel) => fs.readFileSync(path.join(root, rel), "utf8");
const failures = [];
const checks = [];
function check(id, pass, detail) {
  checks.push({ id, pass, detail });
  if (!pass) failures.push(`${id}: ${detail}`);
}

for (const rel of mustExist) check(`exists:${rel}`, fs.existsSync(path.join(root, rel)), "required canonical file exists");

const layout = read("app/layout.tsx");
const shell = read("components/tablet-shell/prisma-tablet-shell.tsx");
const shellCss = read("components/tablet-shell/prisma-tablet-shell.module.css");
const posSurface = read("components/pos/terminal-v2/pos-terminal-surface.tsx");
const posSurfaceCss = read("components/pos/terminal-v2/pos-terminal-surface.module.css");
const posCss = read("components/pos/pos.module.css");
const cobroCss = read("components/pos/pos-cobro-surface.module.css");

check("layout.imports.canonical", layout.includes('import "./prisma-tablet-softglass-canonical.css";'), "layout imports canonical softglass CSS");
check("layout.no.legacy.premium.imports", !/prisma-tablet-light-premium-final|prisma-tablet-background-workbench|prisma-tablet-premium-governed|TabletPremiumRuntimeEffects/.test(layout), "layout does not import old premium/background workbench layers");
check("layout.light.owner", /data-prisma-canonical-shell="softglass-reference-2606"/.test(layout), "layout sets canonical shell owner");
check("shell.no.aside", !/<aside\b/.test(shell), "Tablet shell has no sidebar aside owner");
check("shell.topbar", /className=\{styles\.topbar\}/.test(shell) && /bottomDock/.test(shell), "Tablet shell renders topbar and dock architecture");
check("shell.no.old.sidebar.tokens", !/sidebarClassName|TerminalStatusCard|GuidedSidebarNav|CollapsibleNavGroup|PrismaDarkSelector|TabletRuntimeStatusStrip/.test(shell), "Tablet shell does not render old sidebar/status stack");
check("shell.css.no.global.module", !/:global\(|^\s*(html|body)\b/m.test(shellCss), "shell CSS Module has no :global/html/body selectors");
check("shell.css.no.important", !/!important/.test(shellCss), "shell CSS has no !important");
check("shell.css.reference", /\.topbar[\s\S]*\.bottomDock/.test(shellCss) && !/\.sidebar\b/.test(shellCss), "shell CSS is topbar+dock, not sidebar");
check("pos.surface.canonical", /data-prisma-canonical-pos="softglass-reference-2606"/.test(posSurface), "POS surface is marked canonical");
check("pos.surface.no.legacy.effect", !/surface-breathing-glow|selected-pulse/.test(posSurface), "POS surface no longer uses old decorative effect contract as owner");
check("pos.surface.css.grid", /grid-template-columns:\s*minmax\(0, 1fr\) minmax\(305px, 360px\)/.test(posSurfaceCss), "POS surface uses reference product/ticket grid");
check("pos.css.marker", /PRISMA_SOFTGLASS_CANONICAL_2606_START[\s\S]*PRISMA_SOFTGLASS_CANONICAL_2606_END/.test(posCss), "POS module has canonical override section");
check("cobro.css.marker", /PRISMA_SOFTGLASS_CANONICAL_2606_START[\s\S]*PRISMA_SOFTGLASS_CANONICAL_2606_END/.test(cobroCss), "Cobro module has canonical override section");
check("no.documented.legacy.done", !/documentedLegacySurface|rootOnly/.test(shell + posSurface), "new owners do not claim legacy/root-only done states");

const evidenceDir = path.join(root, "tools", "evidence");
fs.mkdirSync(evidenceDir, { recursive: true });
const report = {
  status: failures.length ? "FAIL" : "PASS",
  generatedAt: new Date().toISOString(),
  checks,
  failures,
  scope: "Tablet canonical Softglass architecture only. PC/Mobile/Chart Lab not modified."
};
fs.writeFileSync(path.join(evidenceDir, "tablet-softglass-canonical-report.json"), JSON.stringify(report, null, 2));
fs.writeFileSync(path.join(evidenceDir, "tablet-softglass-canonical-report.md"), `# Tablet Softglass Canonical Report\n\nStatus: ${report.status}\n\n${checks.map((c) => `- ${c.pass ? "PASS" : "FAIL"} ${c.id}: ${c.detail}`).join("\n")}\n`);

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}
console.log(`TABLET_SOFTGLASS_CANONICAL PASS (${checks.length} checks)`);
