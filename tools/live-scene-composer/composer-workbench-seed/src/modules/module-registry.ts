import type {
  ModuleRegistration,
  ModuleRuntimeSnapshot,
  ModuleStatus,
} from "../contracts";

export class ModuleRegistry {
  private readonly registrations = new Map<string, ModuleRegistration>();
  private readonly runtime = new Map<string, ModuleRuntimeSnapshot>();

  public register(registration: ModuleRegistration): void {
    const { manifest } = registration;

    if (this.registrations.has(manifest.id)) {
      throw new Error(`Module '${manifest.id}' is already registered`);
    }

    this.registrations.set(manifest.id, registration);
    this.runtime.set(manifest.id, {
      id: manifest.id,
      owner: manifest.owner,
      status: "registered",
      dependencies: manifest.dependencies,
      message: "module registered",
    });
  }

  public has(moduleId: string): boolean {
    return this.registrations.has(moduleId);
  }

  public getRegistration(moduleId: string): ModuleRegistration | undefined {
    return this.registrations.get(moduleId);
  }

  public listRegistrations(): readonly ModuleRegistration[] {
    return Array.from(this.registrations.values()).sort((left, right) =>
      left.manifest.id.localeCompare(right.manifest.id),
    );
  }

  public setStatus(
    moduleId: string,
    status: ModuleStatus,
    message?: string,
  ): void {
    const registration = this.registrations.get(moduleId);
    if (!registration) {
      throw new Error(`Module '${moduleId}' is not registered`);
    }

    this.runtime.set(moduleId, {
      id: registration.manifest.id,
      owner: registration.manifest.owner,
      dependencies: registration.manifest.dependencies,
      status,
      message,
    });
  }

  public listRuntimeSnapshots(): readonly ModuleRuntimeSnapshot[] {
    return Array.from(this.runtime.values()).sort((left, right) =>
      left.id.localeCompare(right.id),
    );
  }

  public clear(): void {
    this.registrations.clear();
    this.runtime.clear();
  }
}
