import { getFormsServerEnv } from "@/lib/config/env";

interface RouteContext {
  params: Promise<{ path: string[] }>;
}

const FORWARDED_HEADERS = [
  "accept",
  "content-type",
  "x-actor-role",
  "x-actor-label",
  "x-actor-id",
  "x-authenticated",
  "x-flow-token",
  "x-form-type"
] as const;

function buildForwardHeaders(request: Request): Headers {
  const headers = new Headers();

  for (const headerName of FORWARDED_HEADERS) {
    const value = request.headers.get(headerName);
    if (value) {
      headers.set(headerName, value);
    }
  }

  return headers;
}

async function forward(request: Request, context: RouteContext): Promise<Response> {
  const { engineApiBaseUrl } = getFormsServerEnv();
  const { path } = await context.params;

  if (!Array.isArray(path) || path.length === 0) {
    return new Response(JSON.stringify({ error: "Missing gateway path" }), {
      status: 400,
      headers: { "content-type": "application/json" }
    });
  }

  const incomingUrl = new URL(request.url);
  const targetUrl = new URL(`${engineApiBaseUrl}/api/${path.join("/")}`);
  targetUrl.search = incomingUrl.search;

  const method = request.method.toUpperCase();
  const init: RequestInit = {
    method,
    headers: buildForwardHeaders(request),
    cache: "no-store"
  };

  if (method !== "GET" && method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  const upstream = await fetch(targetUrl, init);
  const responseHeaders = new Headers();
  const contentType = upstream.headers.get("content-type");
  if (contentType) responseHeaders.set("content-type", contentType);

  return new Response(await upstream.arrayBuffer(), {
    status: upstream.status,
    headers: responseHeaders
  });
}

export async function GET(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function POST(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function PATCH(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function PUT(request: Request, context: RouteContext) {
  return forward(request, context);
}

export async function DELETE(request: Request, context: RouteContext) {
  return forward(request, context);
}

