import { NextResponse } from "next/server";

import { getActorFromHeaders } from "@/lib/request-context";
import { getRecordByToken, listRecordSubresources, updateRecord } from "@/lib/services/records";

interface RouteContext {
  params: Promise<{ token: string }>;
}

export async function GET(_request: Request, context: RouteContext) {
  const { token } = await context.params;
  const record = await getRecordByToken(token);
  if (!record) {
    return NextResponse.json({ error: "Token not found" }, { status: 404 });
  }
  const details = await listRecordSubresources(record.id);
  return NextResponse.json({ record, ...details });
}

export async function PATCH(request: Request, context: RouteContext) {
  const { token } = await context.params;
  const record = await getRecordByToken(token);
  if (!record) {
    return NextResponse.json({ error: "Token not found" }, { status: 404 });
  }

  try {
    const body = (await request.json()) as {
      fields: Record<string, unknown>;
      stepId?: string;
      state?:
        | "draft"
        | "submitted"
        | "in_review"
        | "awaiting_update"
        | "approved"
        | "rejected"
        | "dispatched"
        | "synced"
        | "failed";
    };

    const actor = await getActorFromHeaders();
    const updated = await updateRecord({
      recordId: record.id,
      actor: {
        ...actor,
        token
      },
      fields: body.fields ?? {},
      stepId: body.stepId,
      state: body.state
    });

    return NextResponse.json({ record: updated });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Token update failed"
      },
      { status: 400 }
    );
  }
}
