import { NextResponse } from "next/server";
import { licenseDeniedEnvelope } from "../../../../../../shared/licensing";
import { resolvePcFeature } from "./pc-license-service";

export async function guardPcFeatureForApi(featureKey: string): Promise<NextResponse | null> {
  const resolution = resolvePcFeature(featureKey);
  if (resolution.allowed) return null;
  return NextResponse.json(licenseDeniedEnvelope(resolution), { status: resolution.enforcement === "hard_deny" ? 423 : 403 });
}

export function pcLicenseOk<T>(data: T, meta: Record<string, unknown> = {}) {
  return NextResponse.json({ ok: true, data, meta });
}
