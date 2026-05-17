import fs from "node:fs";
import path from "node:path";
import { exists, fail, pass, read, rel, run, warn, writeEvidence } from "./chart-lab-script-utils.mjs";

const requiredFiles = [
  "wrangler.jsonc",
  "deploy/cloudflare-pages.json",
  "deploy/cloudflare-tunnel/prisma-chart-lab.tunnel.template.yml",
  "scripts/run-chart-lab-cf-build.mjs",
  "scripts/deploy-cloudflare-pages.mjs",
  "scripts/doctor-chart-lab-tunnel.ps1",
  "scripts/run-chart-lab-tunnel.ps1",
  "scripts/verify-chart-lab-no-leaks.mjs"
];

for (const file of requiredFiles) {
  if (exists(file)) pass(`Cloudflare file exists: ${file}`);
  else fail(`missing Cloudflare file: ${file}`);
}

const nextConfig = read("next.config.mjs");
for (const needle of ["PRISMA_CHART_LAB_STATIC_EXPORT", "output: \"export\"", "NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE"]) {
  if (nextConfig.includes(needle)) pass(`Next Cloudflare setting present: ${needle}`);
  else fail(`missing Next Cloudflare setting: ${needle}`);
}

const wranglerConfig = read("wrangler.jsonc");
if (wranglerConfig.includes("\"pages_build_output_dir\": \"out\"")) pass("wrangler Pages output directory is out");
else fail("wrangler Pages output directory must be out");

const outIndex = rel("out", "index.html");
if (fs.existsSync(outIndex)) pass("Cloudflare output index exists");
else warn("Cloudflare output index missing; run chart-lab:cf:build before deploy");

const wrangler = run("pnpm", ["exec", "wrangler", "--version"]);
writeEvidence("wrangler-version.txt", `${wrangler.stdout ?? ""}${wrangler.stderr ?? ""}`);
if (wrangler.status === 0) pass("wrangler resolves from package");
else warn("wrangler is not installed yet; run pnpm install");

const whoami = run("pnpm", ["exec", "wrangler", "whoami"]);
writeEvidence("wrangler-whoami-verify.txt", `${whoami.stdout ?? ""}${whoami.stderr ?? ""}`);
if (whoami.status === 0) pass("wrangler auth is available");
else warn("wrangler auth unavailable; deploy will require wrangler login or token");

const leakReport = path.join(rel("out"), "index.html");
if (fs.existsSync(leakReport)) {
  const noLeaks = run("node", ["scripts/verify-chart-lab-no-leaks.mjs"]);
  if (noLeaks.status === 0) pass("no-leak scanner passed for current out directory");
  else fail("no-leak scanner failed for current out directory");
}

if (!process.exitCode) pass("Cloudflare verification complete");
