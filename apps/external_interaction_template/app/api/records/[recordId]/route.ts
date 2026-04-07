import { NextResponse } from "next/server";

import { getActorFromHeaders } from "@/lib/request-context";
import { getRecordById, listRecordSubresources, updateRecord } from "@/lib/services/records";

interface RouteContext {
  params: Promise<{ recordId: string }>;
}

export async function GET(_request: Request, context: RouteContext) {
  const { recordId } = await context.params;
  const record = await getRecordById(recordId);
  if (!record) {
    return NextResponse.json({ error: "Record not found" }, { status: 404 });
  }

  const details = await listRecordSubresources(recordId);
  return NextResponse.json({
    record,
    ...details
  });
}

export async function PATCH(request: Request, context: RouteContext) {
  const { recordId } = await context.params;

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
      recordId,
      actor,
      fields: body.fields ?? {},
      stepId: body.stepId,
      state: body.state
    });

    return NextResponse.json({ record: updated });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Record update failed"
      },
      { status: 400 }
    );
  }
}
