import { NextResponse } from "next/server";

import { createRecord, listRecords } from "@/lib/services/records";
import { getActorFromHeaders } from "@/lib/request-context";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const schemaId = url.searchParams.get("schemaId") ?? undefined;
  const query = url.searchParams.get("query") ?? undefined;
  const state = (url.searchParams.get("state") ?? undefined) as
    | "draft"
    | "submitted"
    | "in_review"
    | "awaiting_update"
    | "approved"
    | "rejected"
    | "dispatched"
    | "synced"
    | "failed"
    | undefined;

  const records = await listRecords({ schemaId, query, state });
  return NextResponse.json({ records });
}

export async function POST(request: Request) {
  try {
    const actor = await getActorFromHeaders();
    const body = (await request.json()) as {
      schemaId: string;
      title?: string;
      fields?: Record<string, unknown>;
      stepId?: string;
      submit?: boolean;
    };

    const created = await createRecord({
      schemaId: body.schemaId,
      actor,
      title: body.title,
      fields: body.fields,
      stepId: body.stepId,
      submit: body.submit
    });

    return NextResponse.json({ record: created }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Record creation failed"
      },
      { status: 400 }
    );
  }
}
