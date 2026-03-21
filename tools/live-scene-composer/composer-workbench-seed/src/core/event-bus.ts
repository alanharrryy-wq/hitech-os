import type { Unsubscribe } from "../contracts";

export type EventHandler<TPayload = unknown> = (payload: TPayload) => void;

export interface EventRecord {
  readonly event: string;
  readonly payload: unknown;
  readonly atUtc: string;
}

export class EventBus {
  private readonly subscribers = new Map<string, Set<EventHandler>>();
  private readonly history: EventRecord[] = [];

  public constructor(private readonly historyMaxSize = 100) {}

  public subscribe<TPayload = unknown>(
    event: string,
    handler: EventHandler<TPayload>,
  ): Unsubscribe {
    const current = this.subscribers.get(event) ?? new Set<EventHandler>();
    current.add(handler as EventHandler);
    this.subscribers.set(event, current);

    return () => {
      const list = this.subscribers.get(event);
      if (!list) {
        return;
      }
      list.delete(handler as EventHandler);
      if (list.size === 0) {
        this.subscribers.delete(event);
      }
    };
  }

  public publish<TPayload = unknown>(event: string, payload?: TPayload): void {
    const record: EventRecord = {
      event,
      payload,
      atUtc: new Date().toISOString(),
    };
    this.history.push(record);
    if (this.history.length > this.historyMaxSize) {
      this.history.shift();
    }

    const listeners = this.subscribers.get(event);
    if (!listeners || listeners.size === 0) {
      return;
    }

    for (const handler of listeners) {
      try {
        handler(payload);
      } catch (error) {
        // Keep the bus resilient; one handler must not break the rest.
        const message = error instanceof Error ? error.message : String(error);
        // eslint-disable-next-line no-console
        console.error(`[event-bus] handler failed for '${event}': ${message}`);
      }
    }
  }

  public hasSubscribers(event: string): boolean {
    return (this.subscribers.get(event)?.size ?? 0) > 0;
  }

  public getHistory(event?: string): readonly EventRecord[] {
    if (!event) {
      return this.history.slice();
    }
    return this.history.filter((entry) => entry.event === event);
  }

  public clear(): void {
    this.subscribers.clear();
    this.history.length = 0;
  }
}

export const WorkbenchEvents = {
  MODULE_REGISTERED: "module.registered",
  MODULE_INITIALIZED: "module.initialized",
  MODULE_FAILED: "module.failed",
  MODULE_DISABLED: "module.disabled",
  SELECTION_CHANGED: "selection.changed",
  MUTATION_REQUESTED: "mutation.requested",
  MUTATION_RESULT: "mutation.result",
} as const;
