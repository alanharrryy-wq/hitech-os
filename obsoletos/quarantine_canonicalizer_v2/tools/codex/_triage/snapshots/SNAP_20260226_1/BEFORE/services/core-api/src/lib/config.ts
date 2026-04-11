import path from "node:path";
import { fileURLToPath } from "node:url";

export interface CoreApiRuntimeConfig {
  host: string;
  port: number;
  aiAgentUrl: string;
  aiAgentTimeoutMs: number;
  serviceVersion: string;
  contractVersion: string;
  fixedNowUtc: string | null;
  governanceRunsRoot: string;
  governanceLatestRunIdPath: string;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "../../../..");

function parseInteger(value: string | undefined, fallback: number): number {
  if (!value) {
    return fallback;
  }

  const parsed = Number.parseInt(value, 10);
  if (Number.isNaN(parsed)) {
    return fallback;
  }

  return parsed;
}

function parseUtcIso(value: string | undefined): string | null {
  if (!value || value.trim().length === 0) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return parsed.toISOString();
}

export function loadRuntimeConfig(): CoreApiRuntimeConfig {
  const governanceRunsRoot = path.resolve(
    process.env.CORE_API_GOVERNANCE_RUNS_ROOT ?? path.join(repoRoot, "tools", "codex", "runs")
  );
  const governanceLatestRunIdPath = path.resolve(
    process.env.CORE_API_GOVERNANCE_LATEST_RUN_ID_PATH ??
      path.join(governanceRunsRoot, "LATEST_RUN_ID.txt")
  );

  return {
    host: process.env.CORE_API_HOST ?? "127.0.0.1",
    port: parseInteger(process.env.CORE_API_PORT, 3001),
    aiAgentUrl: process.env.AI_AGENT_URL ?? "http://127.0.0.1:8001",
    aiAgentTimeoutMs: parseInteger(process.env.AI_AGENT_TIMEOUT_MS, 1500),
    serviceVersion: process.env.CORE_API_VERSION ?? "0.2.0",
    contractVersion: process.env.CONTRACT_SCHEMA_VERSION ?? "1.1.0",
    fixedNowUtc: parseUtcIso(process.env.CORE_API_FIXED_NOW_UTC),
    governanceRunsRoot,
    governanceLatestRunIdPath
  };
}
