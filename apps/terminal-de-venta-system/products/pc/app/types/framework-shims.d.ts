declare namespace JSX {
  interface ElementChildrenAttribute { children: {}; }
  interface IntrinsicAttributes { key?: any; }
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

declare const process: { env: Record<string, string | undefined>; cwd(): string };

declare module "next/server" {
  export class NextResponse {
    static json(body: any, init?: any): any;
  }
}

// PRISMA 04F: no local react module shim; @types/react owns hook exports.
