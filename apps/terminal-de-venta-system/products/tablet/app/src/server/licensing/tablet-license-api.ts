import { NextResponse } from "next/server";
import { licenseDeniedEnvelope } from "../../../../../../shared/licensing";
import { resolveTabletFeature } from "./tablet-license-service";

function tabletLicenseGateResponse(resolution: ReturnType<typeof resolveTabletFeature>) {
  return NextResponse.json(licenseDeniedEnvelope(resolution), { status: resolution.enforcement === "hard_deny" ? 423 : 403 });
}

export async function guardTabletFeatureForApi(featureKey: string): Promise<NextResponse | null> {
  const resolution = resolveTabletFeature(featureKey);
  if (resolution.allowed) return null;
  return tabletLicenseGateResponse(resolution);
}

export async function guardTabletLocalPosForApi(): Promise<NextResponse | null> {
  const resolution = resolveTabletFeature("pos.sale.complete");
  if (resolution.allowed) return null;
  return tabletLicenseGateResponse(resolution);
}

export function tabletLicenseOk<T>(data: T, meta: Record<string, unknown> = {}) {
  return NextResponse.json({ ok: true, data, meta });
}
