import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(toolDir, "..");
const repoRoot = path.resolve(appRoot, "../../../../..");
const runtimeRoot = path.join(appRoot, "generated", "prisma-visual-runtime");
const authorityRoot = path.join(repoRoot, "prisma-html", "authority", "rifat");
const canonicalUiRoot = path.join(authorityRoot, "prisma-ui");
const generatedUiRoot = path.join(repoRoot, "apps", "terminal-de-venta-system", ".prisma-ui");
const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex");
const read = (file) => fs.readFileSync(file);
const readText = (file) => fs.readFileSync(file, "utf8");
const readJson = (file) => JSON.parse(readText(file));
const relRepo = (file) => path.relative(repoRoot, file).replace(/\\/g, "/");

function walk(dir, predicate = () => true) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const absolute = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(absolute, predicate) : predicate(absolute) ? [absolute] : [];
  });
}

function routeFromPage(file) {
  const relative = path.relative(path.join(appRoot, "app"), file).replace(/\\/g, "/");
  if (relative === "page.tsx") return "/";
  return `/${relative.replace(/\/page\.tsx$/, "")}`;
}

function resolveImport(specifier, importer) {
  let base = null;
  if (specifier.startsWith("@components/")) base = path.join(appRoot, "components", specifier.slice("@components/".length));
  else if (specifier.startsWith("@generated/")) base = path.join(appRoot, "generated", specifier.slice("@generated/".length));
  else if (specifier.startsWith("@/")) base = path.join(appRoot, specifier.slice(2));
  else if (specifier.startsWith(".")) base = path.resolve(path.dirname(importer), specifier);
  if (!base) return null;
  const candidates = [
    base,
    `${base}.ts`,
    `${base}.tsx`,
    `${base}.js`,
    `${base}.jsx`,
    path.join(base, "index.ts"),
    path.join(base, "index.tsx")
  ];
  return candidates.find((candidate) => fs.existsSync(candidate) && fs.statSync(candidate).isFile()) ?? null;
}

function buildReachability() {
  const codeFiles = walk(appRoot, (file) => /\.(?:tsx?|jsx?)$/.test(file));
  const pageFiles = walk(path.join(appRoot, "app"), (file) => file.endsWith("page.tsx") && !file.replace(/\\/g, "/").includes("/api/"));
  const entryFiles = [
    ...pageFiles,
    ...["layout.tsx", "error.tsx", "not-found.tsx"].map((name) => path.join(appRoot, "app", name)).filter(fs.existsSync)
  ];
  const queue = [...entryFiles];
  const reachableCode = new Set();
  const reachableCss = new Set();
  const importPattern = /(?:import|export)\s+(?:[\s\S]*?\s+from\s+)?["']([^"']+)["']/g;

  while (queue.length) {
    const file = queue.shift();
    if (reachableCode.has(file)) continue;
    reachableCode.add(file);
    const text = readText(file);
    for (const match of text.matchAll(importPattern)) {
      const specifier = match[1];
      if (specifier.endsWith(".css")) {
        const resolvedCss = resolveImport(specifier, file) ?? path.resolve(path.dirname(file), specifier);
        if (fs.existsSync(resolvedCss)) reachableCss.add(resolvedCss);
        continue;
      }
      const resolved = resolveImport(specifier, file);
      if (resolved) queue.push(resolved);
    }
  }
  return { codeFiles, pageFiles, reachableCode, reachableCss };
}

const checks = [];
function check(id, passed, details) {
  checks.push({ id, passed: Boolean(passed), details });
}

const lockPath = path.join(runtimeRoot, "authority-lock.json");
const manifestPath = path.join(runtimeRoot, "runtime-manifest.json");
const lock = readJson(lockPath);
const manifestBytes = read(manifestPath);
const manifest = JSON.parse(manifestBytes);
check("lock.authority", lock.authority_repo === "hitech-os-prisma-html/prisma-html" && /^[0-9a-f]{40}$/.test(lock.authority_commit), lock);
check("lock.manifest-sha", sha256(manifestBytes) === lock.manifest_sha256, { expected: lock.manifest_sha256, actual: sha256(manifestBytes) });
check("lock.generated", lock.generated === true && lock.manual_edits_forbidden === true, { generated: lock.generated, manual_edits_forbidden: lock.manual_edits_forbidden });

const fileDrift = manifest.files.flatMap((entry) => {
  const absolute = path.join(repoRoot, entry.path);
  if (!fs.existsSync(absolute)) return [{ path: entry.path, issue: "missing" }];
  const content = read(absolute);
  if (content.length !== entry.bytes) return [{ path: entry.path, issue: "byte-count", expected: entry.bytes, actual: content.length }];
  const actual = sha256(content);
  return actual === entry.sha256 ? [] : [{ path: entry.path, issue: "sha256", expected: entry.sha256, actual }];
});
check("manifest.hash-integrity", fileDrift.length === 0, fileDrift);

const routeBindings = readJson(path.join(runtimeRoot, "route-bindings.json"));
const reachability = buildReachability();
const detectedRoutes = reachability.pageFiles.map(routeFromPage).sort();
const boundRoutes = routeBindings.routes.map((row) => row.route).sort();
check("routes.detected", detectedRoutes.length === 23 && detectedRoutes.join("|") === boundRoutes.join("|"), { detectedRoutes, boundRoutes });
check("routes.customer-visible", routeBindings.customerVisible === 22, { customerVisible: routeBindings.customerVisible });
check("routes.state-coverage", routeBindings.routes.filter((row) => !row.internal).every((row) => row.states.length > 0), {
  empty: routeBindings.routes.filter((row) => !row.internal && row.states.length === 0).map((row) => row.route)
});

const layoutText = readText(path.join(appRoot, "app", "layout.tsx"));
check("runtime.single-global-import", layoutText.includes("../generated/prisma-visual-runtime/prisma-tablet-runtime.css") && !layoutText.includes("./globals.css") && !layoutText.includes("nocturne-canonical.css"), {
  generatedImport: layoutText.includes("../generated/prisma-visual-runtime/prisma-tablet-runtime.css")
});
check("runtime.generated-token-import", layoutText.includes("../generated/prisma-visual-runtime/visual-values") && layoutText.includes("prisma-runtime-root.module.css"), {});

const reachableCssDetails = [...reachability.reachableCss].sort().map((file) => ({
  path: relRepo(file),
  generated: readText(file).includes("@generated by prisma-html/tools/generate_tablet_visual_runtime.py")
}));
check("runtime.css-generated", reachableCssDetails.every((row) => row.generated), reachableCssDetails.filter((row) => !row.generated));

const liveCss = [
  ...walk(path.join(appRoot, "app"), (file) => file.endsWith(".css")),
  ...walk(path.join(appRoot, "components"), (file) => file.endsWith(".css")),
  ...walk(runtimeRoot, (file) => file.endsWith(".css"))
];
const importantHits = liveCss.flatMap((file) => readText(file).includes("!important") ? [relRepo(file)] : []);
check("runtime.zero-important", importantHits.length === 0, importantHits);

const legacyPaths = [
  "app/globals.css",
  "app/prisma-tablet-nocturne-canonical.css",
  "app/prisma-tablet-background-workbench.css",
  "app/prisma-tablet-light-premium-final.css",
  "app/prisma-tablet-light-shell.module.css",
  "app/prisma-tablet-premium-governed.css",
  "components/prisma-dark-pos",
  "components/tablet-visual-v2",
  "components/premium-visual",
  "components/operational-screen",
  "components/visual-os",
  "public/visual-os"
];
const existingLegacy = legacyPaths.filter((relative) => fs.existsSync(path.join(appRoot, relative)));
check("legacy.paths-retired", existingLegacy.length === 0, existingLegacy);

const runtimeCode = [...reachability.reachableCode].map((file) => ({ file, text: readText(file) }));
const legacyReferencePattern = /(?:components\/prisma-dark-pos|components\/tablet-visual-v2|components\/premium-visual|public\/visual-os|prisma-tablet-nocturne-canonical\.css)/;
const legacyReferences = runtimeCode.flatMap(({ file, text }) => legacyReferencePattern.test(text) ? [relRepo(file)] : []);
check("legacy.runtime-references", legacyReferences.length === 0, legacyReferences);

const canonicalUiFiles = walk(canonicalUiRoot, (file) => file.endsWith(".json"));
const uiDrift = canonicalUiFiles.flatMap((source) => {
  const relative = path.relative(canonicalUiRoot, source);
  const output = path.join(generatedUiRoot, relative);
  if (!fs.existsSync(output)) return [{ path: relative.replace(/\\/g, "/"), issue: "missing" }];
  return read(source).equals(read(output)) ? [] : [{ path: relative.replace(/\\/g, "/"), issue: "drift" }];
});
check("authority.single-prisma-ui", uiDrift.length === 0, uiDrift);

const localPathHits = walk(runtimeRoot, (file) => /\.(?:json|css|ts|tsx)$/.test(file)).flatMap((file) =>
  /[A-Za-z]:\\/.test(readText(file)) ? [relRepo(file)] : []
);
check("runtime.no-local-paths", localPathHits.length === 0, localPathHits);

const secretHits = walk(runtimeRoot, (file) => /\.(?:json|css|ts|tsx)$/.test(file)).flatMap((file) =>
  /(?:sk-[A-Za-z0-9_-]{20,}|BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|api[_-]?token\s*[:=]\s*["'][^"']+)/i.test(readText(file)) ? [relRepo(file)] : []
);
check("runtime.no-secrets", secretHits.length === 0, secretHits);

const passed = checks.every((item) => item.passed);
const result = {
  status: passed ? "PASS" : "FAIL",
  task: "RIFAT Atlas centralization and Tablet migration",
  authorityCommit: lock.authority_commit,
  visualRuntimeVersion: lock.visual_runtime_version,
  manifestSha256: lock.manifest_sha256,
  routesDetected: detectedRoutes.length,
  routesMigrated: boundRoutes.length,
  customerVisibleRoutes: routeBindings.customerVisible,
  reachableCssFiles: reachableCssDetails.length,
  importantCount: importantHits.length,
  legacyPaths: existingLegacy.length,
  legacyRuntimeReferences: legacyReferences.length,
  checks
};
console.log(JSON.stringify(result, null, 2));
if (!passed) process.exitCode = 1;
