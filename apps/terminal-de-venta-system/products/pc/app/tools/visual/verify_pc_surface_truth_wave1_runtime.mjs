#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { chromium } from "@playwright/test";

const configPath = path.resolve(process.argv[2] || "pc-surface-truth-wave1-routes.json");
const outDir = path.resolve(process.argv[3] || "pc-surface-truth-wave1-runtime-results");
const cfg = JSON.parse(fs.readFileSync(configPath, "utf8"));
const baseUrl = String(process.env.PRISMA_PC_VISUAL_URL || cfg.baseUrl || "http://127.0.0.1:3130").replace(/\/$/, "");
const appRoot = process.cwd();
fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(path.join(outDir, "screenshots"), { recursive: true });
fs.mkdirSync(path.join(outDir, "html"), { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, reducedMotion: "reduce" });
const results = [];

function slug(route) { return route.replace(/^\//, "").replace(/[^a-zA-Z0-9_-]+/g, "_") || "root"; }
function pathOnly(url) { try { return new URL(url).pathname; } catch { return ""; } }
function routeSource(route) {
  const parts = route.replace(/^\/+|\/+$/g, "").split("/").filter(Boolean);
  const file = path.join(appRoot, "app", ...parts, "page.tsx");
  return { file, text: fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "" };
}
function sourceCallsRedirect(source, target) {
  return source.includes(`redirect("${target}")`) || source.includes(`redirect('${target}')`) || source.includes(`redirect(\`${target}\`)`);
}
function containsAll(text, tokens = []) {
  const haystack = String(text).toLowerCase();
  return tokens.length > 0 && tokens.every(token => haystack.includes(String(token).toLowerCase()));
}

for (const entry of cfg.routes) {
  const page = await context.newPage();
  const consoleMessages = [];
  const pageErrors = [];
  page.on("console", msg => { if (["error", "warning"].includes(msg.type())) consoleMessages.push({ type: msg.type(), text: msg.text().slice(0, 1000) }); });
  page.on("pageerror", err => pageErrors.push(String(err?.message || err).slice(0, 1500)));
  let responseStatus = 0;
  let finalUrl = "";
  let text = "";
  let htmlText = "";
  let smartDropdownCount = 0;
  let status = "PASS";
  const checks = [];
  try {
    const source = routeSource(entry.route);
    if (entry.mode === "redirect") {
      checks.push({
        id: "source-redirect-contract",
        pass: sourceCallsRedirect(source.text, entry.target),
        detail: `${path.relative(appRoot, source.file)} -> ${entry.target}`
      });
    }
    if (entry.mode === "not_found") {
      checks.push({
        id: "source-not-found-contract",
        pass: source.text.includes("notFound()"),
        detail: path.relative(appRoot, source.file)
      });
    }

    const response = await page.goto(baseUrl + entry.route, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForLoadState("networkidle", { timeout: 15000 }).catch(() => {});

    if (entry.mode === "redirect") {
      const expectedTokens = entry.expectedText || [];
      if (expectedTokens.length > 0) {
        await page.waitForFunction(
          tokens => {
            const haystack = String(document.body?.innerText || "").toLowerCase();
            return tokens.every(token => haystack.includes(String(token).toLowerCase()));
          },
          expectedTokens,
          { timeout: 15000 }
        ).catch(() => {});
      } else {
        await page.waitForURL(
          url => url.pathname === entry.target,
          { timeout: 15000 }
        ).catch(() => {});
      }
    }

    await page.waitForTimeout(500);
    responseStatus = response?.status() || 0;
    finalUrl = page.url();
    text = await page.locator("body").innerText().catch(() => "");
    htmlText = await page.content();
    smartDropdownCount = await page.locator('[data-prisma-component="SmartDropdownDock"]').count();

    if (entry.mode === "not_found") {
      const nextNotFoundMeta = /<meta[^>]+name=["']next-error["'][^>]+content=["']not-found["']/i.test(htmlText)
        || /<meta[^>]+content=["']not-found["'][^>]+name=["']next-error["']/i.test(htmlText);
      const visibleNotFound = /\b404\b/.test(text) && /not found|could not be found/i.test(text);
      checks.push({
        id: "runtime-not-found-semantic",
        pass: responseStatus === 404 || nextNotFoundMeta || visibleNotFound,
        detail: `status=${responseStatus} meta=${nextNotFoundMeta} visible404=${visibleNotFound}`
      });
    } else if (entry.mode === "redirect") {
      const urlReachedTarget = pathOnly(finalUrl) === entry.target;
      const canonicalTargetRendered = containsAll(text, entry.expectedText || []);
      checks.push({
        id: "runtime-redirect-semantic",
        pass: urlReachedTarget || canonicalTargetRendered,
        detail: `final=${pathOnly(finalUrl)} expected=${entry.target} canonicalTargetRendered=${canonicalTargetRendered}`
      });
    } else {
      checks.push({ id: "render-status", pass: responseStatus >= 200 && responseStatus < 400, detail: `status=${responseStatus}` });
    }

    if (entry.mode !== "not_found" && cfg.forbidSmartDropdownOnCustomerRoutes) {
      checks.push({ id: "no-smart-dropdown", pass: smartDropdownCount === 0, detail: `count=${smartDropdownCount}` });
    }
    for (const token of entry.expectedText || []) {
      checks.push({ id: `expected:${token}`, pass: text.toLowerCase().includes(String(token).toLowerCase()), detail: token });
    }
    for (const token of cfg.bannedLegacyText || []) {
      checks.push({ id: `banned:${token}`, pass: !text.includes(token), detail: token });
    }
    checks.push({ id: "no-page-errors", pass: pageErrors.length === 0, detail: pageErrors.join(" | ") || "none" });

    const s = slug(entry.route);
    await page.screenshot({ path: path.join(outDir, "screenshots", `${s}.png`), fullPage: true });
    fs.writeFileSync(path.join(outDir, "html", `${s}.html`), htmlText, "utf8");
    if (checks.some(c => !c.pass)) status = entry.critical ? "FAIL" : "WARN";
  } catch (err) {
    status = entry.critical ? "FAIL" : "WARN";
    checks.push({ id: "runtime-exception", pass: false, detail: String(err?.message || err) });
  }
  results.push({ ...entry, status, responseStatus, finalUrl, smartDropdownCount, checks, consoleMessages, pageErrors });
  await page.close().catch(() => {});
}

await browser.close();
const summary = {
  status: results.some(r => r.status === "FAIL") ? "FAIL" : results.some(r => r.status === "WARN") ? "WARN" : "PASS",
  baseUrl,
  createdAt: new Date().toISOString(),
  pass: results.filter(r => r.status === "PASS").length,
  warn: results.filter(r => r.status === "WARN").length,
  fail: results.filter(r => r.status === "FAIL").length,
  results,
};
fs.writeFileSync(path.join(outDir, "SURFACE_TRUTH_RUNTIME_RESULT.json"), JSON.stringify(summary, null, 2), "utf8");
const md = [
  "# PC Surface Truth Wave 1 runtime gate",
  "",
  `**Status:** ${summary.status}`,
  `**PASS/WARN/FAIL:** ${summary.pass}/${summary.warn}/${summary.fail}`,
  "",
  ...results.flatMap(r => [
    `## ${r.status === "PASS" ? "✅" : r.status === "WARN" ? "⚠️" : "❌"} ${r.route} — ${r.status}`,
    `- mode: ${r.mode}`,
    `- final URL: ${r.finalUrl || "n/a"}`,
    `- HTTP: ${r.responseStatus || "n/a"}`,
    `- SmartDropdownDock: ${r.smartDropdownCount}`,
    ...r.checks.map(c => `- ${c.pass ? "✅" : "❌"} ${c.id}: ${c.detail}`),
    "",
  ])
];
fs.writeFileSync(path.join(outDir, "SURFACE_TRUTH_RUNTIME_SUMMARY.md"), md.join("\n"), "utf8");
process.exit(summary.status === "FAIL" ? 1 : 0);
