import { NextResponse } from "next/server";
import { notFoundResponse, evaluateApiGate } from "../_lib/security";
import { readArtifactIndices, readDoDResultsPath } from "../_lib/fs";

export async function GET(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const runs = await readArtifactIndices();
  const latestRun = runs[0] ?? null;
  const dodPath = await readDoDResultsPath();

  const payload = {
    serverStatus: "ready" as const,
    lastRunStatus: latestRun ? "ok" as const : "unknown" as const,
    lastRunPath: latestRun?.sourcePath ?? null,
    lastErrorTail: null,
    lastArtifactRunId: latestRun?.runId ?? null,
    updatedAt: new Date().toISOString(),
    dodPath
  };

  return NextResponse.json(payload, { status: 200 });
}
