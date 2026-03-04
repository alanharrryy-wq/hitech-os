export const CONTRACT_FIXTURES_PITCH_MODULE_PATH = "./pitch/index.js";

export * from "./activity.js";
export * from "./api.js";
export * from "./evidence.js";
export * from "./filters.js";
export * from "./layout.js";
export * from "./runs.js";
export * from "./widgets.js";

export interface ContractFixturesWiring {
  readonly pitchModulePath: string;
  loadPitchModule(): Promise<unknown>;
}

export const fixtures: ContractFixturesWiring = Object.freeze({
  pitchModulePath: CONTRACT_FIXTURES_PITCH_MODULE_PATH,
  loadPitchModule: () => import("./pitch/index.js")
});
