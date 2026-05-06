import { NextResponse } from "next/server";
import { licenseDeniedEnvelope } from "../../../../../../shared/licensing";
import { resolveTabletFeature } from "./tablet-license-service";

export async function guardTabletFeatureForApi(featureKey: string): Promise<NextResponse | null> {
  const resolution = resolveTabletFeature(featureKey);
  if (resolution.allowed) return null;
  return NextResponse.json(licenseDeniedEnvelope(resolution), { status: resolution.enforcement === "hard_deny" ? 423 : 403 });
}

export function tabletLicenseOk<T>(data: T, meta: Record<string, unknown> = {}) {
  return NextResponse.json({ ok: true, data, meta });
}
