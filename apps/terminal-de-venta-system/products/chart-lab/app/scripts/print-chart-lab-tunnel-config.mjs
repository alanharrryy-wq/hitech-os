import fs from "node:fs";
import { pass, read, rel, writeEvidence } from "./chart-lab-script-utils.mjs";

const template = read("deploy/cloudflare-tunnel/prisma-chart-lab.tunnel.template.yml");
const evidencePath = writeEvidence("cloudflare-tunnel-template.yml", template);
console.log(template);
pass(`tunnel template copied to evidence: ${evidencePath}`);
pass(`source template: ${rel("deploy", "cloudflare-tunnel", "prisma-chart-lab.tunnel.template.yml")}`);
if (!fs.existsSync(rel("deploy", "cloudflare-tunnel", "prisma-chart-lab.tunnel.template.yml"))) process.exitCode = 1;
