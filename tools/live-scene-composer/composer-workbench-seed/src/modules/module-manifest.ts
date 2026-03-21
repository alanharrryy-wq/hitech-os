import type { ModuleManifest } from "../contracts";

const MODULE_ID_PATTERN = /^[a-z][a-z0-9_\-]{1,63}$/;
const SEMVER_PATTERN = /^\d+\.\d+\.\d+(?:[-+][A-Za-z0-9][A-Za-z0-9.\-]*)?$/;

export type ModuleManifestInput =
  & Pick<ModuleManifest, "id" | "name" | "version" | "owner">
  & Partial<Omit<ModuleManifest, "id" | "name" | "version" | "owner">>;

export function createModuleManifest(input: ModuleManifestInput): ModuleManifest {
  const id = normalizeText(input.id);
  const name = normalizeText(input.name);
  const version = normalizeText(input.version);
  const owner = normalizeText(input.owner);

  if (!MODULE_ID_PATTERN.test(id)) {
    throw new Error(
      "Module manifest field 'id' must match ^[a-z][a-z0-9_-]{1,63}$",
    );
  }

  if (name.length < 2) {
    throw new Error("Module manifest field 'name' must be at least 2 characters");
  }

  if (!SEMVER_PATTERN.test(version)) {
    throw new Error(
      "Module manifest field 'version' must use semver (example: 1.2.3)",
    );
  }

  if (owner.length < 2) {
    throw new Error("Module manifest field 'owner' must be explicitly defined");
  }

  const dependencies = (input.dependencies ?? []).map((dependency) =>
    normalizeText(dependency),
  );

  const uniqueDependencies = Array.from(new Set(dependencies));
  if (uniqueDependencies.length !== dependencies.length) {
    throw new Error("Module manifest field 'dependencies' cannot contain duplicates");
  }

  for (const dependency of uniqueDependencies) {
    if (!MODULE_ID_PATTERN.test(dependency)) {
      throw new Error(
        `Module manifest dependency '${dependency}' does not match id policy`,
      );
    }
    if (dependency === id) {
      throw new Error("Module manifest cannot depend on itself");
    }
  }

  return {
    id,
    name,
    version,
    owner,
    description: normalizeText(input.description ?? ""),
    dependencies: uniqueDependencies,
    enabledByDefault: input.enabledByDefault ?? true,
  };
}

function normalizeText(value: string): string {
  return String(value ?? "").trim();
}
