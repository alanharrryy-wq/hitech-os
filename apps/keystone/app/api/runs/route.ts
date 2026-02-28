import { RUNS_RESPONSE_FIXTURE, RunsQueryResponseSchema } from "@hitech/contracts";
import { NextResponse } from "next/server";
import { validateRoutePayload } from "../../../lib/api/route-contract";

export async function GET(): Promise<Response> {
  const payload = validateRoutePayload(RunsQueryResponseSchema, RUNS_RESPONSE_FIXTURE, "api.runs");
  return NextResponse.json(payload, { status: 200 });
}
