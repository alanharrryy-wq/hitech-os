import { NextResponse } from "next/server";

import { getActorFromHeaders } from "@/lib/request-context";
import { retryDispatchJob } from "@/lib/services/actions";

interface RouteContext {
  params: Promise<{ jobId: string }>;
}

export async function POST(_request: Request, context: RouteContext) {
  const { jobId } = await context.params;
  try {
    const actor = await getActorFromHeaders();
    const result = await retryDispatchJob(jobId, actor);
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Retry failed"
      },
      { status: 400 }
    );
  }
}
