export interface CoreApiRuntimeConfig {
  host: string;
  port: number;
  aiAgentUrl: string;
  aiAgentTimeoutMs: number;
  serviceVersion: string;
  contractVersion: string;
}

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

export function loadRuntimeConfig(): CoreApiRuntimeConfig {
  return {
    host: process.env.CORE_API_HOST ?? "127.0.0.1",
    port: parseInteger(process.env.CORE_API_PORT, 3001),
    aiAgentUrl: process.env.AI_AGENT_URL ?? "http://127.0.0.1:8001",
    aiAgentTimeoutMs: parseInteger(process.env.AI_AGENT_TIMEOUT_MS, 1500),
    serviceVersion: process.env.CORE_API_VERSION ?? "0.2.0",
    contractVersion: process.env.CONTRACT_SCHEMA_VERSION ?? "1.1.0"
  };
}
