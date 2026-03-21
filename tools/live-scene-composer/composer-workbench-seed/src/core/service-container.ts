export type ServiceFactory<T = unknown> = () => T;

type FactoryDefinition =
  | { readonly mode: "transient"; readonly factory: ServiceFactory }
  | { readonly mode: "singleton"; readonly factory: ServiceFactory };

export class ServiceContainer {
  private readonly services = new Map<string, unknown>();
  private readonly factories = new Map<string, FactoryDefinition>();
  private readonly singletonCache = new Map<string, unknown>();

  public register(name: string, service: unknown): void {
    this.assertAvailable(name);
    this.services.set(name, service);
  }

  public registerFactory(name: string, factory: ServiceFactory): void {
    this.assertAvailable(name);
    this.factories.set(name, { mode: "transient", factory });
  }

  public registerSingletonFactory(name: string, factory: ServiceFactory): void {
    this.assertAvailable(name);
    this.factories.set(name, { mode: "singleton", factory });
  }

  public get<T = unknown>(name: string): T | undefined {
    if (this.services.has(name)) {
      return this.services.get(name) as T;
    }

    if (this.singletonCache.has(name)) {
      return this.singletonCache.get(name) as T;
    }

    const definition = this.factories.get(name);
    if (!definition) {
      return undefined;
    }

    const instance = definition.factory();
    if (definition.mode === "singleton") {
      this.singletonCache.set(name, instance);
    }
    return instance as T;
  }

  public require<T = unknown>(name: string): T {
    const service = this.get<T>(name);
    if (service === undefined) {
      throw new Error(`Service '${name}' is not registered`);
    }
    return service;
  }

  public has(name: string): boolean {
    return (
      this.services.has(name) ||
      this.factories.has(name) ||
      this.singletonCache.has(name)
    );
  }

  public unregister(name: string): void {
    this.services.delete(name);
    this.factories.delete(name);
    this.singletonCache.delete(name);
  }

  public clear(): void {
    this.services.clear();
    this.factories.clear();
    this.singletonCache.clear();
  }

  public getAllNames(): readonly string[] {
    const names = new Set<string>();
    for (const name of this.services.keys()) {
      names.add(name);
    }
    for (const name of this.factories.keys()) {
      names.add(name);
    }
    for (const name of this.singletonCache.keys()) {
      names.add(name);
    }
    return Array.from(names).sort((left, right) => left.localeCompare(right));
  }

  private assertAvailable(name: string): void {
    if (this.services.has(name) || this.factories.has(name)) {
      throw new Error(`Service '${name}' is already registered`);
    }
  }
}
