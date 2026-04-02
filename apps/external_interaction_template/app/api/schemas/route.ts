import { NextResponse } from "next/server";

import { listSchemas } from "@/lib/core/schema-registry";
import { listAdapters } from "@/lib/adapters";
import { ensureTemplateBootstrap } from "@/lib/services/bootstrap";

export async function GET() {
  await ensureTemplateBootstrap();
  return NextResponse.json({
    schemas: listSchemas(),
    adapters: listAdapters().map((adapter) => ({
      id: adapter.id,
      label: adapter.label,
      direction: adapter.direction
    }))
  });
}
