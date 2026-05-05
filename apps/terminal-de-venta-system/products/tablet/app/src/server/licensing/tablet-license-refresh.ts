import { NextResponse } from "next/server";
import { getLicenseRefreshStatus, refreshLocalLicenseFromRemote } from "../../../../../../shared/licensing";

export function getTabletLicenseRefreshStatus() {
  return getLicenseRefreshStatus();
}

export async function refreshTabletLicense() {
  return refreshLocalLicenseFromRemote();
}

export function tabletLicenseRefreshOk<T>(data: T, meta: Record<string, unknown> = {}) {
  return NextResponse.json({ ok: true, data, meta });
}
