import { NextResponse } from "next/server";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { runTriDbSyncNow } from "../../../../../src/server/services/tri-db-command.service";

export const dynamic = "force-dynamic";

export async function POST() {
  const prismaLicenseGate = await guardPcFeatureForApi("sync.managed");
  if (prismaLicenseGate) return prismaLicenseGate;

  try {
    const result = await runTriDbSyncNow();
    return NextResponse.json(result, { status: result.ok ? 200 : 500 });
  } catch (error: any) {
    return NextResponse.json(
      {
        ok: false,
        status: "BLOCKED",
        message: error?.message ?? String(error)
      },
      { status: 500 }
    );
  }
}
