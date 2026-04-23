import { NextResponse } from "next/server";

import { getActorFromHeaders } from "@/lib/request-context";
import { applyRecordAction } from "@/lib/services/actions";

interface RouteContext {
  params: Promise<{ recordId: string }>;
}

export async function POST(request: Request, context: RouteContext) {
  const { recordId } = await context.params;

  try {
    const body = (await request.json()) as {
      actionId: string;
      note?: string;
      payload?: Record<string, unknown>;
    };

    const actor = await getActorFromHeaders();
    const result = await applyRecordAction({
      recordId,
      actionId: body.actionId,
      actor,
      note: body.note,
      payload: body.payload
    });

    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Action failed"
      },
      { status: 400 }
    );
  }
}
