import type {
  SelectionRef,
  SelectionState,
  Unsubscribe,
} from "../contracts";
import { EventBus, WorkbenchEvents } from "../core/event-bus";

export class SelectionProvider {
  private readonly listeners = new Set<() => void>();
  private selection: SelectionState;

  public constructor(
    initialSelection?: SelectionState,
    private readonly eventBus?: EventBus,
  ) {
    this.selection =
      initialSelection ?? {
        current: null,
        origin: "seed",
        updatedAtUtc: new Date().toISOString(),
      };
  }

  public getSelection(): SelectionState {
    return { ...this.selection };
  }

  public select(ref: SelectionRef, origin = "workbench"): void {
    this.selection = {
      current: ref,
      origin,
      updatedAtUtc: new Date().toISOString(),
    };
    this.eventBus?.publish(WorkbenchEvents.SELECTION_CHANGED, this.selection);
    this.notify();
  }

  public clear(origin = "workbench"): void {
    this.selection = {
      current: null,
      origin,
      updatedAtUtc: new Date().toISOString(),
    };
    this.eventBus?.publish(WorkbenchEvents.SELECTION_CHANGED, this.selection);
    this.notify();
  }

  public subscribe(listener: () => void): Unsubscribe {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener();
    }
  }
}
