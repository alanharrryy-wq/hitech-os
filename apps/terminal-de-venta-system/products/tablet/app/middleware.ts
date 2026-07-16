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

function isRetiredTabletRoute(pathname: string) {
  return RETIRED_TABLET_ROUTE_PREFIXES.some((route) => pathname === route || pathname.startsWith(`${route}/`));
}

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname || "/";

  if (isRetiredTabletRoute(pathname)) {
    return new NextResponse("Not Found", {
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
  return NextResponse.next({ request: { headers: requestHeaders } });
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)"]
};
