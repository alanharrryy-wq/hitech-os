import type { CommandLike, Unsubscribe } from "../contracts";

export type BeforeExecuteHandler = (
  commandName: string,
  args: readonly unknown[],
) => void;

export type AfterExecuteHandler = (
  commandName: string,
  result: unknown,
) => void;

export interface CommandRecord {
  readonly commandName: string;
  readonly args: readonly unknown[];
  readonly result: unknown;
  readonly atUtc: string;
}

export class CommandDispatcher {
  private readonly commands = new Map<string, CommandLike>();
  private readonly history: CommandRecord[] = [];
  private readonly beforeHandlers = new Set<BeforeExecuteHandler>();
  private readonly afterHandlers = new Set<AfterExecuteHandler>();

  public constructor(private readonly historyMaxSize = 100) {}

  public register(name: string, command: CommandLike): void {
    if (this.commands.has(name)) {
      throw new Error(`Command '${name}' is already registered`);
    }
    this.commands.set(name, command);
  }

  public unregister(name: string): void {
    this.commands.delete(name);
  }

  public has(name: string): boolean {
    return this.commands.has(name);
  }

  public execute<TResult = unknown>(
    name: string,
    ...args: readonly unknown[]
  ): TResult {
    const command = this.commands.get(name);
    if (!command) {
      throw new Error(`Command '${name}' is not registered`);
    }

    if (command.canExecute && !command.canExecute()) {
      throw new Error(`Command '${name}' cannot execute in the current state`);
    }

    for (const handler of this.beforeHandlers) {
      handler(name, args);
    }

    try {
      const result = command.execute(...args);
      this.history.push({
        commandName: name,
        args,
        result,
        atUtc: new Date().toISOString(),
      });
      if (this.history.length > this.historyMaxSize) {
        this.history.shift();
      }

      for (const handler of this.afterHandlers) {
        handler(name, result);
      }

      return result as TResult;
    } catch (error) {
      if (command.onExecuteError) {
        command.onExecuteError(error);
      }
      throw error;
    }
  }

  public onBeforeExecute(handler: BeforeExecuteHandler): Unsubscribe {
    this.beforeHandlers.add(handler);
    return () => {
      this.beforeHandlers.delete(handler);
    };
  }

  public onAfterExecute(handler: AfterExecuteHandler): Unsubscribe {
    this.afterHandlers.add(handler);
    return () => {
      this.afterHandlers.delete(handler);
    };
  }

  public getCommand(name: string): CommandLike | undefined {
    return this.commands.get(name);
  }

  public getHistory(name?: string): readonly CommandRecord[] {
    if (!name) {
      return this.history.slice();
    }
    return this.history.filter((record) => record.commandName === name);
  }

  public clear(): void {
    this.commands.clear();
    this.history.length = 0;
    this.beforeHandlers.clear();
    this.afterHandlers.clear();
  }
}
