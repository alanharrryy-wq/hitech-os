#!/usr/bin/env node
import fs from "node:fs";
import { exists, pass, rel, run, warn, writeEvidence } from "./chart-lab-script-utils.mjs";

const publicUrl = process.argv.includes("--public-url") ? process.argv[process.argv.indexOf("--public-url") + 1] : null;
const report = { generatedAt: new Date().toISOString(), publicUrl, checks: [] };

function check(status, message, detail = null) {
  report.checks.push({ status, message, detail });
  if (status === "PASS") pass(message);
  else warn(message);
}

const cf = run("node", ["scripts/verify-chart-lab-cloudflare.mjs"]);
check(cf.status === 0 ? "PASS" : "WARN", "existing Cloudflare verifier executed", { status: cf.status });

if (exists("out/index.html")) {
  const html = fs.readFileSync(rel("out", "index.html"), "utf8");
  check(html.includes("__next") || html.includes("PRISMA") || html.includes("Chart") ? "PASS" : "WARN", "out/index.html contains app marker");
  const leaks = run("node", ["scripts/verify-chart-lab-no-leaks.mjs"]);
  check(leaks.status === 0 ? "PASS" : "WARN", "no-leak scanner executed", { status: leaks.status });
} else {
  check("WARN", "out/index.html missing; run cf:build before static smoke");
}

if (publicUrl) {
  try {
    const response = await fetch(publicUrl, { redirect: "follow" });
    const text = await response.text();
    check(response.ok ? "PASS" : "WARN", `public URL status ${response.status}`, { url: publicUrl });
    check(/PRISMA|Chart|__next/i.test(text) ? "PASS" : "WARN", "public URL contains app marker", { url: publicUrl });
  } catch (error) {
    check("WARN", "public URL fetch failed", { url: publicUrl, error: String(error?.message || error) });
  }
}

const reportPath = writeEvidence("cloudflare-smoke-report.json", report);
console.log(`cloudflare smoke report: ${reportPath}`);
