import { NextResponse } from "next/server";
import { TriageActionRequestSchema } from "../../../../components/pitch-engine/schemas";
import { evaluateApiGate, notFoundResponse } from "../_lib/security";
import { runTriageAction, saveTriageNotes } from "../_lib/triage";

export async function POST(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const body = (await request.json()) as unknown;
  const parsed = TriageActionRequestSchema.parse(body);

  if (parsed.action === "notes") {
    const notesResult = await saveTriageNotes({
      runId: parsed.runId,
      sceneId: parsed.sceneId,
      sequenceId: parsed.sequenceId,
      notes: parsed.notes ?? ""
    });

    return NextResponse.json(notesResult, { status: 200 });
  }

  const result = await runTriageAction({
    action: parsed.action,
    runId: parsed.runId,
    sceneId: parsed.sceneId,
    sequenceId: parsed.sequenceId
  });

  return NextResponse.json(result, { status: result.ok ? 200 : 500 });
}
