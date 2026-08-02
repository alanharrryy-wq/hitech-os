import { appendFile, mkdir } from "node:fs/promises";
import path from "node:path";
import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const SIGNALS = new Set(["ChunkLoadError", "Failed to load chunk", "_next/static/chunks"]);
const SOURCES = new Set(["window.error", "unhandledrejection"]);

export async function POST(request: Request) {
  const raw = await request.text();
  if (raw.length > 2048) {
    return NextResponse.json({ ok: false, code: "PAYLOAD_TOO_LARGE" }, { status: 413 });
  }

  let body: Record<string, unknown>;
  try {
    body = JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ ok: false, code: "INVALID_JSON" }, { status: 400 });
  }

  const signal = typeof body.signal === "string" ? body.signal : "";
  const source = typeof body.source === "string" ? body.source : "";
  if (!SIGNALS.has(signal) || !SOURCES.has(source)) {
    return NextResponse.json({ ok: false, code: "INVALID_SIGNAL" }, { status: 422 });
  }

  const outputRoot = process.env.PRISMA_OUTPUT_DIR || "F:\\descargasf";
  const evidenceDir = path.join(outputRoot, "prisma-zero-idle");
  await mkdir(evidenceDir, { recursive: true });
  await appendFile(
    path.join(evidenceDir, "chunkload-beacons.ndjson"),
    `${JSON.stringify({
      schemaVersion: "prisma-passive-chunk-evidence/v1",
      recordedAt: new Date().toISOString(),
      app: "tablet",
      port: 3120,
      signal,
      source,
      pii: false,
      salesData: false
    })}\n`,
    { encoding: "utf8" }
  );

  return NextResponse.json({ ok: true, accepted: true }, { status: 202 });
}
