import { NextResponse } from "next/server";
import {
  evaluateClientCapability,
  envOverrideEnabled,
  hasDebugToken,
  isProductionBuild,
  parseCapabilityMode
} from "../../../../lib/scene-studio/scene-access";
import { evaluateApiGate, notFoundResponse } from "../_lib/security";

export async function GET(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed || isProductionBuild()) {
    return notFoundResponse();
  }

  const url = new URL(request.url);
  const requestedMode = parseCapabilityMode(url.searchParams.get("requestedMode"));

  const capability = evaluateClientCapability({
    requestedMode,
    debugToken: gate.debugToken || hasDebugToken(url.searchParams.get("debug")),
    envOverride: envOverrideEnabled(),
    viewportWidth: Number(url.searchParams.get("viewport") ?? "1280"),
    prefersReducedMotion: url.searchParams.get("reducedMotion") === "1",
    lowPerf: url.searchParams.get("lowPerf") === "1"
  });

  return NextResponse.json(capability, { status: 200 });
}
