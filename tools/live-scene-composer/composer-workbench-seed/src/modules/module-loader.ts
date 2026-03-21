import type { ModuleContextLike, ModuleInstance } from "../contracts";
import { WorkbenchEvents } from "../core/event-bus";
import { ModuleRegistry } from "./module-registry";

export interface ModuleLoadReport {
  readonly initialized: readonly string[];
  readonly failed: readonly string[];
  readonly skipped: readonly string[];
}

export interface ModuleLoaderOptions {
  readonly registry: ModuleRegistry;
  readonly createContext: (moduleId: string) => ModuleContextLike;
  readonly onModuleInitialized?: (moduleId: string, instance: ModuleInstance) => void;
}

export class ModuleLoader {
  private readonly registry: ModuleRegistry;
  private readonly createContext: (moduleId: string) => ModuleContextLike;
  private readonly onModuleInitialized?: (
    moduleId: string,
    instance: ModuleInstance,
  ) => void;

  private readonly instances = new Map<string, ModuleInstance>();
  private readonly initOrder: string[] = [];

  public constructor(options: ModuleLoaderOptions) {
    this.registry = options.registry;
    this.createContext = options.createContext;
    this.onModuleInitialized = options.onModuleInitialized;
  }

  public async initializeAll(): Promise<ModuleLoadReport> {
    const initialized: string[] = [];
    const failed = new Set<string>();
    const skipped = new Set<string>();
    const visiting = new Set<string>();
    const resolved = new Set<string>();

    const initializeModule = async (moduleId: string): Promise<boolean> => {
      if (resolved.has(moduleId)) {
        return true;
      }

      if (failed.has(moduleId) || skipped.has(moduleId)) {
        return false;
      }

      if (visiting.has(moduleId)) {
        this.registry.setStatus(moduleId, "failed", "dependency cycle detected");
        failed.add(moduleId);
        return false;
      }

      const registration = this.registry.getRegistration(moduleId);
      if (!registration) {
        failed.add(moduleId);
        return false;
      }

      visiting.add(moduleId);

      const { manifest } = registration;
      if (!manifest.enabledByDefault) {
        this.registry.setStatus(moduleId, "disabled", "module disabled by manifest");
        skipped.add(moduleId);
        visiting.delete(moduleId);
        return false;
      }

      for (const dependency of manifest.dependencies) {
        if (!this.registry.has(dependency)) {
          this.registry.setStatus(
            moduleId,
            "failed",
            `missing dependency '${dependency}'`,
          );
          failed.add(moduleId);
          visiting.delete(moduleId);
          return false;
        }

        const dependencyOk = await initializeModule(dependency);
        if (!dependencyOk) {
          this.registry.setStatus(
            moduleId,
            "failed",
            `dependency '${dependency}' failed`,
          );
          failed.add(moduleId);
          visiting.delete(moduleId);
          return false;
        }
      }

      visiting.delete(moduleId);

      if (this.instances.has(moduleId)) {
        resolved.add(moduleId);
        return true;
      }

      try {
        const instance = registration.create();
        const context = this.createContext(moduleId);
        await instance.initialize(context);

        this.instances.set(moduleId, instance);
        this.initOrder.push(moduleId);
        this.registry.setStatus(moduleId, "initialized", "module initialized");
        initialized.push(moduleId);
        resolved.add(moduleId);
        this.onModuleInitialized?.(moduleId, instance);

        context.emitEvent(WorkbenchEvents.MODULE_INITIALIZED, {
          moduleId,
          owner: instance.manifest.owner,
        });

        return true;
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        this.registry.setStatus(moduleId, "failed", message);
        failed.add(moduleId);

        const context = this.createContext(moduleId);
        context.emitEvent(WorkbenchEvents.MODULE_FAILED, {
          moduleId,
          message,
        });

        return false;
      }
    };

    for (const registration of this.registry.listRegistrations()) {
      await initializeModule(registration.manifest.id);
    }

    return {
      initialized,
      failed: Array.from(failed).sort((left, right) => left.localeCompare(right)),
      skipped: Array.from(skipped).sort((left, right) => left.localeCompare(right)),
    };
  }

  public getInstance(moduleId: string): ModuleInstance | undefined {
    return this.instances.get(moduleId);
  }

  public listInitializedModules(): readonly string[] {
    return this.initOrder.slice();
  }

  public async shutdownAll(): Promise<void> {
    const reverseOrder = this.initOrder.slice().reverse();
    for (const moduleId of reverseOrder) {
      const instance = this.instances.get(moduleId);
      if (!instance || !instance.shutdown) {
        continue;
      }

      await instance.shutdown();
      this.registry.setStatus(moduleId, "skipped", "module shut down");
    }

    this.instances.clear();
    this.initOrder.length = 0;
  }
}
