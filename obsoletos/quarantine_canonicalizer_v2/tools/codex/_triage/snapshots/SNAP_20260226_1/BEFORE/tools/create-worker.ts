#!/usr/bin/env node

import { mkdirSync, readdirSync, statSync, writeFileSync } from "node:fs";
import * as path from "node:path";
import { WORKER_ID_PATTERN } from "../factory/contracts/FactoryContracts";

interface CliOptions {
  readonly workerId: string;
  readonly description: string;
  readonly rootDir: string;
  readonly dryRun: boolean;
}

interface PlannedFile {
  readonly relativePath: string;
  readonly content: string;
}

function printUsage(): void {
  const usage = [
    "Usage:",
    "  node dist/tools/create-worker.js --name <WORKER_ID> [options]",
    "",
    "Options:",
    "  --name, -n           Worker id (required), format: /^[A-Z]_[a-z0-9_]+$/",
    "  --description, -d    Worker description",
    "  --root               Repository root (default: current directory)",
    "  --dry-run            Print planned files without writing",
    "  --help, -h           Show this help",
    "",
    "Example:",
    "  pnpm run factory:create-worker -- --name E_observability --description \"Observability worker\"",
    "",
  ];
  process.stdout.write(usage.join("\n"));
}

function parseArgs(argv: readonly string[]): CliOptions {
  let workerId = "";
  let description = "Generated deterministic worker module.";
  let rootDir = process.cwd();
  let dryRun = false;

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === undefined) {
      continue;
    }
    const next = argv[index + 1];
    switch (token) {
      case "--help":
      case "-h":
        printUsage();
        process.exit(0);
      case "--name":
      case "-n":
        if (next === undefined) {
          throw new Error("--name requires a value.");
        }
        workerId = next.trim();
        index += 1;
        break;
      case "--description":
      case "-d":
        if (next === undefined) {
          throw new Error("--description requires a value.");
        }
        description = next.trim();
        index += 1;
        break;
      case "--root":
        if (next === undefined) {
          throw new Error("--root requires a value.");
        }
        rootDir = path.resolve(next);
        index += 1;
        break;
      case "--dry-run":
        dryRun = true;
        break;
      default:
        if (token.startsWith("-")) {
          throw new Error(`Unknown argument: ${token}`);
        }
        if (workerId.length === 0) {
          workerId = token.trim();
          break;
        }
        throw new Error(`Unexpected positional argument: ${token}`);
    }
  }

  if (workerId.length === 0) {
    throw new Error("Worker id is required. Use --name <WORKER_ID>.");
  }
  if (description.length === 0) {
    throw new Error("Worker description must not be empty.");
  }

  return {
    workerId,
    description,
    rootDir,
    dryRun,
  };
}

function validateWorkerName(workerId: string): void {
  if (!WORKER_ID_PATTERN.test(workerId)) {
    throw new Error(
      `Worker id ${workerId} does not match required pattern ${WORKER_ID_PATTERN.source}.`,
    );
  }
}

function listExistingWorkerIds(factoryRoot: string): readonly string[] {
  if (!path.isAbsolute(factoryRoot)) {
    throw new Error("Factory root must be absolute.");
  }

  const entries = readdirSync(factoryRoot, { withFileTypes: true });
  const workers: string[] = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) {
      continue;
    }
    if (!WORKER_ID_PATTERN.test(entry.name)) {
      continue;
    }
    workers.push(entry.name);
  }
  return workers.sort((left, right) => left.localeCompare(right));
}

function createWorkerAgentTemplate(workerId: string, description: string): string {
  return [
    "import {",
    "  AgentExecutionResult,",
    "  FactoryAgent,",
    "} from \"../contracts/AgentInterface\";",
    "import { WorkerExecutionContext } from \"../contracts/FactoryContracts\";",
    "import { hashText } from \"../shared/Hashing\";",
    "",
    `const DESCRIPTION = ${JSON.stringify(description)};`,
    "",
    `export class ${workerId}Agent implements FactoryAgent {`,
    `  readonly workerId = ${JSON.stringify(workerId)};`,
    "  readonly description = DESCRIPTION;",
    "  readonly deterministicOrderHint = 100;",
    "  readonly boundaries = {",
    `    allowedReadRoots: [\"factory/${workerId}\", \"factory/contracts\", \"factory/shared\"],`,
    `    allowedWriteRoots: [\"factory/${workerId}\"],`,
    "    deniesCrossWorkerBundles: true,",
    "  } as const;",
    "  readonly capabilities = {",
    "    supportsDryRun: true,",
    "    supportsSnapshotOutput: true,",
    "    emitsDiffs: true,",
    "  } as const;",
    "",
    "  async execute(context: WorkerExecutionContext): Promise<AgentExecutionResult> {",
    "    const generatedPath = `factory/${this.workerId}/README.md`;",
    "    const checksum = hashText(`${context.runId}:${context.executionSeed}:${this.workerId}`);",
    "    return {",
    "      workerId: this.workerId,",
    "      status: \"PASS\",",
    "      summary: `${this.workerId} produced deterministic baseline output.`,",
    "      fileChanges: [",
    "        {",
    "          workerId: this.workerId,",
    "          path: generatedPath,",
    "          kind: \"modified\",",
    "          sha256: checksum,",
    "          bytes: checksum.length,",
    "          summary: \"Worker baseline artifact updated deterministically.\",",
    "        },",
    "      ],",
    "      checks: [",
    "        {",
    "          name: \"deterministic_template_integrity\",",
    "          required: true,",
    "          rc: 0,",
    "          details: \"Template worker executed without temporal signals.\",",
    "        },",
    "      ],",
    "      metadata: {",
    "        generatedBy: \"tools/create-worker.ts\",",
    "        workerId: this.workerId,",
    "      },",
    "      output: {",
    "        workerId: this.workerId,",
    "        checksum,",
    "      },",
    "    };",
    "  }",
    "}",
    "",
  ].join("\n");
}

function createIndexTemplate(workerId: string): string {
  return [`export * from \"./WorkerAgent\";`, `export { ${workerId}Agent } from \"./WorkerAgent\";`, ""].join(
    "\n",
  );
}

function createScopeLockTemplate(workerId: string): string {
  const payload = {
    worker_id: workerId,
    allowed_paths: [`factory/${workerId}`],
    forbidden_paths: [
      "factory/A_core",
      "factory/B_tooling",
      "factory/C_features",
      "factory/D_validation",
      "factory/Z_aggregator",
    ],
    feature_flags: {
      allowExperimentalWorkers: false,
      allowCrossModuleImports: false,
      allowTemporalSignals: false,
      allowNonDeterministicApis: false,
    },
  };
  return JSON.stringify(payload, null, 2) + "\n";
}

function createReadmeTemplate(workerId: string, description: string): string {
  const lines = [
    `# ${workerId}`,
    "",
    description,
    "",
    "## Deterministic Rules",
    "- No temporal dependencies.",
    "- No cross-module imports into other factory worker blocks.",
    "- Feature flags remain OFF by default.",
    "- Outputs must be deterministic for identical input envelopes.",
    "",
    "## Owned Surface",
    `- \`factory/${workerId}/\``,
    "",
  ];
  return lines.join("\n");
}

function planFiles(workerId: string, description: string): readonly PlannedFile[] {
  const basePath = `factory/${workerId}`;
  const files: PlannedFile[] = [
    {
      relativePath: `${basePath}/WorkerAgent.ts`,
      content: createWorkerAgentTemplate(workerId, description),
    },
    {
      relativePath: `${basePath}/index.ts`,
      content: createIndexTemplate(workerId),
    },
    {
      relativePath: `${basePath}/SCOPE_LOCK.json`,
      content: createScopeLockTemplate(workerId),
    },
    {
      relativePath: `${basePath}/README.md`,
      content: createReadmeTemplate(workerId, description),
    },
  ];
  return files.sort((left, right) => left.relativePath.localeCompare(right.relativePath));
}

function ensureUniqueWorker(workerId: string, existingWorkers: readonly string[]): void {
  if (existingWorkers.includes(workerId)) {
    throw new Error(`Worker ${workerId} already exists.`);
  }
}

function writePlannedFiles(rootDir: string, plannedFiles: readonly PlannedFile[]): void {
  for (const file of plannedFiles) {
    const absolutePath = path.resolve(rootDir, file.relativePath);
    const absoluteDir = path.dirname(absolutePath);
    mkdirSync(absoluteDir, { recursive: true });
    writeFileSync(absolutePath, file.content, { encoding: "utf8" });
  }
}

function ensureFactoryRoot(rootDir: string): string {
  const factoryRoot = path.resolve(rootDir, "factory");
  const factoryStats = statSync(factoryRoot, { throwIfNoEntry: false });
  if (factoryStats === undefined || !factoryStats.isDirectory()) {
    throw new Error(`Factory root does not exist: ${factoryRoot}`);
  }
  return factoryRoot;
}

function renderPlan(plannedFiles: readonly PlannedFile[]): string {
  const lines = ["Planned files:"];
  for (const file of plannedFiles) {
    lines.push(`- ${file.relativePath}`);
  }
  lines.push("");
  return lines.join("\n");
}

function run(): number {
  const options = parseArgs(process.argv.slice(2));
  validateWorkerName(options.workerId);

  const factoryRoot = ensureFactoryRoot(options.rootDir);
  const existingWorkers = listExistingWorkerIds(factoryRoot);
  ensureUniqueWorker(options.workerId, existingWorkers);

  const plannedFiles = planFiles(options.workerId, options.description);
  process.stdout.write(renderPlan(plannedFiles));

  if (options.dryRun) {
    process.stdout.write("Dry run complete. No files were written.\n");
    return 0;
  }

  writePlannedFiles(options.rootDir, plannedFiles);
  process.stdout.write(`Worker ${options.workerId} created successfully.\n`);
  return 0;
}

try {
  const exitCode = run();
  process.exit(exitCode);
} catch (error: unknown) {
  const message = error instanceof Error ? error.message : "Unknown error";
  process.stderr.write(`create-worker failed: ${message}\n`);
  process.exit(1);
}
