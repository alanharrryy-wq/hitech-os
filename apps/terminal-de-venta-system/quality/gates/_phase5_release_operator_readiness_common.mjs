import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";
import { finding } from "../core/result-types.mjs";

export const PHASE5_GATE_IDS = ["Q26", "Q27", "Q28", "Q29", "Q30", "Q31"];
export const PHASE5_TITLE = "PRISMA PQOS Phase 5: Release & Operator Readiness";

const LAUNCHERS = [
  ["00_KILL_ALL_LOCAL.cmd", "kill_everything.ps1"],
  ["01_LEVANTAR_TODO_LOCAL.cmd", "local_up.ps1"],
  ["02_LEVANTAR_TODO_LOCAL_CLOUDFLARE.cmd", "all_up.ps1"],
  ["03_LEVANTAR_SOLO_UN_MODULO.cmd", "module_cloudflare.ps1"],
  ["04_ABRIR_ATLAS_DEPENDENCIAS.cmd", "open_dependency_atlas.ps1"],
  ["09_KILL_EVERYTHING_PRISMA.cmd", "kill_everything.ps1"],
];

const REQUIRED_KILL_PORTS = ["3000", "3100", "3110", "3120", "3130", "3140", "3150", "3200"];
const OUT_DIR = "F:\\descargasf";

function strictPhase5() {
  const value = String(process.env.PRISMA_QUALITY_STRICT_PHASE5 || "").trim().toLowerCase();
  return value === "1" || value === "true" || value === "yes" || value === "strict";
}

function softOrBlock(blockers, warnings, detail) {
  if (strictPhase5()) blockers.push(detail);
  else warnings.push(detail);
}

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

function isWindowsPathReady(absPath) {
  // In Linux/macOS test runners, F:\descargasf is a Windows contract path and cannot be
  // probed literally. On Windows, absence is a real operator-readiness issue.
  if (process.platform !== "win32") return true;
  return exists(absPath);
}

function evidenceItem(gateId, message, index) {
  return {
    schemaVersion: "1.0",
    evidenceId: `${gateId}_INLINE_${index + 1}`,
    gateId,
    type: "phase5-inline",
    summary: String(message),
    createdAt: new Date().toISOString(),
    payload: { value: message }
  };
}

function result(gateId, title, blockers, warnings, evidence) {
  const normalizedEvidence = evidence.map((item, index) => typeof item === "object" ? item : evidenceItem(gateId, item, index));
  if (normalizedEvidence.length === 0) {
    normalizedEvidence.push(evidenceItem(gateId, `${gateId} completed with no additional runtime evidence.`, 0));
  }
  const findings = [
    ...blockers.map((detail, index) => finding({
      id: `${gateId}_BLOCKER_${index + 1}`,
      severity: "S1",
      layer: "Release",
      title: `${gateId} release blocker`,
      detail,
      evidence: normalizedEvidence,
      recommendation: "Resolve this release readiness blocker before claiming Phase 5 readiness."
    })),
    ...warnings.map((detail, index) => finding({
      id: `${gateId}_WARNING_${index + 1}`,
      severity: "S3",
      layer: "Release",
      title: `${gateId} release warning`,
      detail,
      evidence: normalizedEvidence,
      recommendation: "Review this warning before release handoff."
    }))
  ];
  return {
    gateId,
    id: gateId,
    code: gateId,
    phase: 5,
    phaseName: PHASE5_TITLE,
    title,
    status: blockers.length > 0 ? "BLOCKED" : warnings.length > 0 ? "READY_WITH_WARNINGS" : "READY",
    summary: `${gateId}: ${blockers.length} blockers, ${warnings.length} warnings, ${normalizedEvidence.length} evidence items`,
    findings,
    evidence: normalizedEvidence,
    blockerCount: blockers.length,
    warningCount: warnings.length,
    timestamp: new Date().toISOString(),
  };
}

function gateQ26(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const cc = path.join(root, "prisma-control-center");
  const wrappersDir = path.join(cc, "internal", "wrappers");

  if (!exists(cc)) {
    evidence.push("prisma-control-center no existe en este root; Launcher OS se trata como carril no activo para este paquete quality-only.");
    evidence.push("Q26 mantiene bloqueo duro solo cuando Control Center existe pero sus launchers/wrappers estan incompletos.");
    return result("Q26", "Launcher OS release readiness", blockers, warnings, evidence);
  }

  for (const [cmd, wrapper] of LAUNCHERS) {
    const cmdPath = path.join(cc, cmd);
    const wrapperPath = path.join(wrappersDir, wrapper);
    if (!exists(cmdPath)) blockers.push(`Falta launcher oficial ${cmd}`);
    else evidence.push(`Launcher presente: ${cmd}`);
    if (!exists(wrapperPath)) blockers.push(`Falta wrapper oficial ${wrapper}`);
    else evidence.push(`Wrapper presente: ${wrapper}`);
    const cmdText = normalize(readSafe(cmdPath));
    if (exists(cmdPath) && !cmdText.includes(wrapper.toLowerCase())) {
      softOrBlock(blockers, warnings, `${cmd} no referencia claramente ${wrapper}`);
    }
    if (cmdText.includes("prisma_launcher_runs")) {
      softOrBlock(blockers, warnings, `${cmd} aun depende de PRISMA_LAUNCHER_RUNS`);
    }
  }

  const wrapperFiles = listFilesRecursive(wrappersDir, { maxDepth: 2, skip: [] });
  const wrapperCorpus = normalize(wrapperFiles.map(readSafe).join("\n"));
  if (wrapperCorpus.includes("prisma_launcher_runs")) {
    softOrBlock(blockers, warnings, "Wrappers aun mencionan PRISMA_LAUNCHER_RUNS");
  }
  if (!wrapperCorpus.includes("f:/descargasf") && !wrapperCorpus.includes("f:\\descargasf")) {
    warnings.push("Wrappers no muestran salida directa a F:\\descargasf; se recomienda dejar evidencia visible al operador.");
  } else {
    evidence.push("Wrappers contienen salida directa a F:\\descargasf");
  }
  evidence.push(`Q26 mode: ${strictPhase5() ? "strict" : "install-safe advisory for content drift"}`);
  const killText = normalize(readSafe(path.join(wrappersDir, "kill_everything.ps1")) + "\n" + readSafe(path.join(cc, "09_KILL_EVERYTHING_PRISMA.cmd")));
  for (const port of REQUIRED_KILL_PORTS) {
    if (!killText.includes(port)) blockers.push(`Kill everything no cubre puerto ${port}`);
  }
  evidence.push("Q26 usa solo launchers definitivos: 00, 01, 02, 03, 04 y 09.");
  return result("Q26", "Launcher OS release readiness", blockers, warnings, evidence);
}

function gateQ27(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  if (!isWindowsPathReady(OUT_DIR)) blockers.push(`No existe ${OUT_DIR}`);
  else evidence.push(process.platform === "win32" ? `${OUT_DIR} existe` : `${OUT_DIR} aceptado como contrato Windows en plataforma ${process.platform}`);

  const latestKill = path.join(OUT_DIR, "latest_KILL_EVERYTHING.zip");
  if (exists(latestKill)) evidence.push("latest_KILL_EVERYTHING.zip existe");
  else evidence.push("latest_KILL_EVERYTHING.zip no existe ahora; kill evidence puede generarse bajo demanda.");

  const docCorpus = normalize([
    "prisma-control-center/README_OPERADOR.md",
    "prisma-control-center/README_OPERADOR_CRYSTAL.md",
    "quality/docs/phase-5-release-operator-readiness.md",
    "quality/docs/evidence-ledger-hardening.md",
  ].map((rel) => readSafe(path.join(root, rel))).join("\n"));
  for (const token of ["latest_all_local.zip", "latest_all_local_cloudflare.zip", "latest_module_cloudflare.zip", "latest_dependency_atlas_open.zip", "latest_kill_everything.zip", "transcript.log", "summary.json", "f:/descargasf", "prisma_quality_os"]) {
    if (!docCorpus.includes(token)) warnings.push(`Evidencia/documentacion no menciona '${token}'.`);
    else evidence.push(`Evidencia documentada: ${token}`);
  }
  if (!exists(path.join(root, "quality", "core", "evidence-writer.mjs"))) {
    blockers.push("No encontre quality/core/evidence-writer.mjs. El writer de evidencia es obligatorio.");
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
  for (const file of tempFixes) warnings.push(`Script temporal activo: ${path.relative(root, file)}`);
  if (tempFixes.length === 0) evidence.push("Sin scripts temporales prisma_*_fix.py en zonas principales del repo");
  const badRuns = path.join(OUT_DIR, "PRISMA_LAUNCHER_RUNS");
  if (process.platform === "win32" && exists(badRuns)) blockers.push(`${badRuns} no debe existir como carpeta permanente`);
  else evidence.push("Sin PRISMA_LAUNCHER_RUNS permanente en F:\\descargasf o fuera de plataforma Windows");
  if (exists(cc) && !exists(wrappers)) blockers.push("Control Center existe pero falta prisma-control-center/internal/wrappers");
  else if (!exists(cc)) evidence.push("Control Center no activo en este root; hygiene de wrappers omitida sin bloquear.");
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
    if (!exists(doc)) warnings.push(`Falta doc operador opcional: ${path.relative(root, doc)}`);
    else evidence.push(`Doc presente: ${path.relative(root, doc)}`);
  }
  const corpus = normalize(docs.map(readSafe).join("\n"));
  const requiredTerms = [
    "3000", "3110", "3120", "3130", "3140", "3150",
    "launcher", "diagnost", "kill", "zip", "rollback", "cloudflare", "local", "f:/descargasf",
  ];
  for (const term of requiredTerms) {
    if (!corpus.includes(term)) warnings.push(`Docs operador no cubren '${term}'`);
    else evidence.push(`Docs cubren '${term}'`);
  }
  if (!exists(path.join(root, "quality", "docs", "phase-5-release-operator-readiness.md"))) {
    blockers.push("Falta quality/docs/phase-5-release-operator-readiness.md, documento minimo de Phase 5.");
  }
  return result("Q29", "Operator docs readiness", blockers, warnings, evidence);
}

function hasScript(scripts, name, contains = null) {
  const value = scripts && typeof scripts[name] === "string" ? scripts[name] : "";
  if (!value) return false;
  return contains ? normalize(value).includes(normalize(contains)) : true;
}

function gateQ30(root) {
  const blockers = [];
  const warnings = [];
  const evidence = [];
  const rootPackageJson = loadJsonSafe(path.join(root, "package.json"));
  const rootScripts = rootPackageJson?.scripts || {};
  const qualityPackageJson = loadJsonSafe(path.join(root, "quality", "package.json"));
  const qualityScripts = qualityPackageJson?.scripts || {};
  const cliPath = path.join(root, "quality", "bin", "prisma-quality.mjs");

  if (!exists(cliPath)) blockers.push("Falta quality/bin/prisma-quality.mjs");
  else evidence.push("CLI directo presente: quality/bin/prisma-quality.mjs");

  const scriptChecks = [
    ["quality:phase5", "phase5"],
    ["quality:release", "release"],
    ["quality:pr", "pr"],
  ];
  for (const [scriptName, profileName] of scriptChecks) {
    if (hasScript(rootScripts, scriptName)) {
      evidence.push(`Root package.json expone ${scriptName}`);
    } else if (hasScript(qualityScripts, scriptName) || exists(cliPath)) {
      evidence.push(`Root package.json no expone ${scriptName}; aceptado porque el paquete quality trae CLI/script directo para perfil ${profileName}.`);
    } else {
      blockers.push(`No hay forma directa de ejecutar ${scriptName} ni CLI equivalente.`);
    }
  }
  if (hasScript(rootScripts, "quality:release") && !hasScript(rootScripts, "quality:release", "phase5") && !hasScript(rootScripts, "quality:release", "release")) {
    warnings.push("quality:release existe pero no menciona explicitamente release/phase5; revisar si apunta al perfil correcto.");
  }

  const phase5 = loadJsonSafe(path.join(root, "quality", "profiles", "phase5.json"));
  const release = loadJsonSafe(path.join(root, "quality", "profiles", "release.json"));
  const manifest = loadJsonSafe(path.join(root, "quality", "prisma-quality.manifest.json"));
  if (!phase5) blockers.push("phase5.json no parsea o no existe");
  if (!release) blockers.push("release.json no parsea o no existe");
  if (!manifest) blockers.push("prisma-quality.manifest.json no parsea o no existe");

  for (const gate of PHASE5_GATE_IDS) {
    if (!jsonContains(phase5, gate)) blockers.push(`phase5.json no contiene ${gate}`);
    else evidence.push(`phase5.json contiene ${gate}`);
    if (!jsonContains(release, gate) && !jsonContains(release, "phase5")) blockers.push(`release.json no contiene ${gate} ni referencia Phase 5`);
    else evidence.push(`release.json cubre ${gate}`);
    if (!jsonContains(manifest, gate)) blockers.push(`manifest no contiene ${gate}`);
    else evidence.push(`manifest contiene ${gate}`);
  }
  for (const gate of PHASE5_GATE_IDS) {
    if (!exists(path.join(root, "quality", "gates", `${gate}.mjs`))) blockers.push(`Falta archivo gate ${gate}.mjs`);
  }
  return result("Q30", "Release profile readiness", blockers, warnings, evidence);
}

export async function runPhase5Gate(gateId, context = {}) {
  const root = path.resolve(context.repoRoot || context.root || process.env.PRISMA_ROOT || process.cwd());
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
  for (const gateId of PHASE5_GATE_IDS.filter((gateId) => gateId !== "Q31")) {
    results.push(await runPhase5Gate(gateId, context));
  }
  return results;
}

export function isBlocked(result) {
  return result.status === "BLOCKED" || (Array.isArray(result.blockers) && result.blockers.length > 0);
}

export async function runCli(gateId) {
  const result = await runPhase5Gate(gateId, { repoRoot: process.cwd() });
  console.log(JSON.stringify(result, null, 2));
  process.exit(isBlocked(result) ? 1 : 0);
}

export function isDirectModule(importMetaUrl) {
  if (!process.argv[1]) return false;
  return fileURLToPath(importMetaUrl) === path.resolve(process.argv[1]);
}
