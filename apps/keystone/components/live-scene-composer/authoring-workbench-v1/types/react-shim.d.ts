declare module "react" {
  export type ReactNode = any;
  export type Dispatch<A> = (value: A) => void;
  export interface Context<T> {
    Provider: any;
    displayName?: string;
  }
  export function createContext<T>(defaultValue: T): Context<T>;
  export function useContext<T>(context: Context<T>): T;
  export function useMemo<T>(factory: () => T, deps: readonly unknown[]): T;
  export function useReducer<S, A>(reducer: (state: S, action: A) => S, initialState: S): [S, Dispatch<A>];
  export function useState<S>(initialState: S): [S, Dispatch<S>];
  export function useEffect(effect: () => void | (() => void), deps?: readonly unknown[]): void;
}

declare module "react/jsx-runtime" {
  export const Fragment: any;
  export function jsx(type: any, props: any, key?: any): any;
  export function jsxs(type: any, props: any, key?: any): any;
}

declare namespace JSX {
  interface IntrinsicElements {
    article: any;
    aside: any;
    button: any;
    code: any;
    div: any;
    h1: any;
    h2: any;
    h3: any;
    h4: any;
    header: any;
    input: any;
    label: any;
    li: any;
    main: any;
    option: any;
    p: any;
    pre: any;
    section: any;
    select: any;
    small: any;
    span: any;
    strong: any;
    ul: any;
  }
}
