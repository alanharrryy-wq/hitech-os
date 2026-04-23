declare namespace JSX {
  interface ElementChildrenAttribute { children: {}; }
  interface IntrinsicAttributes { key?: any; }
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare const process: { env: Record<string, string | undefined> };

declare module "react" {
  export type ReactNode = any;
}

declare module "next/server" {
  export class NextResponse {
    static json(body: any, init?: any): any;
  }
}
