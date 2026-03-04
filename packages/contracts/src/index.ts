import { CONTRACT_FIXTURES_PITCH_MODULE_PATH } from "./fixtures/index.js";

export * from "./capabilities.js";
export * from "./domain/pitch/index.js";
export * from "./errors.js";
export * from "./featureFlags.js";
export * from "./fixtures/index.js";
export * from "./health.js";
export * from "./job.js";
export * from "./mission-control/index.js";
export * from "./parsing.js";
export * from "./result.js";
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
  loadDomainModule: () => import("./domain/pitch/index.js"),
  loadFixturesIndexModule: () => import("./fixtures/index.js"),
  loadFixturesModule: () => import("./fixtures/pitch/index.js")
});
