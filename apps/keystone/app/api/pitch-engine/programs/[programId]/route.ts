import { NextResponse } from "next/server";
import { ProgramUpdateInputSchema, PitchProgramSchema } from "../../../../../components/pitch-engine/schemas";
import { evaluateApiGate, notFoundResponse } from "../../_lib/security";
import { readProgramLibrary, writeProgramLibrary } from "../../_lib/fs";

interface Params {
  readonly params: Promise<{
    readonly programId: string;
  }>;
}

export async function PUT(request: Request, context: Params): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const { programId } = await context.params;
  const body = (await request.json()) as unknown;
  const parsed = ProgramUpdateInputSchema.parse(body);

  const programs = await readProgramLibrary();
  const existing = programs.find((program) => program.id === programId);
  if (!existing) {
    return NextResponse.json({ message: "Program not found" }, { status: 404 });
  }

  const nextProgram = parsed.program
    ? PitchProgramSchema.parse(parsed.program)
    : {
        ...existing,
        name: parsed.name ?? existing.name,
        description: parsed.description ?? existing.description,
        owner: parsed.owner ?? existing.owner,
        version: parsed.version ?? existing.version,
        updatedAt: new Date().toISOString()
      };

  const updated = programs.map((program) => (program.id === programId ? nextProgram : program));
  await writeProgramLibrary(updated);

  return NextResponse.json(nextProgram, { status: 200 });
}

export async function DELETE(request: Request, context: Params): Promise<Response> {
  const gate = evaluateApiGate(request);
  if (!gate.allowed) {
    return notFoundResponse();
  }

  const { programId } = await context.params;
  const programs = await readProgramLibrary();

  const exists = programs.some((program) => program.id === programId);
  if (!exists) {
    return NextResponse.json({ message: "Program not found" }, { status: 404 });
  }

  const updated = programs.filter((program) => program.id !== programId);
  await writeProgramLibrary(updated);

  return NextResponse.json({ ok: true }, { status: 200 });
}
