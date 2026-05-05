#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const out = {
    root: process.cwd(),
    baseUrl: process.env.PRISMA_VOS_BASE_URL || "http://127.0.0.1:3120",
    out: process.env.PRISMA_VOS_OUTPUT_DIR || "F:/descargasf/prisma-visual-os/00c",
    screens: null,
    headful: false,
  };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--root") out.root = argv[++i];
    else if (arg === "--base-url") out.baseUrl = argv[++i];
    else if (arg === "--out") out.out = argv[++i];
    else if (arg === "--screens") out.screens = argv[++i].split(",").map((s) => s.trim()).filter(Boolean);
    else if (arg === "--headful") out.headful = true;
  }
  return out;
}

function slug(s) { return String(s).replace(/[^a-z0-9_-]+/gi, "_").replace(/^_+|_+$/g, "").toLowerCase(); }
function ts() { return new Date().toISOString().replace(/[:.]/g, "-"); }
function joinUrl(base, route) { return new URL(route, base.endsWith("/") ? base : `${base}/`).toString(); }

const args = parseArgs(process.argv);
const root = path.resolve(args.root);
const configPath = path.join(root, "products/shared-ui/prisma/visual-os/prisma-visual-os.golden-screens.00c.json");
if (!fs.existsSync(configPath)) {
  console.error(`[VOS 00C CAPTURE] No existe config: ${configPath}`);
  process.exit(1);
}

let playwright;
try {
  playwright = await import("playwright");
} catch (error) {
  console.error("[VOS 00C CAPTURE] Falta Playwright. Instala dependencias del repo o agrega playwright al entorno de desarrollo.");
  console.error("[VOS 00C CAPTURE] Este arnés no cambia archivos; sólo captura evidencia cuando la app local ya está arriba.");
  console.error(String(error?.message || error));
  process.exit(2);
}

const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
const allScreens = Array.isArray(config.screens) ? config.screens : [];
const selected = args.screens ? allScreens.filter((s) => args.screens.includes(s.id)) : allScreens;
if (!selected.length) {
  console.error("[VOS 00C CAPTURE] No hay screens seleccionadas.");
  process.exit(1);
}

const runDir = path.join(args.out, ts());
fs.mkdirSync(runDir, { recursive: true });
const browser = await playwright.chromium.launch({ headless: !args.headful });
const manifest = {
  package: "PRISMA_VISUAL_OS_POS_GOLDEN_QA_00C_20260503_v01",
  createdAt: new Date().toISOString(),
  root,
  baseUrl: args.baseUrl,
  runDir,
  screens: [],
};

try {
  for (const screen of selected) {
    const context = await browser.newContext({
      viewport: screen.viewport || { width: 1365, height: 768 },
      reducedMotion: config.defaults?.reducedMotion || "reduce",
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const consoleEvents = [];
    page.on("console", (msg) => {
      if (["error", "warning"].includes(msg.type())) consoleEvents.push({ type: msg.type(), text: msg.text() });
    });
    const url = joinUrl(args.baseUrl, screen.route || "/pos");
    const entry = { id: screen.id, route: screen.route, url, viewport: screen.viewport, ok: false, screenshot: null, errors: [] };
    try {
      await page.goto(url, { waitUntil: config.defaults?.waitUntil || "networkidle", timeout: config.defaults?.timeoutMs || 30000 });
      if (screen.requiredSelector) await page.waitForSelector(screen.requiredSelector, { timeout: 5000 });
      await page.emulateMedia({ reducedMotion: "reduce" });
      const screenshot = path.join(runDir, `${slug(screen.id)}.png`);
      await page.screenshot({ path: screenshot, fullPage: true });
      entry.ok = true;
      entry.screenshot = screenshot;
    } catch (error) {
      entry.errors.push(String(error?.message || error));
    } finally {
      entry.console = consoleEvents;
      manifest.screens.push(entry);
      await context.close();
      console.log(`[VOS 00C CAPTURE] ${entry.ok ? "OK" : "FAIL"} ${screen.id} -> ${entry.screenshot || entry.errors.join(" | ")}`);
    }
  }
} finally {
  await browser.close();
}

const manifestPath = path.join(runDir, "prisma_visual_os_pos_golden_00c_manifest.json");
fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2), "utf8");
console.log(`[VOS 00C CAPTURE] manifest=${manifestPath}`);
if (manifest.screens.some((s) => !s.ok)) process.exit(1);
