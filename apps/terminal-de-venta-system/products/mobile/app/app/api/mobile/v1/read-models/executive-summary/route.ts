import { mobileProjectionJson } from "@/lib/prisma-app/mobile-security";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET(request: Request) {
  return mobileProjectionJson(request, "RM.BUSINESS.EXECUTIVE_SUMMARY");
}
