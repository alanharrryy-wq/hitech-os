import { FeatureFlagKey, FeatureFlags, createFeatureFlags } from "../contracts/FactoryContracts";
import { deepFreeze } from "../shared/Immutability";

export interface ToolingStep {
  readonly name: string;
  readonly command: string;
  readonly required: boolean;
  readonly deterministic: boolean;
}

export interface ToolingSmokePlan {
  readonly steps: readonly ToolingStep[];
  readonly requiredStepNames: readonly string[];
}

const TEMPORAL_COMMAND_PATTERN = /\b(date|time|timestamp|now)\b/i;

function assertToolingStep(step: ToolingStep, contextLabel: string): void {
  if (step.name.trim().length === 0) {
    throw new Error(`${contextLabel}.name must not be empty.`);
  }
  if (step.command.trim().length === 0) {
    throw new Error(`${contextLabel}.command must not be empty.`);
  }
  if (TEMPORAL_COMMAND_PATTERN.test(step.command)) {
    throw new Error(`${contextLabel}.command appears temporal and is not deterministic.`);
  }
}

function compareSteps(left: ToolingStep, right: ToolingStep): number {
  if (left.required !== right.required) {
    return left.required ? -1 : 1;
  }
  return left.name.localeCompare(right.name);
}

export class ToolingPolicy {
  private readonly deterministicSteps: readonly ToolingStep[];
  private readonly featureFlags: FeatureFlags;

  constructor(
    steps: readonly ToolingStep[],
    overrides: Readonly<Partial<Record<FeatureFlagKey, boolean>>> = {},
  ) {
    for (const [index, step] of steps.entries()) {
      assertToolingStep(step, `steps[${index}]`);
    }
    this.deterministicSteps = deepFreeze([...steps].sort(compareSteps));
    this.featureFlags = createFeatureFlags(overrides);
  }

  getSteps(): readonly ToolingStep[] {
    return this.deterministicSteps;
  }

  getFeatureFlags(): FeatureFlags {
    return this.featureFlags;
  }

  createSmokePlan(): ToolingSmokePlan {
    const steps = this.getSteps().filter((step) => {
      if (step.required) {
        return true;
      }
      return this.featureFlags.allowExperimentalWorkers;
    });
    const requiredStepNames = steps
      .filter((step) => step.required)
      .map((step) => step.name)
      .sort((left, right) => left.localeCompare(right));
    return {
      steps,
      requiredStepNames,
    };
  }
}
