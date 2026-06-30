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

  export type CSSProperties = Record<string, string | number | undefined>;

  export type MutableRefObject<T> = {
    current: T;
  };

  export type FormEvent<T = any> = {
    preventDefault(): void;
    currentTarget: T;
    target: any;
  };

  export type ChangeEvent<T = any> = {
    target: T;
    currentTarget: T;
  };

  export type PointerEvent<T = any> = {
    pointerId: number;
    clientX: number;
    clientY: number;
    currentTarget: T & {
      setPointerCapture?: (pointerId: number) => void;
      releasePointerCapture?: (pointerId: number) => void;
    };
    target: any;
    preventDefault(): void;
    stopPropagation?: () => void;
  };

  export function useState<T>(
    initialState: T | (() => T)
  ): [T, (value: T | ((previous: T) => T)) => void];

  export function useEffect(
    effect: () => void | (() => void),
    deps?: any[]
  ): void;

  export function useMemo<T>(
    factory: () => T,
    deps?: any[]
  ): T;

  export function useRef<T>(
    initialValue: T
  ): MutableRefObject<T>;

  export function useRef<T = undefined>(): MutableRefObject<T | undefined>;
}

declare module "react-dom" {
  export function createPortal(children: any, container: any): any;
}

declare module "next/server" {
  export type NextRequest = {
    headers: HeadersInit;
    nextUrl: {
      pathname: string;
    };
  };

  export class NextResponse {
    static json(body: any, init?: any): any;
    static next(init?: any): any;
  }
}
