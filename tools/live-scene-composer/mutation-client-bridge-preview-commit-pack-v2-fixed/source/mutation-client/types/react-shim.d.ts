declare module "react" {
  export function useState<T>(initial: T): [T, (next: T) => void];
  export function useCallback<T extends (...args: any[]) => any>(fn: T, deps: readonly unknown[]): T;
}
