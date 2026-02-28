import { ACTIVITY_RESPONSE_FIXTURE, ActivityQueryResponseSchema } from "@hitech/contracts";
import { NextResponse } from "next/server";
import { validateRoutePayload } from "../../../lib/api/route-contract";

export async function GET(): Promise<Response> {
  const payload = validateRoutePayload(
    ActivityQueryResponseSchema,
    ACTIVITY_RESPONSE_FIXTURE,
    "api.activity"
  );
  return NextResponse.json(payload, { status: 200 });
}
