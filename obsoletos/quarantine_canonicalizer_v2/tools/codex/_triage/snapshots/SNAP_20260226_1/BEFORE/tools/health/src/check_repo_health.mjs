#!/usr/bin/env node
import { readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../..");

const MAX_SRC_FILE_BYTES = 10 * 1024 * 1024;

const expectedSchemaFiles = [
  "agent-capabilities.schema.json",
  "feature-flags.schema.json",
  "health-report.schema.json",
  "job-request.schema.json",
  "job-result.schema.json",
  "manifest.json",
  "python-sync-map.json",
  "schema-version.json"
].sort((left, right) => left.localeCompare(right));

const ignoreDirectories = new Set([
  ".git",
  ".turbo",
  "node_modules",
  "dist",
  "build",
  "coverage",
  ".venv",
  "venv",
  "__pycache__"
]);

const dumpPatterns = [
  /\.zip$/i,
  /DUMP/i,
  /\.bak/i
];

function toPosix(value) {
  return value.replace(/\\/g, "/");
}

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

function collectFiles(currentDirectory, relativeStart = "") {
  const entries = readdirSync(currentDirectory, { withFileTypes: true });
  const sortedEntries = [...entries].sort((left, right) => left.name.localeCompare(right.name));
  const files = [];

  for (const entry of sortedEntries) {
    const relativePath = path.join(relativeStart, entry.name);
    const absolutePath = path.join(currentDirectory, entry.name);

    if (entry.isDirectory()) {
      if (ignoreDirectories.has(entry.name)) {
        continue;
      }

      files.push(...collectFiles(absolutePath, relativePath));
      continue;
    }

    if (entry.isFile()) {
      files.push({
        absolutePath,
        relativePath: toPosix(relativePath)
      });
    }
  }

  return files;
}

function isSrcPath(relativePath) {
  return relativePath.startsWith("src/") || relativePath.includes("/src/");
}

function checkSchemaFiles(violations) {
  const generatedDir = path.join(repoRoot, "packages/contracts/schemas/generated");
  const diskFiles = readdirSync(generatedDir, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right));

  const missing = expectedSchemaFiles.filter((file) => !diskFiles.includes(file));
  const extras = diskFiles.filter((file) => !expectedSchemaFiles.includes(file));

  for (const file of missing) {
    violations.push({
      code: "SCHEMA_MISSING",
      path: `packages/contracts/schemas/generated/${file}`,
      message: "Expected generated schema file is missing"
    });
  }

  for (const file of extras) {
    violations.push({
      code: "SCHEMA_EXTRA",
      path: `packages/contracts/schemas/generated/${file}`,
      message: "Unexpected generated schema file found"
    });
  }

  return {
    expectedCount: expectedSchemaFiles.length,
    diskCount: diskFiles.length,
    missing,
    extras
  };
}

function checkSrcArtifacts(files, violations) {
  const largeFiles = [];
  const dumpFiles = [];

  for (const fileInfo of files) {
    if (!isSrcPath(fileInfo.relativePath)) {
      continue;
    }

    const stats = statSync(fileInfo.absolutePath);
    const basename = path.basename(fileInfo.relativePath);

    if (stats.size > MAX_SRC_FILE_BYTES) {
      largeFiles.push({
        path: fileInfo.relativePath,
        size: stats.size
      });
      violations.push({
        code: "SRC_TOO_LARGE",
        path: fileInfo.relativePath,
        message: `File exceeds ${MAX_SRC_FILE_BYTES} bytes`,
        size: stats.size
      });
    }

    if (dumpPatterns.some((pattern) => pattern.test(basename))) {
      dumpFiles.push({
        path: fileInfo.relativePath,
        size: stats.size
      });
      violations.push({
        code: "SRC_DUMP_PATTERN",
        path: fileInfo.relativePath,
        message: "Dump/archive/back-up pattern is blocked under src/**",
        size: stats.size
      });
    }
  }

  return {
    maxSrcBytes: MAX_SRC_FILE_BYTES,
    largeFileCount: largeFiles.length,
    dumpPatternCount: dumpFiles.length,
    largeFiles,
    dumpFiles
  };
}

async function fetchWithTimeout(url, init, timeoutMs = 500) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal
    });
    const text = await response.text();
    return {
      ok: response.ok,
      status: response.status,
      body: text
    };
  } catch {
    return {
      ok: false,
      status: 0,
      body: ""
    };
  } finally {
    clearTimeout(timeout);
  }
}

async function checkEndpointsIfRunning(violations) {
  const reports = [];

  const services = [
    {
      name: "core-api",
      baseUrl: "http://127.0.0.1:3001",
      checks: async () => {
        const enqueue = await fetchWithTimeout("http://127.0.0.1:3001/jobs", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            jobId: "health-check-001",
            kind: "echo",
            input: { text: "health" },
            requestedAtUtc: "2026-01-01T00:00:00.000Z",
            flags: {
              enableAiExecution: false,
              enableCapabilitiesProxy: false,
              enableExperimentalUi: false,
              enableHealthDashboard: false
            }
          })
        });

        const job = await fetchWithTimeout("http://127.0.0.1:3001/jobs/health-check-001", { method: "GET" });
        const capabilities = await fetchWithTimeout("http://127.0.0.1:3001/capabilities", { method: "GET" });

        return [
          { path: "POST /jobs", response: enqueue, allowed: [200, 202, 400] },
          { path: "GET /jobs/:id", response: job, allowed: [200, 404] },
          { path: "GET /capabilities", response: capabilities, allowed: [200, 502] }
        ];
      }
    },
    {
      name: "ai-agent",
      baseUrl: "http://127.0.0.1:8001",
      checks: async () => {
        const capabilities = await fetchWithTimeout("http://127.0.0.1:8001/capabilities", { method: "GET" });
        const run = await fetchWithTimeout("http://127.0.0.1:8001/jobs/run", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            jobId: "health-ai-001",
            kind: "echo",
            input: { text: "health" },
            requestedAtUtc: "2026-01-01T00:00:00Z",
            flags: {
              enableAiExecution: true,
              enableCapabilitiesProxy: false,
              enableExperimentalUi: false,
              enableHealthDashboard: false
            }
          })
        });

        return [
          { path: "GET /capabilities", response: capabilities, allowed: [200] },
          { path: "POST /jobs/run", response: run, allowed: [200, 400] }
        ];
      }
    }
  ];

  for (const service of services) {
    const health = await fetchWithTimeout(`${service.baseUrl}/health`, { method: "GET" });

    if (!health.ok) {
      reports.push({
        service: service.name,
        running: false,
        healthStatus: health.status,
        endpoints: []
      });
      continue;
    }

    const endpointResults = await service.checks();
    const normalized = endpointResults.map((result) => ({
      endpoint: result.path,
      status: result.response.status,
      ok: result.allowed.includes(result.response.status)
    }));

    for (const endpoint of normalized) {
      if (!endpoint.ok) {
        violations.push({
          code: "ENDPOINT_MISSING_OR_INVALID",
          path: `${service.name} ${endpoint.endpoint}`,
          message: `Unexpected status code ${endpoint.status}`
        });
      }
    }

    reports.push({
      service: service.name,
      running: true,
      healthStatus: health.status,
      endpoints: normalized
    });
  }

  return reports.sort((left, right) => left.service.localeCompare(right.service));
}

async function main() {
  const allFiles = collectFiles(repoRoot);
  const violations = [];

  const schemaReport = checkSchemaFiles(violations);
  const artifactReport = checkSrcArtifacts(allFiles, violations);
  const endpointReport = await checkEndpointsIfRunning(violations);

  const sortedViolations = [...violations].sort((left, right) => {
    const pathCompare = left.path.localeCompare(right.path);
    if (pathCompare !== 0) {
      return pathCompare;
    }

    return left.code.localeCompare(right.code);
  });

  const report = {
    generatedAt: "static",
    repo: toPosix(repoRoot),
    checks: {
      endpoints: endpointReport,
      schemas: schemaReport,
      srcArtifacts: artifactReport
    },
    violations: sortedViolations
  };

  const serialized = `${JSON.stringify(stableSort(report), null, 2)}\n`;
  process.stdout.write(serialized);

  if (sortedViolations.length > 0) {
    process.exitCode = 1;
  }
}

main().catch((error) => {
  process.stderr.write(`health check failed: ${error instanceof Error ? error.message : "unknown error"}\n`);
  process.exitCode = 1;
});
