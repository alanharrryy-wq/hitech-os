declare namespace JSX {
  interface ElementChildrenAttribute { children: {}; }
  interface IntrinsicAttributes { key?: any; }
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare const process: { env: Record<string, string | undefined>; cwd(): string };

declare module "react" {
  export type ReactNode = any;
  export type FormEvent<T = any> = { preventDefault(): void; currentTarget: T; target: any };
  export type ChangeEvent<T = any> = { target: T; currentTarget: T };
  export function useState<T>(initialState: T | (() => T)): [T, (value: T | ((previous: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useMemo<T>(factory: () => T, deps?: any[]): T;
}

declare module "next/server" {
  export class NextResponse {
    static json(body: any, init?: any): any;
  }
}
