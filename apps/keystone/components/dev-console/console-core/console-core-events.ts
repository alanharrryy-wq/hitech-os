"use client";

const LISTENER_REGISTRY_KEY = "__HITECH_DEV_CONSOLE_LISTENER_REGISTRY__";

type ListenerRegistry = Record<string, number>;

function getListenerRegistry(): ListenerRegistry {
  if (typeof window === "undefined") {
    return {};
  }

  const globalWindow = window as Window & { [LISTENER_REGISTRY_KEY]?: ListenerRegistry };
  if (!globalWindow[LISTENER_REGISTRY_KEY]) {
    globalWindow[LISTENER_REGISTRY_KEY] = {};
  }
  return globalWindow[LISTENER_REGISTRY_KEY] as ListenerRegistry;
}

function incrementListener(eventName: string): void {
  const registry = getListenerRegistry();
  registry[eventName] = (registry[eventName] ?? 0) + 1;
}

function decrementListener(eventName: string): void {
  const registry = getListenerRegistry();
  registry[eventName] = Math.max(0, (registry[eventName] ?? 0) - 1);
}

export function registerConsoleEventListener(
  eventName: keyof WindowEventMap | string,
  listener: EventListenerOrEventListenerObject,
  options?: AddEventListenerOptions
): () => void {
  if (typeof window === "undefined") {
    return () => undefined;
  }

  window.addEventListener(eventName, listener, options);
  incrementListener(eventName);

  return () => {
    window.removeEventListener(eventName, listener, options);
    decrementListener(eventName);
  };
}

export function dispatchConsoleEvent<TDetail>(eventName: string, detail: TDetail): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return window.dispatchEvent(new CustomEvent(eventName, { detail }));
}

export function getConsoleEventListenerCount(eventName: string): number {
  const registry = getListenerRegistry();
  return registry[eventName] ?? 0;
}

export function snapshotConsoleEventListenerCounts(): Readonly<Record<string, number>> {
  const registry = getListenerRegistry();
  return { ...registry };
}
