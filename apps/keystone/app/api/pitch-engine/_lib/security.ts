import { NextResponse } from "next/server";
import {
  hasDebugToken,
  isPitchEngineApiAllowed,
  parseCapabilityMode
} from "../../../../lib/scene-studio/scene-access";
import type { CapabilityMode } from "../../../../components/pitch-engine/types";

export interface ApiGateResult {
  readonly allowed: boolean;
  readonly requestedMode: CapabilityMode;
  readonly debugToken: boolean;
}

function readRequestedMode(request: Request): CapabilityMode {
  const url = new URL(request.url);
  const queryMode = url.searchParams.get("requestedMode") ?? url.searchParams.get("mode");
  const headerMode = request.headers.get("x-pitch-capability-mode");
  return parseCapabilityMode(queryMode ?? headerMode);
}

function readDebugToken(request: Request): boolean {
  const url = new URL(request.url);
  const queryDebug = url.searchParams.get("debug");
  const headerDebug = request.headers.get("x-pitch-debug");
  return hasDebugToken(queryDebug ?? headerDebug);
}

export function evaluateApiGate(request: Request): ApiGateResult {
  const requestedMode = readRequestedMode(request);
  const debugToken = readDebugToken(request);
  const access = isPitchEngineApiAllowed({
    debugToken,
    requestedMode
  });

  return {
    allowed: access.allowed,
    requestedMode,
    debugToken
  };
}

export function notFoundResponse(): Response {
  return NextResponse.json({ message: "Not found" }, { status: 404 });
}
