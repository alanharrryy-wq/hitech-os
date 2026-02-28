export const CONTRACT_FIXTURES_PITCH_MODULE_PATH = "./pitch/index.js";

export interface ContractFixturesWiring {
  readonly pitchModulePath: string;
  loadPitchModule(): Promise<unknown>;
}

export const fixtures: ContractFixturesWiring = Object.freeze({
  pitchModulePath: CONTRACT_FIXTURES_PITCH_MODULE_PATH,
  loadPitchModule: () => import(CONTRACT_FIXTURES_PITCH_MODULE_PATH)
});
