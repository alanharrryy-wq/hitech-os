import { fail, ok, toBackofficeError } from "@/lib/backoffice/api-response";
import { guardPcFeatureForApi } from "@/server/licensing/pc-license-api";
import { claimDurablePcDevice, getDurableDeviceClaim, revokeDurablePcDevice } from "@/server/services/device-claims.service";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const deviceId = new URL(request.url).searchParams.get("deviceId") ?? "";
    if (!deviceId.trim()) return fail("DEVICE_ID_REQUIRED", "Falta deviceId.", 400);
    const device = await getDurableDeviceClaim(deviceId);
    if (!device) return fail("DEVICE_NOT_FOUND", "No existe el dispositivo solicitado.", 404);
    return ok({ device }, { endpoint: "GET /api/backoffice/devices/claims", persistence: "DeviceHeartbeat", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "DEVICE_ID_REQUIRED") return fail("DEVICE_ID_REQUIRED", "Falta un identificador válido para el dispositivo.", 400);
    return toBackofficeError(error);
  }
}

export async function POST(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const device = await claimDurablePcDevice(body);
    return ok({ device, claimed: true }, { endpoint: "POST /api/backoffice/devices/claims", persistence: "DeviceHeartbeat", wave: 3 }, { status: 201 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "DEVICE_ID_REQUIRED") return fail("DEVICE_ID_REQUIRED", "Falta un identificador válido para el dispositivo.", 400);
    return toBackofficeError(error);
  }
}

export async function DELETE(request: Request) {
  try {
    const licenseGate = await guardPcFeatureForApi("pc.open");
    if (licenseGate) return licenseGate;
    const body = await request.json().catch(() => { throw new Error("INVALID_JSON_BODY"); });
    const device = await revokeDurablePcDevice(body);
    if (!device) return fail("DEVICE_NOT_FOUND", "No existe el dispositivo solicitado.", 404);
    return ok({ device, revoked: true }, { endpoint: "DELETE /api/backoffice/devices/claims", persistence: "DeviceHeartbeat", wave: 3 });
  } catch (error) {
    if (error instanceof Error && error.message === "INVALID_JSON_BODY") return fail("INVALID_JSON_BODY", "El cuerpo JSON no es válido.", 400);
    if (error instanceof Error && error.message === "DEVICE_ID_REQUIRED") return fail("DEVICE_ID_REQUIRED", "Falta un identificador válido para el dispositivo.", 400);
    return toBackofficeError(error);
  }
}
