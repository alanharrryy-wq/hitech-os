import fs from "node:fs";
import path from "node:path";
import { fail, pass, terminalRoot } from "./chart-lab-script-utils.mjs";

const allowedPrefixes = [
  "products/chart-lab/app/",
  "shared/prisma-charts/PrismaEChart.tsx",
  "shared/prisma-charts/prismaEchartsLoader.ts"
];
const forbiddenHits = [];

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const absolute = path.join(dir, entry.name);
    const relDir = path.relative(terminalRoot, absolute).replace(/\\/g, "/");
    if (["node_modules", ".next", "out", "_local"].includes(entry.name) || relDir.startsWith("tools/_local")) continue;
    if (entry.isDirectory()) walk(absolute);
    else if (/\.(ts|tsx|js|jsx|mjs)$/.test(entry.name)) {
      const rel = path.relative(terminalRoot, absolute).replace(/\\/g, "/");
      const content = fs.readFileSync(absolute, "utf8");
      if (content.includes("from \"echarts") || content.includes("from 'echarts") || content.includes("import(\"echarts")) {
        if (!allowedPrefixes.some((prefix) => rel.startsWith(prefix) || rel === prefix)) forbiddenHits.push(rel);
      }
    }
  }
}

walk(terminalRoot);

if (forbiddenHits.length) fail(`ECharts import boundary violations: ${forbiddenHits.join(", ")}`);
else pass("ECharts import boundary is clean for product surfaces");
