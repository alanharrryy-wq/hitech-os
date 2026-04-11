import { IncomingMessage, ServerResponse } from "node:http";

export interface HttpContext {
  method: string;
  pathname: string;
  query: URLSearchParams;
}

export interface HttpRouteMatch {
  params: Record<string, string>;
}

export function getHttpContext(request: IncomingMessage): HttpContext {
  const method = (request.method ?? "GET").toUpperCase();
  const url = new URL(request.url ?? "/", "http://127.0.0.1");
  return {
    method,
    pathname: url.pathname,
    query: url.searchParams
  };
}

export async function readJsonBody(request: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];

  for await (const chunk of request) {
    chunks.push(Buffer.from(chunk));
  }

  const text = Buffer.concat(chunks).toString("utf8").trim();
  if (text.length === 0) {
    return {};
  }

  return JSON.parse(text) as unknown;
}

export function writeJson(response: ServerResponse, statusCode: number, payload: unknown): void {
  const content = `${JSON.stringify(payload, null, 2)}\n`;
  response.statusCode = statusCode;
  response.setHeader("content-type", "application/json; charset=utf-8");
  response.setHeader("content-length", Buffer.byteLength(content));
  response.end(content);
}

export function writeNotFound(response: ServerResponse, pathname: string): void {
  writeJson(response, 404, {
    error: "NOT_FOUND",
    message: `No route matched ${pathname}`
  });
}

export function matchPath(pathname: string, template: string): HttpRouteMatch | null {
  const left = pathname.split("/").filter(Boolean);
  const right = template.split("/").filter(Boolean);
  if (left.length !== right.length) {
    return null;
  }

  const params: Record<string, string> = {};

  for (let index = 0; index < left.length; index += 1) {
    const current = left[index];
    const expected = right[index];

    if (expected.startsWith(":")) {
      params[expected.slice(1)] = decodeURIComponent(current);
      continue;
    }

    if (current !== expected) {
      return null;
    }
  }

  return { params };
}
