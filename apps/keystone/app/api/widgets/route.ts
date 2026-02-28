import { WIDGETS_RESPONSE_FIXTURE, WidgetsQueryResponseSchema } from "@hitech/contracts";
import { NextResponse } from "next/server";
import { validateRoutePayload } from "../../../lib/api/route-contract";

export async function GET(): Promise<Response> {
  const payload = validateRoutePayload(
    WidgetsQueryResponseSchema,
    WIDGETS_RESPONSE_FIXTURE,
    "api.widgets"
  );
  return NextResponse.json(payload, { status: 200 });
}
