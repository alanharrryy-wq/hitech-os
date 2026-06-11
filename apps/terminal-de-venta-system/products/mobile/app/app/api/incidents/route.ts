import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function redirectWithQuery(request: Request, pathname: string) {
  const source = new URL(request.url);
  const target = new URL(pathname, request.url);
  source.searchParams.forEach((value, key) => target.searchParams.set(key, value));
  return NextResponse.redirect(target, 307);
}

export function GET(request: Request) {
  return redirectWithQuery(request, "/api/mobile/alerts");
}
