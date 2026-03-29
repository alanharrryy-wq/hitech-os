export type MirrorListener<TValue> = (value: TValue, source: string) => void;

export interface MirrorState<TValue> {
  readonly value: TValue;
  readonly source: string;
  readonly updatedAt: string;
}

export interface MirrorStore<TValue> {
  getState(): MirrorState<TValue>;
  setValue(value: TValue, source: string): void;
  patch(transform: (current: TValue) => TValue, source: string): void;
  subscribe(listener: MirrorListener<TValue>): () => void;
}

export function createMirrorStore<TValue>(
  initialValue: TValue,
  initialSource = "init"
): MirrorStore<TValue> {
  let state: MirrorState<TValue> = {
    value: initialValue,
    source: initialSource,
    updatedAt: new Date(0).toISOString()
  };
  const listeners = new Set<MirrorListener<TValue>>();

  function emit(): void {
    const snapshot = state;
    for (const listener of listeners) {
      listener(snapshot.value, snapshot.source);
    }
  }

  function setValue(value: TValue, source: string): void {
    state = {
      value,
      source,
      updatedAt: new Date().toISOString()
    };
    emit();
  }

  function patch(transform: (current: TValue) => TValue, source: string): void {
    setValue(transform(state.value), source);
  }

  function getState(): MirrorState<TValue> {
    return state;
  }

  function subscribe(listener: MirrorListener<TValue>): () => void {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  }

  return {
    getState,
    setValue,
    patch,
    subscribe
  };
}
