import type {
  CommandLike,
  LifecycleResult,
  ModuleContextLike,
  ModuleManifest,
} from "../contracts";

export abstract class ModuleBase {
  protected readonly disposables: Array<() => void> = [];

  protected constructor(public readonly manifest: ModuleManifest) {}

  public abstract initialize(context: ModuleContextLike): LifecycleResult;

  public shutdown(): LifecycleResult {
    for (const dispose of this.disposables.splice(0, this.disposables.length)) {
      dispose();
    }
  }

  protected registerCommand(
    context: ModuleContextLike,
    commandName: string,
    command: CommandLike,
  ): void {
    context.registerCommand(commandName, command);
    this.disposables.push(() => {
      context.unregisterCommand(commandName);
    });
  }

  protected subscribeEvent<TPayload = unknown>(
    context: ModuleContextLike,
    event: string,
    handler: (payload: TPayload) => void,
  ): void {
    const unsubscribe = context.subscribeEvent(event, handler);
    this.disposables.push(unsubscribe);
  }

  protected emitEvent<TPayload = unknown>(
    context: ModuleContextLike,
    event: string,
    payload?: TPayload,
  ): void {
    context.emitEvent(event, payload);
  }
}
