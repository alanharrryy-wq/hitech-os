import type {
  MutationResult,
  WorkbenchLayoutModel,
} from "../contracts";
import {
  ComposerWorkbenchProvider,
  type ComposerWorkbenchProviderOptions,
} from "../providers/composer-workbench-provider";
import { buildModuleBoard, type ModuleBoardModel } from "./surfaces/module-board";
import { buildWorkbenchLayout } from "./workbench-layout";

export interface ComposerWorkbenchViewModel {
  readonly layout: WorkbenchLayoutModel;
  readonly moduleBoard: ModuleBoardModel;
}

export class ComposerWorkbench {
  private latestMutation: MutationResult | undefined;

  public constructor(public readonly provider: ComposerWorkbenchProvider) {}

  public async initialize(): Promise<void> {
    await this.provider.initializeModules();
  }

  public async shutdown(): Promise<void> {
    await this.provider.shutdownModules();
  }

  public async requestMutation(intent: Parameters<ComposerWorkbenchProvider["requestMutation"]>[0]): Promise<MutationResult> {
    const result = await this.provider.requestMutation(intent);
    this.latestMutation = result;
    return result;
  }

  public getViewModel(): ComposerWorkbenchViewModel {
    const modules = this.provider.getModuleSnapshots();
    const routeStatus = this.provider.getRouteStatus();

    return {
      moduleBoard: buildModuleBoard(modules),
      layout: buildWorkbenchLayout({
        modules,
        selection: this.provider.getSelection(),
        latestMutation: this.latestMutation,
        safeMode: routeStatus.safeMode,
        bridgeRoute: routeStatus.bridgeRoute,
        workspaceStatus: routeStatus.workspaceState,
      }),
    };
  }
}

export function createComposerWorkbench(
  options: ComposerWorkbenchProviderOptions,
): ComposerWorkbench {
  return new ComposerWorkbench(new ComposerWorkbenchProvider(options));
}
