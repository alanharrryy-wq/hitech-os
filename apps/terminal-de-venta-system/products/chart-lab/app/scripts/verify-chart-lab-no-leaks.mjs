import fs from "node:fs";
import path from "node:path";
import { fail, pass, rel, writeEvidence } from "./chart-lab-script-utils.mjs";

const outDir = rel("out");
const denied = [
  /F:\\/i,
  /DATABASE_URL/i,
  /CLOUDFLARE_API_TOKEN/i,
  /\.env/i,
  /BEGIN PRIVATE KEY/i,
  /cloudflared.+credentials/i,
  /C:\\Users\\[^\\]+\\.cloudflared/i
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
      for (const pattern of denied) {
        if (pattern.test(content)) findings.push({ file: path.relative(outDir, absolute), pattern: String(pattern) });
      }
      if (!allowedLocalhostFiles.has(path.relative(outDir, absolute)) && /localhost|127\.0\.0\.1/i.test(content)) {
        findings.push({ file: path.relative(outDir, absolute), pattern: "localhost/127.0.0.1" });
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

if (findings.length) fail(`public build leak scan found ${findings.length} issue(s)`);
else pass("public build leak scan passed");
