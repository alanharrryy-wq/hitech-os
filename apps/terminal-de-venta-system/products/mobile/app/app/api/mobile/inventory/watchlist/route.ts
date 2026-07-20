import { mobileDataPlaneJson } from "@/lib/prisma-app/mobile-data-plane";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(request: Request) {
  return mobileDataPlaneJson(request, "inventory_watchlist");
}
