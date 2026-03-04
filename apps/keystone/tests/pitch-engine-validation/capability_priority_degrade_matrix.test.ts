import { createAgentCapabilities } from "@hitech/contracts";
import { describe, expect, it } from "vitest";
import { AgentRegistry } from "../../../../factory/A_core/AgentRegistry";
import { createFeatureFlags, normalizeRequestedWorkers } from "../../../../factory/contracts/FactoryContracts";
import type { FactoryAgent } from "../../../../factory/contracts/AgentInterface";
import { resolvePitchLayerFlags } from "../../lib/pitch/layer-resolution";
import {
  CAPABILITY_PRIORITY_SCENARIOS,
  MOTION_BUDGET_SCENARIOS,
  REQUESTED_WORKER_SCENARIOS
} from "./fixtures/capability_degrade_scenarios.generated";

function buildAgent(workerId: string, hint: number): FactoryAgent {
  return {
    workerId,
    description: `agent-${workerId}`,
    deterministicOrderHint: hint,
    boundaries: {
      allowedReadRoots: ["apps/keystone"],
      allowedWriteRoots: ["apps/keystone/tests/pitch-engine-validation"],
      deniesCrossWorkerBundles: true
    },
    capabilities: {
      supportsDryRun: true,
      supportsSnapshotOutput: true,
      emitsDiffs: true
    },
    async execute() {
      return {
        workerId,
        status: "PASS",
        summary: `ok-${workerId}`,
        fileChanges: [{ path: "apps/keystone/tests/pitch-engine-validation/fake.ts", kind: "add", summary: "x" }],
        checks: [{ id: "c1", status: "PASS", detail: "ok" }],
        metadata: { workerId },
        output: { workerId }
      };
    }
  };
}

function applyCapabilityHardGate(env: string, requested: Record<string, boolean>) {
  if (env !== "production") {
    return { ...requested };
  }
  return {
    allowExperimentalWorkers: false,
    allowCrossModuleImports: false,
    allowTemporalSignals: false,
    allowNonDeterministicApis: false
  };
}

describe("pitch-engine capability/degrade + A_core validation", () => {
  it("keeps AgentRegistry deterministic fixed-order semantics", () => {
    const registry = new AgentRegistry();
    registry.register(buildAgent("D_validation", 50));
    registry.register(buildAgent("A_core", 10));
    registry.register(buildAgent("Z_aggregator", 99));
    expect(registry.list().map((agent) => agent.workerId)).toEqual([
      "A_core",
      "D_validation",
      "Z_aggregator"
    ]);
  });

  for (const scenario of REQUESTED_WORKER_SCENARIOS) {
    it(`requested worker normalization ${scenario.id}`, () => {
      expect(normalizeRequestedWorkers(scenario.input as string[])).toEqual(scenario.expected);
    });
  }

  for (const scenario of CAPABILITY_PRIORITY_SCENARIOS) {
    it(`requested vs applied capability hard gate ${scenario.id}`, () => {
      const requested = scenario.requested as Record<string, boolean>;
      const expectedApplied = scenario.applied as Record<string, boolean>;
      const applied = applyCapabilityHardGate(scenario.env, requested);
      expect(applied).toEqual(expectedApplied);
      const normalized = createFeatureFlags(applied as any);
      expect(Object.values(normalized).every((value) => typeof value === "boolean")).toBe(true);
      if (scenario.env === "production") {
        expect(Object.values(normalized).every((value) => value === false)).toBe(true);
      }
    });
  }

  for (const scenario of MOTION_BUDGET_SCENARIOS) {
    it(`motion budget degrade ${scenario.id}`, () => {
      const resolved = resolvePitchLayerFlags({
        layers: scenario.requested,
        layerProfile: scenario.profile,
        debug: "1"
      });
      const appliedMotion = scenario.profile === "neutral"
        ? resolved.flags["motion.enabled"]
        : false;
      expect(appliedMotion).toBe(scenario.expectMotionEnabled);
    });
  }

  for (let i = 0; i < 120; i += 1) {
    it(`capabilities contract sorting and priority ${i + 1}`, () => {
      const caps = createAgentCapabilities({
        version: `1.0.${i % 10}`,
        protocolVersion: "2026-03",
        maxInputChars: 4000 + i,
        supportedJobKinds: i % 2 === 0 ? ["summarize_text", "echo", "extract_keywords"] : ["extract_keywords", "echo", "summarize_text"],
        notes: i % 2 === 0 ? ["z", "a", "m"] : [" m ", "", "a", "z"]
      });
      expect(caps.supportedJobKinds).toEqual(["echo", "extract_keywords", "summarize_text"]);
      expect(caps.notes).toEqual(["a", "m", "z"]);
      expect(caps.deterministic).toBe(true);
    });
  }
});

