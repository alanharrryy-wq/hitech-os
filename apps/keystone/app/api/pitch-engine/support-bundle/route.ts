import { NextResponse } from "next/server";
import { SupportBundleRequestSchema } from "../../../../components/pitch-engine/schemas";
import type { SupportBundle } from "../../../../components/pitch-engine/types";
import { summarizeProgram } from "../../../../components/pitch-engine/utils/timeline";
import { evaluateApiGate, notFoundResponse } from "../_lib/security";
import { readArtifactIndices, readDoDResultsPath, readProgramLibrary } from "../_lib/fs";

export async function POST(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const body = (await request.json()) as unknown;
  const parsed = SupportBundleRequestSchema.parse(body);

  const [programs, runs, dodResultPath] = await Promise.all([
    readProgramLibrary(),
    readArtifactIndices(),
    readDoDResultsPath()
  ]);

  const selectedProgram =
    parsed.selectedProgramId !== null
      ? programs.find((program) => program.id === parsed.selectedProgramId) ?? null
      : null;
  const selectedScene =
    selectedProgram && parsed.selectedSceneId
      ? selectedProgram.scenes.find((scene) => scene.id === parsed.selectedSceneId) ?? null
      : null;
  const selectedSequence =
    selectedProgram && parsed.selectedSequenceId
      ? selectedProgram.sequences.find((sequence) => sequence.id === parsed.selectedSequenceId) ?? null
      : null;

  const stats = selectedProgram
    ? summarizeProgram(selectedProgram)
    : {
        scenes: 0,
        sequences: 0,
        markers: 0,
        keyframes: 0
      };

  const bundle: SupportBundle = {
    generatedAt: new Date().toISOString(),
    app: "keystone",
    route: "/dev/pitch-engine",
    selectedProgram,
    selectedScene,
    selectedSequence,
    capabilityStatus: parsed.capabilityStatus,
    operatorHud: parsed.operatorHud,
    artifactRuns: runs,
    diagnostics: {
      selectedProgramStats: stats,
      links: parsed.links,
      dodResultPath
    },
    environment: parsed.environment
  };

  return NextResponse.json(bundle, { status: 200 });
}
