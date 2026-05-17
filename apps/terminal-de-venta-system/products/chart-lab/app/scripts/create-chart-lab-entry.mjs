import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function toPascalCase(value) {
  return value
    .replace(/[^a-zA-Z0-9]+/g, " ")
    .trim()
    .split(/\s+/)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join("");
}

function usage() {
  console.log(`PRISMA Chart Lab scaffold

Dry run:
  node scripts/create-chart-lab-entry.mjs --id=web.example-chart --title="Example Chart" --surface=web

Write files:
  node scripts/create-chart-lab-entry.mjs --id=web.example-chart --title="Example Chart" --surface=web --write

Creates:
  src/prisma-charts/components/<PascalName>.tsx
  src/prisma-charts/mocks/<id>.mock.ts

It prints the registry entry stub. It never edits the registry automatically.
`);
}

const args = Object.fromEntries(
  process.argv.slice(2).map((arg) => {
    const [key, ...rest] = arg.replace(/^--/, "").split("=");
    return [key, rest.length ? rest.join("=") : "true"];
  })
);

if (args.help || !args.id || !args.title) {
  usage();
  process.exit(args.help ? 0 : 1);
}

const id = String(args.id);
const title = String(args.title);
const surface = String(args.surface ?? "web");
const componentName = toPascalCase(title);
const componentPath = path.join(appRoot, "src", "prisma-charts", "components", `${componentName}.tsx`);
const mockPath = path.join(appRoot, "src", "prisma-charts", "mocks", `${id}.mock.ts`);
const write = args.write === "true";

const componentSource = `"use client";

import type { LabChartRenderProps } from "../chart-lab-types";

export function ${componentName}({ entry }: LabChartRenderProps) {
  return (
    <section className="lab-empty-chart" aria-label={entry.title}>
      <strong>{entry.title}</strong>
      <span>New PRISMA chart scaffold</span>
    </section>
  );
}
`;

const mockSource = `export const ${componentName}Mock = {
  label: ${JSON.stringify(title)},
  status: "lab/mock",
  points: []
};
`;

if (write) {
  for (const target of [componentPath, mockPath]) {
    if (fs.existsSync(target)) {
      console.error(`Refusing to overwrite existing file: ${target}`);
      process.exit(1);
    }
    fs.mkdirSync(path.dirname(target), { recursive: true });
  }
  fs.writeFileSync(componentPath, componentSource, "utf8");
  fs.writeFileSync(mockPath, mockSource, "utf8");
  console.log(`Created ${componentPath}`);
  console.log(`Created ${mockPath}`);
} else {
  console.log("Dry run only. Add --write to create files.");
  console.log(`Would create ${componentPath}`);
  console.log(`Would create ${mockPath}`);
}

console.log(`
Registry stub:
{
  id: ${JSON.stringify(id)},
  title: ${JSON.stringify(title)},
  shortName: ${JSON.stringify(title)},
  surface: ${JSON.stringify(surface)},
  family: "future",
  chartType: "Custom",
  description: "Describe the operational visual.",
  operationalQuestion: "What PRISMA question does this answer?",
  readiness: "placeholder",
  dataStatus: "lab/mock",
  mockDataLabel: "Lab mock data only.",
  confidence: 100,
  freshnessLabel: "Static lab mock.",
  promotionTarget: "Choose PC, Tablet, Mobile, Web, or Control.",
  promotionBoundary: "Promote explicitly through the target surface adapter.",
  sourceModule: "products/chart-lab/app",
  componentPath: "products/chart-lab/app/src/prisma-charts/components/${componentName}.tsx",
  mockPath: "products/chart-lab/app/src/prisma-charts/mocks/${id}.mock.ts",
  registryPath: "products/chart-lab/app/src/prisma-charts/chart-lab-registry.tsx",
  defaultHeight: 320,
  Component: ${componentName}
}
`);
