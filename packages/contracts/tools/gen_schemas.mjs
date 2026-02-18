#!/usr/bin/env node
import { createHash } from "node:crypto";
import { mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.resolve(__dirname, "../schemas/generated");
const checkMode = process.argv.includes("--check");

const baseSchema = "https://json-schema.org/draft/2020-12/schema";

const SCHEMAS = [
  {
    name: "FeatureFlags",
    file: "feature-flags.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "FeatureFlags",
      additionalProperties: false,
      properties: {
        enableAiExecution: { default: false, type: "boolean" },
        enableExperimentalUi: { default: false, type: "boolean" },
        enableHealthDashboard: { default: false, type: "boolean" }
      },
      required: ["enableAiExecution", "enableExperimentalUi", "enableHealthDashboard"],
      type: "object"
    }
  },
  {
    name: "HealthReport",
    file: "health-report.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "HealthReport",
      additionalProperties: false,
      properties: {
        checks: {
          additionalProperties: {
            enum: ["ok", "degraded", "error"],
            type: "string"
          },
          type: "object"
        },
        service: { minLength: 1, type: "string" },
        status: { enum: ["ok", "degraded", "error"], type: "string" },
        timestamp: { format: "date-time", type: "string" },
        version: { minLength: 1, type: "string" }
      },
      required: ["checks", "service", "status", "timestamp", "version"],
      type: "object"
    }
  },
  {
    name: "JobRequest",
    file: "job-request.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "JobRequest",
      additionalProperties: false,
      properties: {
        executionMode: {
          default: "queued",
          enum: ["queued", "run-now"],
          type: "string"
        },
        payload: {
          additionalProperties: {
            oneOf: [{ type: "string" }, { type: "number" }, { type: "boolean" }]
          },
          type: "object"
        },
        requestId: { minLength: 1, type: "string" },
        submittedAt: { format: "date-time", type: "string" },
        taskType: {
          enum: ["summarize", "classify", "extract"],
          type: "string"
        }
      },
      required: ["executionMode", "payload", "requestId", "submittedAt", "taskType"],
      type: "object"
    }
  },
  {
    name: "JobResult",
    file: "job-result.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "JobResult",
      additionalProperties: false,
      properties: {
        error: { type: "string" },
        jobId: { minLength: 1, type: "string" },
        output: {
          additionalProperties: {
            oneOf: [{ type: "string" }, { type: "number" }, { type: "boolean" }]
          },
          type: "object"
        },
        processedAt: { format: "date-time", type: "string" },
        requestId: { minLength: 1, type: "string" },
        source: { enum: ["core-api", "ai-agent"], type: "string" },
        status: { enum: ["queued", "running", "completed", "failed"], type: "string" }
      },
      required: ["jobId", "processedAt", "requestId", "source", "status"],
      type: "object"
    }
  }
];

function stableSort(value) {
  if (Array.isArray(value)) {
    return value.map((item) => stableSort(item));
  }

  if (value !== null && typeof value === "object") {
    return Object.keys(value)
      .sort((left, right) => left.localeCompare(right))
      .reduce((accumulator, key) => {
        accumulator[key] = stableSort(value[key]);
        return accumulator;
      }, {});
  }

  return value;
}

function serialize(value) {
  return `${JSON.stringify(stableSort(value), null, 2)}\n`;
}

function sha256(value) {
  return createHash("sha256").update(value).digest("hex");
}

function upsertFile(filePath, content) {
  if (checkMode) {
    const current = readFileSync(filePath, "utf8");
    return current === content;
  }

  writeFileSync(filePath, content, "utf8");
  return true;
}

mkdirSync(outputDir, { recursive: true });

const expectedFiles = new Set([
  "feature-flags.schema.json",
  "health-report.schema.json",
  "job-request.schema.json",
  "job-result.schema.json",
  "manifest.json",
  "python-sync-map.json"
]);

if (!checkMode) {
  for (const existing of readdirSync(outputDir)) {
    if (existing.endsWith(".json") && !expectedFiles.has(existing)) {
      rmSync(path.join(outputDir, existing), { force: true });
    }
  }
}

const sortedSchemas = [...SCHEMAS].sort((left, right) => left.name.localeCompare(right.name));
const manifest = [];
let failed = false;

for (const entry of sortedSchemas) {
  const targetPath = path.join(outputDir, entry.file);
  const serialized = serialize(entry.schema);
  const ok = upsertFile(targetPath, serialized);

  manifest.push({
    file: entry.file,
    name: entry.name,
    sha256: sha256(serialized)
  });

  if (!ok) {
    failed = true;
    console.error(`[schema-check] MISMATCH ${entry.file}`);
  } else {
    console.log(`[schema-gen] OK ${entry.file}`);
  }
}

const syncMap = {
  generatedAt: "static",
  pythonModelMap: {
    FeatureFlags: "services/ai-agent/app/models.py::FeatureFlagsModel",
    HealthReport: "services/ai-agent/app/models.py::HealthReportModel",
    JobRequest: "services/ai-agent/app/models.py::JobRequestModel",
    JobResult: "services/ai-agent/app/models.py::JobResultModel"
  },
  schemaFiles: manifest.map((item) => item.file)
};

const manifestDoc = {
  version: 1,
  entries: manifest
};

const manifestPath = path.join(outputDir, "manifest.json");
const syncMapPath = path.join(outputDir, "python-sync-map.json");

if (!upsertFile(manifestPath, serialize(manifestDoc))) {
  failed = true;
  console.error("[schema-check] MISMATCH manifest.json");
} else {
  console.log("[schema-gen] OK manifest.json");
}

if (!upsertFile(syncMapPath, serialize(syncMap))) {
  failed = true;
  console.error("[schema-check] MISMATCH python-sync-map.json");
} else {
  console.log("[schema-gen] OK python-sync-map.json");
}

if (checkMode && failed) {
  process.exitCode = 1;
  console.error("[schema-check] Detected schema drift.");
} else if (checkMode) {
  console.log("[schema-check] All generated schemas are deterministic.");
}
