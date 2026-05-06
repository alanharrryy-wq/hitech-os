import { NextResponse } from "next/server";
import { getLicenseRefreshStatus, refreshLocalLicenseFromRemote } from "../../../../../../shared/licensing";

export function getPcLicenseRefreshStatus() {
  return getLicenseRefreshStatus();
}

export async function refreshPcLicense() {
  return refreshLocalLicenseFromRemote();
}

export function pcLicenseRefreshOk<T>(data: T, meta: Record<string, unknown> = {}) {
  return NextResponse.json({ ok: true, data, meta });
}
