#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const toolsDir = path.dirname(__filename);
const appRoot = path.resolve(toolsDir, "..");

function exists(p) {
  return fs.existsSync(p);
}

function read(p) {
  return fs.readFileSync(p, "utf8");
}

function readJson(p) {
  return JSON.parse(read(p));
}

function listFiles(root) {
  const out = [];
  if (!exists(root)) return out;
  const stack = [root];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (["node_modules", ".next", "dist", "build", ".git"].includes(entry.name)) continue;
        stack.push(full);
      } else {
        out.push(full);
      }
    }
  }
  return out;
}

function runNode(relativeTool) {
  const full = path.join(appRoot, relativeTool);
  const result = spawnSync(process.execPath, [full], {
    cwd: appRoot,
    encoding: "utf8",
    shell: false,
  });
  return {
    tool: relativeTool,
    path: full,
    exists: exists(full),
    status: result.status,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    ok: exists(full) && result.status === 0,
  };
}

const checks = [];
function check(id, ok, detail) {
  checks.push({ id, ok, detail });
}

const previousVerifiers = [
  "tools/verify_tablet_i01_runtime.mjs",
  "tools/verify_tablet_i02_catalogo.mjs",
  "tools/verify_tablet_i03a_ticket_detail.mjs",
  "tools/verify_tablet_03_pos_unificado.mjs",
  "tools/verify_tablet_04_offline_export.mjs",
];

const requiredFiles = [
  "data/.gitkeep",
  "src/server/local-catalog/index.ts",
  "data/tablet-catalog.local.json",
  "app/api/pos/catalog/products/route.ts",
  "app/api/pos/sales/detail/route.ts",
  "app/checkout/page.tsx",
  "app/api/pos/offline/audit/route.ts",
  "app/offline/page.tsx",
  "docs/qa/TABLET_LOCAL_PY_WORKFLOW_CONTRACT.md",
  "docs/qa/TABLET_05_RELEASE_READINESS.md",
];

for (const relative of requiredFiles) {
  check(`R05-FILE-${relative}`, exists(path.join(appRoot, relative)), relative);
}

for (const verifier of previousVerifiers) {
  check(`R05-VERIFIER-EXISTS-${verifier}`, exists(path.join(appRoot, verifier)), verifier);
}

const verifierRuns = previousVerifiers.map(runNode);
for (const run of verifierRuns) {
  check(`R05-VERIFIER-RUN-${run.tool}`, run.ok, { status: run.status, stderr: run.stderr.slice(0, 800) });
}

const pkgPath = path.join(appRoot, "package.json");
check("R05-PACKAGE-EXISTS", exists(pkgPath), pkgPath);
if (exists(pkgPath)) {
  const pkg = readJson(pkgPath);
  const scripts = pkg.scripts || {};
  const requiredScripts = [
    "verify:i01-runtime",
    "verify:i02-catalogo",
    "verify:i03a-ticket-detail",
    "verify:03-pos",
    "verify:04-offline",
    "verify:05-release",
    "tablet:05:release",
  ];
  for (const script of requiredScripts) {
    check(`R05-SCRIPT-${script}`, Boolean(scripts[script]), script);
  }
}

const releaseEvidenceRoot = path.join(appRoot, "evidence", "release");
const chainedEvidenceDir = path.join(releaseEvidenceRoot, "previous-verifiers");
fs.mkdirSync(chainedEvidenceDir, { recursive: true });

for (const run of verifierRuns) {
  const safeName = run.tool.replace(/[\/:]+/g, "_").replace(/\.mjs$/, "");
  const evidencePath = path.join(chainedEvidenceDir, `${safeName}.txt`);
  fs.writeFileSync(
    evidencePath,
    `COMMAND: ${process.execPath} ${run.path}
EXIT_CODE: ${run.status}

STDOUT:
${run.stdout}

STDERR:
${run.stderr}
`,
    "utf8",
  );
  check(
    `R05-EVIDENCE-GENERATED-${run.tool}`,
    exists(evidencePath),
    path.relative(appRoot, evidencePath).split(path.sep).join("/"),
  );
}

const legacyEvidenceFiles = [
  "evidence/verifier-output/verify_tablet_i02_catalogo.txt",
  "evidence/verifier-output/verify_tablet_i03a_ticket_detail.txt",
  "evidence/verifier-output/verify_tablet_03_pos_unificado.txt",
  "evidence/verifier-output/verify_tablet_04_offline_export.txt",
  "evidence/tablet_i02_file_inventory.json",
  "evidence/tablet_i03a_file_inventory.json",
  "evidence/tablet_03_pos_file_inventory.json",
  "evidence/tablet_04_offline_file_inventory.json",
];

const legacyEvidenceStatus = legacyEvidenceFiles.map((relative) => ({
  relative,
  exists: exists(path.join(appRoot, relative)),
}));

const workflowPath = path.join(appRoot, "docs", "qa", "TABLET_LOCAL_PY_WORKFLOW_CONTRACT.md");
if (exists(workflowPath)) {
  const workflow = read(workflowPath);
  check("R05-WORKFLOW-ONE-PY", workflow.includes("un solo `.py` autocontenido"), workflowPath);
  check("R05-WORKFLOW-RUN", workflow.includes("--run"), workflowPath);
  check("R05-WORKFLOW-ROLLBACK", workflow.includes("--rollback"), workflowPath);
  check("R05-WORKFLOW-DESCARGASF", workflow.includes("F:\\descargasf"), workflowPath);
}

const productionRoots = ["app", "components", "src", "lib"]
  .map((segment) => path.join(appRoot, segment))
  .filter((root) => exists(root));
const productionFiles = productionRoots
  .flatMap((root) => listFiles(root))
  .filter((file) => /\.(ts|tsx|js|jsx)$/.test(file));
const bizDemoHits = [];
for (const file of productionFiles) {
  const rel = path.relative(appRoot, file).split(path.sep).join("/");
  const text = read(file);
  if (text.includes("biz_demo_001")) {
    bizDemoHits.push(rel);
  }
}
check("R05-NO-BIZ-DEMO-001-PRODUCTION", bizDemoHits.length === 0, bizDemoHits);

const ok = checks.every((item) => item.ok);
const releaseDir = path.join(appRoot, "evidence", "release");
const verifierDir = path.join(appRoot, "evidence", "verifier-output");
fs.mkdirSync(releaseDir, { recursive: true });
fs.mkdirSync(verifierDir, { recursive: true });

const report = {
  ok,
  appRoot,
  generatedAt: new Date().toISOString(),
  release: "tablet_05_release",
  checks,
  verifierRuns: verifierRuns.map((run) => ({
    tool: run.tool,
    exists: run.exists,
    status: run.status,
    ok: run.ok,
    stdoutPreview: run.stdout.slice(0, 1200),
    stderrPreview: run.stderr.slice(0, 1200),
  })),
  bizDemoHits,
  legacyEvidenceStatus,
  verdict: ok ? "READY" : "BLOCKED",
  note: "R05 chains all previous Tablet verifiers, checks evidence, blocks biz_demo_001, and writes release readiness evidence."
};

const jsonPath = path.join(releaseDir, "tablet_05_release_readiness.json");
const mdPath = path.join(releaseDir, "tablet_05_release_readiness.md");
fs.writeFileSync(jsonPath, JSON.stringify(report, null, 2) + "\n", "utf8");

const gateRows = checks.map((item) => `| ${item.id} | ${item.ok ? "PASS" : "FAIL"} | ${typeof item.detail === "string" ? item.detail.replace(/\|/g, "\\|") : JSON.stringify(item.detail).replace(/\|/g, "\\|")} |`).join("\n");
const md = `# Tablet 05 Release Readiness\n\n` +
  `Generated: ${report.generatedAt}\n\n` +
  `Final status: **${report.verdict}**\n\n` +
  `## Gate matrix\n\n| Gate | Estado | Evidencia |\n|---|---|---|\n${gateRows}\n\n` +
  `## Verifier chain\n\n` +
  verifierRuns.map((run) => `- ${run.ok ? "PASS" : "FAIL"} ${run.tool} exit=${run.status}`).join("\n") +
  `\n\n## biz_demo_001 hits\n\n${bizDemoHits.length ? bizDemoHits.map((hit) => `- ${hit}`).join("\n") : "Sin hallazgos."}\n`;
fs.writeFileSync(mdPath, md, "utf8");
fs.writeFileSync(path.join(verifierDir, "verify_tablet_05_release_readiness.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report, null, 2));
process.exit(ok ? 0 : 2);
