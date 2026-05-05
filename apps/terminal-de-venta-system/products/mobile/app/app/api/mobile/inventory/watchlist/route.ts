import { mobileDataPlaneJson } from "@/lib/prisma-app/mobile-data-plane";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  return mobileDataPlaneJson("inventory_watchlist");
}
