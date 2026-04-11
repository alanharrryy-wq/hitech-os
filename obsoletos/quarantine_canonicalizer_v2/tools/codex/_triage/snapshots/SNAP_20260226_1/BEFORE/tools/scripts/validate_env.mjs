#!/usr/bin/env node
const checks = [
  {
    name: "CORE_API_HOST",
    validate: (value) => value.trim().length > 0,
    message: "must be a non-empty string"
  },
  {
    name: "CORE_API_PORT",
    validate: (value) => {
      const parsed = Number.parseInt(value, 10);
      return Number.isInteger(parsed) && parsed >= 1 && parsed <= 65535;
    },
    message: "must be an integer in range 1-65535"
  },
  {
    name: "AI_AGENT_URL",
    validate: (value) => {
      try {
        const parsed = new URL(value);
        return parsed.protocol === "http:" || parsed.protocol === "https:";
      } catch {
        return false;
      }
    },
    message: "must be a valid http(s) URL"
  },
  {
    name: "AI_AGENT_TIMEOUT_MS",
    validate: (value) => {
      const parsed = Number.parseInt(value, 10);
      return Number.isInteger(parsed) && parsed > 0;
    },
    message: "must be a positive integer"
  },
  {
    name: "CONTRACT_SCHEMA_VERSION",
    validate: (value) => value.trim().length > 0,
    message: "must be a non-empty string"
  },
  {
    name: "CORE_API_FIXED_NOW_UTC",
    validate: (value) => !Number.isNaN(new Date(value).getTime()),
    message: "must be a valid ISO UTC datetime"
  }
];

const failures = [];
const normalized = [];

for (const check of checks) {
  const value = process.env[check.name];
  if (value === undefined) {
    normalized.push(`${check.name}=<unset>`);
    continue;
  }

  const trimmed = String(value).trim();
  if (!check.validate(trimmed)) {
    failures.push(`${check.name} ${check.message}`);
    continue;
  }

  normalized.push(`${check.name}=${trimmed}`);
}

normalized.sort((left, right) => left.localeCompare(right));
for (const line of normalized) {
  console.log(`[env] ${line}`);
}

if (failures.length > 0) {
  failures.sort((left, right) => left.localeCompare(right));
  for (const failure of failures) {
    console.error(`[env] INVALID ${failure}`);
  }
  process.exit(1);
}

console.log("[env] validation OK");
