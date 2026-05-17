import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

export const PHASE5_GATE_IDS = ["Q26", "Q27", "Q28", "Q29", "Q30"];
export const PHASE5_TITLE = "PRISMA PQOS Phase 5: Release & Operator Readiness";

const LAUNCHERS = [
  ["01_LEVANTAR_TODO_LOCAL.cmd", "local_up.ps1"],
  ["02_LEVANTAR_TODO_CLOUDFLARE.cmd", "cloudflare_up.ps1"],
  ["03_LEVANTAR_TODO_LOCAL_Y_CLOUDFLARE.cmd", "all_up.ps1"],
  ["04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd", "health.ps1"],
  ["05_LEVANTAR_WEB_CONTROL_LOCAL.cmd", "web_control_local.ps1"],
  ["06_LEVANTAR_WEB_CONTROL_LOCAL_Y_CLOUDFLARE.cmd", "web_control_cloudflare.ps1"],
  ["07_ABRIR_PANEL_CONTROL_3150.cmd", "panel_3150.ps1"],
  ["08_LEVANTAR_CHART_LAB_LOCAL.cmd", "chart_lab_local.ps1"],
  ["09_KILL_EVERYTHING_PRISMA.cmd", "kill_everything.ps1"],
];

const REQUIRED_KILL_PORTS = ["3000", "3100", "3110", "3120", "3130", "3140", "3150", "3200"];
const OUT_DIR = "F:\\descargasf";

function exists(p) {
  return fs.existsSync(p);
}

function readSafe(p) {
  try {
    return fs.readFileSync(p, "utf8");
  } catch {
    return "";
  }
}

function listFilesRecursive(root, options = {}) {
  const out = [];
  const maxDepth = options.maxDepth ?? 8;
  const skip = new Set(options.skip ?? ["node_modules", ".git", ".next", "dist", "build"]);
  function walk(dir, depth) {
    if (depth > maxDepth || !exists(dir)) return;
    let entries = [];
    try {
      entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!skip.has(entry.name)) walk(full, depth + 1);
      } else {
        out.push(full);
      }
    }
  }
  walk(root, 0);
  return out;
}

function normalize(text) {
  return String(text || "").replace(/\\/g, "/").toLowerCase();
}

function loadJsonSafe(file) {
  try {
    return JSON.parse(readSafe(file));
  } catch {
    return null;
  }
}

function jsonContains(value, needle) {
  if (typeof value === "string") return value.includes(needle);
  if (Array.isArray(value)) return value.some((item) => jsonContains(item, needle));
  if (value && typeof value === "object") return Object.values(value).some((item) => jsonContains(item, needle));
  return false;
}

function result(gateId, title, blockers, warnings, evidence) {
  return {
    id: gateId,
    code: gateId,
    phase: 5,
    phaseName: PHASE5_TITLE,
    title,
    status: blockers.length > 0 ? "BLOCKED" : warnings.length > 0 ? "WARN" : "PASS",
    blockers,
    warnings,
    evidence,
    summary: `${gateId}: ${blockers.length} blockers, ${warnings.length} warnings, ${evidence.length} evidence items`,
    timestamp: new Date().toISOString(),
  };
}

function gateQ26(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const cc = path.join(root, "prisma-control-center");
  const wrappersDir = path.join(cc, "internal", "wrappers");
  for (const [cmd, wrapper] of LAUNCHERS) {
    const cmdPath = path.join(cc, cmd);
    const wrapperPath = path.join(wrappersDir, wrapper);
    if (!exists(cmdPath)) blockers.push(`Falta launcher oficial ${cmd}`);
    else evidence.push(`Launcher presente: ${cmd}`);
    if (!exists(wrapperPath)) blockers.push(`Falta wrapper oficial ${wrapper}`);
    else evidence.push(`Wrapper presente: ${wrapper}`);
    const cmdText = normalize(readSafe(cmdPath));
    if (exists(cmdPath) && !cmdText.includes(wrapper.toLowerCase())) {
      blockers.push(`${cmd} no referencia claramente ${wrapper}`);
    }
    if (cmdText.includes("prisma_launcher_runs")) {
      blockers.push(`${cmd} aun depende de PRISMA_LAUNCHER_RUNS`);
    }
  }
  const wrapperFiles = listFilesRecursive(wrappersDir, { maxDepth: 2, skip: [] });
  const wrapperCorpus = normalize(wrapperFiles.map(readSafe).join("\n"));
  if (wrapperCorpus.includes("prisma_launcher_runs")) {
    blockers.push("Wrappers aun mencionan PRISMA_LAUNCHER_RUNS");
  }
  if (!wrapperCorpus.includes("f:/descargasf") && !wrapperCorpus.includes("f:\\descargasf")) {
    blockers.push("Wrappers no muestran salida directa a F:\\descargasf");
  } else {
    evidence.push("Wrappers contienen salida directa a F:\\descargasf");
  }
  const killText = normalize(readSafe(path.join(wrappersDir, "kill_everything.ps1")) + "\n" + readSafe(path.join(cc, "09_KILL_EVERYTHING_PRISMA.cmd")));
  for (const port of REQUIRED_KILL_PORTS) {
    if (!killText.includes(port)) blockers.push(`Kill everything no cubre puerto ${port}`);
  }
  const healthText = normalize(readSafe(path.join(wrappersDir, "health.ps1")) + "\n" + readSafe(path.join(cc, "04_DIAGNOSTICO_LOCAL_Y_CLOUDFLARE.cmd")));
  if (healthText.includes("throw") && healthText.includes("fail") && !healthText.includes("optional")) {
    warnings.push("Diagnostico podria fallar duro ante health FAIL. Revisar opcionalidad runtime.");
  } else {
    evidence.push("Diagnostico no parece convertir todo FAIL operativo en bloqueo duro sin contexto.");
  }
  return result("Q26", "Launcher OS release readiness", blockers, warnings, evidence);
}

function gateQ27(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const outExists = exists(OUT_DIR);
  if (!outExists) blockers.push(`No existe ${OUT_DIR}`);
  else evidence.push(`${OUT_DIR} existe`);
  const latestDiagnose = path.join(OUT_DIR, "latest_DIAGNOSE.zip");
  const latestKill = path.join(OUT_DIR, "latest_KILL_EVERYTHING.zip");
  if (exists(latestDiagnose)) evidence.push("latest_DIAGNOSE.zip existe");
  else warnings.push("latest_DIAGNOSE.zip no existe ahora. Se acepta si el mecanismo esta documentado.");
  if (exists(latestKill)) evidence.push("latest_KILL_EVERYTHING.zip existe");
  else warnings.push("latest_KILL_EVERYTHING.zip no existe ahora. Se acepta si kill everything documenta su generacion.");
  const docCorpus = normalize([
    "prisma-control-center/README_OPERADOR.md",
    "prisma-control-center/README_OPERADOR_CRYSTAL.md",
    "quality/docs/phase-5-release-operator-readiness.md",
    "quality/docs/evidence-ledger-hardening.md",
  ].map((rel) => readSafe(path.join(root, rel))).join("\n"));
  for (const token of ["latest_diagnose.zip", "transcript.log", "summary.json", "f:/descargasf", "prisma_quality_os"]) {
    if (!docCorpus.includes(token)) blockers.push(`Evidencia no documenta ${token}`);
    else evidence.push(`Evidencia documentada: ${token}`);
  }
  if (!exists(path.join(root, "quality", "core", "evidence-writer.mjs"))) {
    warnings.push("No encontre quality/core/evidence-writer.mjs. Verificar writer equivalente.");
  } else {
    evidence.push("quality/core/evidence-writer.mjs presente");
  }
  return result("Q27", "Evidence bundle readiness", blockers, warnings, evidence);
}

function gateQ28(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const cc = path.join(root, "prisma-control-center");
  const wrappers = path.join(cc, "internal", "wrappers");
  const ccFiles = listFilesRecursive(cc, { maxDepth: 4, skip: ["node_modules", ".git"] });
  const badBak = ccFiles.filter((file) => /\.bak_/i.test(path.basename(file)) || /\.bak_/i.test(file));
  for (const file of badBak) blockers.push(`Archivo .bak_* activo: ${path.relative(root, file)}`);
  if (badBak.length === 0) evidence.push("Sin .bak_* activo en Control Center y wrappers");
  const legacyCandidates = [path.join(cc, "legacy_launchers"), path.join(root, "legacy_launchers")];
  for (const candidate of legacyCandidates) {
    if (exists(candidate)) blockers.push(`legacy_launchers activo: ${path.relative(root, candidate)}`);
  }
  if (!legacyCandidates.some(exists)) evidence.push("Sin legacy_launchers activo");
  const repoFiles = listFilesRecursive(root, { maxDepth: 3 });
  const tempFixes = repoFiles.filter((file) => /(^|[\\/])prisma_.*_fix\.py$/i.test(file) || /(^|[\\/])prisma_.*temp.*\.py$/i.test(file));
  for (const file of tempFixes) blockers.push(`Script temporal activo: ${path.relative(root, file)}`);
  if (tempFixes.length === 0) evidence.push("Sin scripts temporales prisma_*_fix.py en zonas principales del repo");
  const badRuns = path.join(OUT_DIR, "PRISMA_LAUNCHER_RUNS");
  if (exists(badRuns)) blockers.push(`${badRuns} no debe existir como carpeta permanente`);
  else evidence.push("Sin PRISMA_LAUNCHER_RUNS permanente en F:\\descargasf");
  if (!exists(wrappers)) warnings.push("No pude revisar wrappers porque falta la carpeta esperada");
  return result("Q28", "Cleanup and artifact hygiene", blockers, warnings, evidence);
}

function gateQ29(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const docs = [
    path.join(root, "prisma-control-center", "README_OPERADOR.md"),
    path.join(root, "prisma-control-center", "README_OPERADOR_CRYSTAL.md"),
    path.join(root, "quality", "docs", "phase-5-release-operator-readiness.md"),
  ];
  for (const doc of docs) {
    if (!exists(doc)) blockers.push(`Falta doc operador: ${path.relative(root, doc)}`);
    else evidence.push(`Doc presente: ${path.relative(root, doc)}`);
  }
  const corpus = normalize(docs.map(readSafe).join("\n"));
  const requiredTerms = [
    "3000", "3110", "3120", "3130", "3140", "3150",
    "launcher", "diagnost", "kill", "zip", "rollback", "cloudflare", "local", "f:/descargasf",
  ];
  for (const term of requiredTerms) {
    if (!corpus.includes(term)) blockers.push(`Docs operador no cubren '${term}'`);
    else evidence.push(`Docs cubren '${term}'`);
  }
  return result("Q29", "Operator docs readiness", blockers, warnings, evidence);
}

function gateQ30(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const packageJson = loadJsonSafe(path.join(root, "package.json"));
  const scripts = packageJson?.scripts || {};
  for (const scriptName of ["quality:phase5", "quality:release", "quality:pr"]) {
    if (typeof scripts[scriptName] !== "string") blockers.push(`package.json no tiene script ${scriptName}`);
    else evidence.push(`Script presente: ${scriptName} = ${scripts[scriptName]}`);
  }
  if (typeof scripts["quality:release"] === "string" && !normalize(scripts["quality:release"]).includes("phase5")) {
    blockers.push("quality:release no incluye Phase 5 ni quality:phase5");
  }
  const phase5 = loadJsonSafe(path.join(root, "quality", "profiles", "phase5.json"));
  const release = loadJsonSafe(path.join(root, "quality", "profiles", "release.json"));
  const manifest = loadJsonSafe(path.join(root, "quality", "prisma-quality.manifest.json"));
  for (const gate of PHASE5_GATE_IDS) {
    if (!jsonContains(phase5, gate)) blockers.push(`phase5.json no contiene ${gate}`);
    else evidence.push(`phase5.json contiene ${gate}`);
    if (!jsonContains(release, gate) && !jsonContains(release, "phase5")) blockers.push(`release.json no contiene ${gate} ni referencia Phase 5`);
    if (!jsonContains(manifest, gate)) blockers.push(`manifest no contiene ${gate}`);
  }
  for (const gate of PHASE5_GATE_IDS) {
    if (!exists(path.join(root, "quality", "gates", `${gate}.mjs`))) blockers.push(`Falta archivo gate ${gate}.mjs`);
  }
  return result("Q30", "Release profile readiness", blockers, warnings, evidence);
}

export async function runPhase5Gate(gateId, context = {}) {
  const root = path.resolve(context.root || process.env.PRISMA_ROOT || process.cwd());
  switch (gateId) {
    case "Q26": return gateQ26(root);
    case "Q27": return gateQ27(root);
    case "Q28": return gateQ28(root);
    case "Q29": return gateQ29(root);
    case "Q30": return gateQ30(root);
    default: throw new Error(`Unknown Phase 5 gate: ${gateId}`);
  }
}

export async function runPhase5All(context = {}) {
  const results = [];
  for (const gateId of PHASE5_GATE_IDS) {
    results.push(await runPhase5Gate(gateId, context));
  }
  return results;
}

export function isBlocked(result) {
  return result.status === "BLOCKED" || (Array.isArray(result.blockers) && result.blockers.length > 0);
}

export async function runCli(gateId) {
  const result = await runPhase5Gate(gateId, { root: process.cwd() });
  console.log(JSON.stringify(result, null, 2));
  process.exit(isBlocked(result) ? 1 : 0);
}

export function isDirectModule(importMetaUrl) {
  if (!process.argv[1]) return false;
  return fileURLToPath(importMetaUrl) === path.resolve(process.argv[1]);
}
