import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

type JsonPrimitive = string | number | boolean | null;
type JsonValue = JsonPrimitive | JsonValue[] | { [key: string]: JsonValue };

interface SchemaEntry {
  name: string;
  file: string;
  schema: JsonValue;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.resolve(__dirname, "../schemas/generated");
const checkMode = process.argv.includes("--check");
const baseSchema = "https://json-schema.org/draft/2020-12/schema";
const contractVersion = "1.1.0";

const jsonValueDef: JsonValue = {
  oneOf: [
    { type: "string" },
    { type: "number" },
    { type: "boolean" },
    { type: "null" },
    {
      type: "array",
      items: { $ref: "#/$defs/jsonValue" }
    },
    {
      type: "object",
      additionalProperties: { $ref: "#/$defs/jsonValue" }
    }
  ]
};

const jobKinds = ["echo", "extract_keywords", "summarize_text"];
const jobStatuses = ["completed", "failed", "queued", "running"];
const healthStatuses = ["degraded", "error", "ok"];

const featureFlags = {
  enableAiExecution: false,
  enableCapabilitiesProxy: false,
  enableExperimentalUi: false,
  enableHealthDashboard: false
};

const SCHEMAS: SchemaEntry[] = [
  {
    name: "AgentCapabilities",
    file: "agent-capabilities.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "AgentCapabilities",
      additionalProperties: false,
      type: "object",
      properties: {
        defaults: {
          type: "object",
          additionalProperties: false,
          properties: {
            enableAiExecution: { type: "boolean", default: false },
            enableCapabilitiesProxy: { type: "boolean", default: false },
            enableExperimentalUi: { type: "boolean", default: false },
            enableHealthDashboard: { type: "boolean", default: false }
          },
          required: [
            "enableAiExecution",
            "enableCapabilitiesProxy",
            "enableExperimentalUi",
            "enableHealthDashboard"
          ]
        },
        deterministic: { const: true, type: "boolean" },
        maxInputChars: { type: "integer", minimum: 1 },
        notes: { type: "array", items: { type: "string", minLength: 1 } },
        protocolVersion: { type: "string", minLength: 1 },
        serviceName: { const: "ai-agent", type: "string" },
        supportedJobKinds: {
          type: "array",
          minItems: 1,
          items: { type: "string", enum: jobKinds }
        },
        version: { type: "string", minLength: 1 }
      },
      required: [
        "defaults",
        "deterministic",
        "maxInputChars",
        "notes",
        "protocolVersion",
        "serviceName",
        "supportedJobKinds",
        "version"
      ]
    }
  },
  {
    name: "FeatureFlags",
    file: "feature-flags.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "FeatureFlags",
      type: "object",
      additionalProperties: false,
      properties: {
        enableAiExecution: { type: "boolean", default: false },
        enableCapabilitiesProxy: { type: "boolean", default: false },
        enableExperimentalUi: { type: "boolean", default: false },
        enableHealthDashboard: { type: "boolean", default: false }
      },
      required: [
        "enableAiExecution",
        "enableCapabilitiesProxy",
        "enableExperimentalUi",
        "enableHealthDashboard"
      ]
    }
  },
  {
    name: "HealthReport",
    file: "health-report.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "HealthReport",
      type: "object",
      additionalProperties: false,
      properties: {
        checks: {
          type: "array",
          items: {
            type: "object",
            additionalProperties: false,
            properties: {
              message: { type: "string", minLength: 1 },
              name: { type: "string", minLength: 1 },
              status: { type: "string", enum: healthStatuses }
            },
            required: ["message", "name", "status"]
          }
        },
        contractVersion: { type: "string", minLength: 1 },
        service: { type: "string", minLength: 1 },
        status: { type: "string", enum: healthStatuses },
        timestampUtc: { type: "string", format: "date-time" },
        version: { type: "string", minLength: 1 }
      },
      required: ["checks", "contractVersion", "service", "status", "timestampUtc", "version"]
    }
  },
  {
    name: "JobRequest",
    file: "job-request.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "JobRequest",
      type: "object",
      additionalProperties: false,
      $defs: {
        jsonValue: jsonValueDef
      },
      properties: {
        flags: {
          type: "object",
          additionalProperties: false,
          properties: {
            enableAiExecution: { type: "boolean", default: false },
            enableCapabilitiesProxy: { type: "boolean", default: false },
            enableExperimentalUi: { type: "boolean", default: false },
            enableHealthDashboard: { type: "boolean", default: false }
          },
          required: [
            "enableAiExecution",
            "enableCapabilitiesProxy",
            "enableExperimentalUi",
            "enableHealthDashboard"
          ]
        },
        input: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/jsonValue"
          }
        },
        jobId: { type: "string", minLength: 1 },
        kind: { type: "string", enum: jobKinds },
        requestedAtUtc: { type: "string", format: "date-time" }
      },
      required: ["flags", "input", "jobId", "kind", "requestedAtUtc"]
    }
  },
  {
    name: "JobResult",
    file: "job-result.schema.json",
    schema: {
      $schema: baseSchema,
      $id: "JobResult",
      type: "object",
      additionalProperties: false,
      $defs: {
        jsonValue: jsonValueDef
      },
      properties: {
        finishedAtUtc: {
          oneOf: [{ type: "string", format: "date-time" }, { type: "null" }]
        },
        jobId: { type: "string", minLength: 1 },
        kind: { type: "string", enum: jobKinds },
        logs: {
          type: "array",
          items: {
            type: "object",
            additionalProperties: false,
            properties: {
              atUtc: { type: "string", format: "date-time" },
              details: {
                type: "object",
                additionalProperties: { $ref: "#/$defs/jsonValue" }
              },
              event: { type: "string", minLength: 1 },
              level: { type: "string", enum: ["error", "info", "warn"] },
              message: { type: "string", minLength: 1 },
              seq: { type: "integer", minimum: 0 }
            },
            required: ["atUtc", "details", "event", "level", "message", "seq"]
          }
        },
        output: {
          type: "object",
          additionalProperties: {
            $ref: "#/$defs/jsonValue"
          }
        },
        status: { type: "string", enum: jobStatuses }
      },
      required: ["finishedAtUtc", "jobId", "kind", "logs", "output", "status"]
    }
  }
];

const expectedFiles = [
  "agent-capabilities.schema.json",
  "feature-flags.schema.json",
  "health-report.schema.json",
  "job-request.schema.json",
  "job-result.schema.json",
  "manifest.json",
  "python-sync-map.json",
  "schema-version.json"
].sort((left, right) => left.localeCompare(right));

function stableSort(value: JsonValue): JsonValue {
  if (Array.isArray(value)) {
    return value.map((item) => stableSort(item));
  }

  if (value !== null && typeof value === "object") {
    return Object.keys(value)
      .sort((left, right) => left.localeCompare(right))
      .reduce((accumulator, key) => {
        accumulator[key] = stableSort((value as Record<string, JsonValue>)[key]);
        return accumulator;
      }, {} as Record<string, JsonValue>);
  }

  return value;
}

function serialize(value: JsonValue): string {
  return `${JSON.stringify(stableSort(value), null, 2)}\n`;
}

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function upsertFile(filePath: string, content: string): boolean {
  if (checkMode) {
    if (!existsSync(filePath)) {
      return false;
    }

    const current = readFileSync(filePath, "utf8");
    return current === content;
  }

  writeFileSync(filePath, content, "utf8");
  return true;
}

function cleanExtraArtifacts(): boolean {
  const diskFiles = readdirSync(outputDir, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right));

  const extras = diskFiles.filter((file) => !expectedFiles.includes(file));
  if (checkMode) {
    if (extras.length > 0) {
      for (const file of extras) {
        console.error(`[schema-check] EXTRA_FILE ${file}`);
      }
      return false;
    }
    return true;
  }

  for (const extra of extras) {
    rmSync(path.join(outputDir, extra), { force: true });
    console.log(`[schema-gen] REMOVED ${extra}`);
  }
  return true;
}

mkdirSync(outputDir, { recursive: true });

const sortedSchemas = [...SCHEMAS].sort((left, right) => left.name.localeCompare(right.name));
const manifest: Array<{ file: string; name: string; sha256: string }> = [];
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

const schemaFiles = manifest.map((item) => item.file).sort((left, right) => left.localeCompare(right));
const manifestDoc = {
  version: 2,
  contractVersion,
  entries: manifest.sort((left, right) => left.file.localeCompare(right.file))
};

const syncMap = {
  generatedAt: "static",
  contractVersion,
  pythonModelMap: {
    AgentCapabilities: "services/ai-agent/app/models.py::AgentCapabilitiesModel",
    FeatureFlags: "services/ai-agent/app/models.py::FeatureFlagsModel",
    HealthReport: "services/ai-agent/app/models.py::HealthReportModel",
    JobRequest: "services/ai-agent/app/models.py::JobRequestModel",
    JobResult: "services/ai-agent/app/models.py::JobResultModel"
  },
  schemaFiles
};

const versionDoc = {
  contractVersion,
  compatibility: {
    backwardCompatibleWith: ["1.0.x"],
    notes: [
      "Added AgentCapabilities schema",
      "JobRequest switched to {jobId, kind, input, requestedAtUtc, flags}",
      "JobResult switched to {jobId, kind, status, output, logs, finishedAtUtc}"
    ]
  },
  featureFlagsDefault: featureFlags
};

const generatedDocs: Array<[string, JsonValue]> = [
  ["manifest.json", manifestDoc],
  ["python-sync-map.json", syncMap],
  ["schema-version.json", versionDoc]
];

for (const [fileName, value] of generatedDocs) {
  const targetPath = path.join(outputDir, fileName);
  if (!upsertFile(targetPath, serialize(value))) {
    failed = true;
    console.error(`[schema-check] MISMATCH ${fileName}`);
  } else {
    console.log(`[schema-gen] OK ${fileName}`);
  }
}

if (!cleanExtraArtifacts()) {
  failed = true;
}

if (checkMode && failed) {
  process.exitCode = 1;
  console.error("[schema-check] Detected schema drift.");
} else if (checkMode) {
  console.log("[schema-check] All generated schemas are deterministic.");
}
