import { NextResponse } from "next/server";
import {
  ProgramCreateInputSchema,
  ProgramImportInputSchema,
  PitchProgramSchema
} from "../../../../components/pitch-engine/schemas";
import { buildStableId, nowIso } from "../../../../components/pitch-engine/utils/id";
import type { PitchProgram } from "../../../../components/pitch-engine/types";
import { evaluateApiGate, notFoundResponse } from "../_lib/security";
import { readProgramLibrary, writeProgramLibrary } from "../_lib/fs";

interface ProgramPostBody {
  readonly action: "create" | "import";
  readonly name?: string;
  readonly description?: string;
  readonly owner?: string;
  readonly program?: PitchProgram;
}

export async function GET(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const programs = await readProgramLibrary();
  return NextResponse.json(programs, { status: 200 });
}

function createProgram(input: {
  readonly name: string;
  readonly description: string;
  readonly owner: string;
  readonly existingPrograms: readonly PitchProgram[];
}): PitchProgram {
  const now = nowIso();
  const id = buildStableId(
    "program",
    input.name,
    input.existingPrograms.map((item) => item.id)
  );

  return {
    id,
    name: input.name,
    description: input.description,
    owner: input.owner,
    version: "1.0.0",
    createdAt: now,
    updatedAt: now,
    scenes: [],
    sequences: [],
    diagnostics: {
      source: "user",
      lastSaveError: null,
      warnings: [],
      artifactLinks: []
    }
  };
}

export async function POST(request: Request): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const body = (await request.json()) as ProgramPostBody;
  const programs = await readProgramLibrary();

  if (body.action === "create") {
    const parsed = ProgramCreateInputSchema.parse({
      name: body.name,
      description: body.description,
      owner: body.owner
    });

    const program = createProgram({
      ...parsed,
      existingPrograms: programs
    });

    const updated = [...programs, program];
    await writeProgramLibrary(updated);

    return NextResponse.json(program, { status: 201 });
  }

  const imported = ProgramImportInputSchema.parse({
    program: body.program
  });

  const existingIds = new Set(programs.map((item) => item.id));
  const safeProgram = existingIds.has(imported.program.id)
    ? {
        ...imported.program,
        id: buildStableId("program-import", imported.program.name, programs.map((item) => item.id))
      }
    : imported.program;

  PitchProgramSchema.parse(safeProgram);

  const updated = [...programs, safeProgram];
  await writeProgramLibrary(updated);

  return NextResponse.json(safeProgram, { status: 201 });
}
