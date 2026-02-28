import { CONTRACT_FIXTURES_PITCH_MODULE_PATH } from "./fixtures/index.js";

export * from "./capabilities.js";
export * from "./featureFlags.js";
export * from "./fixtures/index.js";
export * from "./health.js";
export * from "./job.js";
export * from "./version.js";

export const CONTRACT_DOMAIN_PITCH_MODULE_PATH = "./domain/pitch/index.js";
export const CONTRACT_FIXTURES_MODULE_PATH = "./fixtures/index.js";

export interface PitchDomainWiring {
  readonly domainModulePath: string;
  readonly fixturesModulePath: string;
  loadDomainModule(): Promise<unknown>;
  loadFixturesIndexModule(): Promise<unknown>;
  loadFixturesModule(): Promise<unknown>;
}

export const pitch: PitchDomainWiring = Object.freeze({
  domainModulePath: CONTRACT_DOMAIN_PITCH_MODULE_PATH,
  fixturesModulePath: CONTRACT_FIXTURES_PITCH_MODULE_PATH,
  loadDomainModule: () => import(CONTRACT_DOMAIN_PITCH_MODULE_PATH),
  loadFixturesIndexModule: () => import(CONTRACT_FIXTURES_MODULE_PATH),
  loadFixturesModule: () => import(CONTRACT_FIXTURES_PITCH_MODULE_PATH)
});
