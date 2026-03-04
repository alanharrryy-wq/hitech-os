import { NextResponse } from "next/server";
import { evaluateApiGate, notFoundResponse } from "./_lib/security";

export async function GET(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  return NextResponse.json(
    {
      ok: true,
      service: "pitch-engine",
      requestedMode: gate.requestedMode,
      debugToken: gate.debugToken,
      timestamp: new Date().toISOString()
    },
    { status: 200 }
  );
}
