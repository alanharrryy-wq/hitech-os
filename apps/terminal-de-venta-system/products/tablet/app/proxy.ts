import { NextResponse, type NextRequest } from "next/server";

/**
 * CUSTOMER_SURFACE_REDUCTION_1507
 * Defense in depth: retired internal Tablet routes remain unavailable even if
 * a future merge accidentally recreates a page directory.
 *
 * Chart Lab is a separate product/runtime and is intentionally outside this matcher.
 */
const RETIRED_TABLET_ROUTE_PREFIXES = [
  "/events/outbox",
  "/prisma-pulse",
  "/prisma-dark-pos-reference",
  "/prisma-visual-catalog",
  "/referencia-visual",
  "/release-gate",
  "/screen-standard-preview",
  "/tablet-lab",
  "/visual-os"
] as const;

/**
 * TABLET_LAB_LOCAL_GATE_1607
 * Tablet Lab remains a retired customer route, but its historical source may run
 * on localhost during non-production development. Public and production requests
 * continue to receive the same hard 404 used by the customer-surface contract.
 */
const LOCAL_TABLET_LAB_ROUTE = "/tablet-lab";
const LOCAL_TABLET_LAB_HOSTS = new Set(["localhost", "127.0.0.1", "::1"]);

function requestHostname(request: NextRequest) {
  const host = ((request.headers as Headers).get("host") || "").trim().toLowerCase();
  if (host.startsWith("[")) {
    const closingBracket = host.indexOf("]");
    return closingBracket > 0 ? host.slice(1, closingBracket) : host;
  }
  return host.split(":", 1)[0] || "";
}

function nextWithRequestHeaders(headers: Headers) {
  const next = NextResponse.next as unknown as (init: {
    request: { headers: Headers };
  }) => ReturnType<typeof NextResponse.next>;
  return next({ request: { headers } });
}

function isLocalTabletLabRequest(request: NextRequest, pathname: string) {
  const isTabletLabPath = pathname === LOCAL_TABLET_LAB_ROUTE || pathname.startsWith(`${LOCAL_TABLET_LAB_ROUTE}/`);
  if (!isTabletLabPath || process.env.NODE_ENV === "production") return false;
  const hostname = requestHostname(request);
  return LOCAL_TABLET_LAB_HOSTS.has(hostname);
}

function isRetiredTabletRoute(pathname: string) {
  return RETIRED_TABLET_ROUTE_PREFIXES.some((route) => pathname === route || pathname.startsWith(`${route}/`));
}

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname || "/";
  const localTabletLab = isLocalTabletLabRequest(request, pathname);

  if (isRetiredTabletRoute(pathname) && !localTabletLab) {
    return new Response("Not Found", {
      status: 404,
      headers: {
        "content-type": "text/plain; charset=utf-8",
        "x-prisma-route": pathname,
        "x-prisma-retired-route": "true",
        "x-robots-tag": "noindex, nofollow"
      }
    });
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-prisma-route", pathname);

  if (localTabletLab) {
    requestHeaders.set("x-prisma-internal-lab", "tablet-lab");
    const response = nextWithRequestHeaders(requestHeaders);
    response.headers.set("x-prisma-internal-lab", "tablet-lab");
    response.headers.set("x-robots-tag", "noindex, nofollow");
    response.headers.set("cache-control", "no-store");
    return response;
  }

  return nextWithRequestHeaders(requestHeaders);
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)"]
};
