import fs from "node:fs";
import path from "node:path";
import { fail, pass, rel, warn, writeEvidence } from "./chart-lab-script-utils.mjs";

const outDir = rel("out");
const rules = [
  { severity: "fail", pattern: /F:\\/i, label: "Windows absolute drive path" },
  { severity: "fail", pattern: /DATABASE_URL\s*[:=]\s*["'][^"']+/i, label: "DATABASE_URL value" },
  { severity: "fail", pattern: /CLOUDFLARE_API_TOKEN\s*[:=]\s*["'][^"']+/i, label: "Cloudflare token value" },
  { severity: "warn", pattern: /\.env(?:\.local|\.production|\.development)?(?:\s|["'<])/i, label: "benign env filename string" },
  { severity: "fail", pattern: /BEGIN PRIVATE KEY/i, label: "private key block" },
  { severity: "fail", pattern: /cloudflared.+credentials/i, label: "cloudflared credentials" },
  { severity: "fail", pattern: /C:\\Users\\[^\\]+\\.cloudflared/i, label: "local cloudflared path" },
  { severity: "fail", pattern: /\b(?:SECRET|TOKEN|PRIVATE_KEY)\s*[:=]\s*["'][A-Za-z0-9_./+=-]{16,}["']/i, label: "secret-like assignment" }
];
const allowedLocalhostFiles = new Set();
const findings = [];

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(absolute);
    else {
      const ext = path.extname(entry.name).toLowerCase();
      if (![".html", ".js", ".css", ".json", ".txt", ".svg", ".map"].includes(ext)) continue;
      const content = fs.readFileSync(absolute, "utf8");
      for (const rule of rules) {
        if (rule.pattern.test(content)) findings.push({ file: path.relative(outDir, absolute), pattern: String(rule.pattern), severity: rule.severity, label: rule.label });
      }
      if (!allowedLocalhostFiles.has(path.relative(outDir, absolute)) && /https?:\/\/(?:localhost|127\.0\.0\.1)|(?:localhost|127\.0\.0\.1):\d+/i.test(content)) {
        findings.push({ file: path.relative(outDir, absolute), pattern: "local origin URL", severity: "fail", label: "local origin URL" });
      }
    }
  }
}

if (!fs.existsSync(outDir)) {
  fail("out directory is missing; run chart-lab:cf:build before no-leak verification");
} else {
  walk(outDir);
}

writeEvidence("no-leak-report.json", { outDir, findings });

const failFindings = findings.filter((item) => item.severity === "fail");
const warnFindings = findings.filter((item) => item.severity === "warn");
if (failFindings.length) fail(`public build leak scan found ${failFindings.length} failing issue(s)`);
else if (warnFindings.length) {
  warn(`public build leak scan found ${warnFindings.length} warning(s), no secret values`);
  pass("public build leak scan passed with warnings");
} else pass("public build leak scan passed");
