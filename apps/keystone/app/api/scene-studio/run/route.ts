import { NextResponse } from "next/server";

const DISABLED_PAYLOAD = {
  kind: "scene_studio_disabled",
  error: "Scene Studio is removed from active scope for repository cleanup."
} as const;

export const runtime = "nodejs";

export function GET(): Response {
  return NextResponse.json(DISABLED_PAYLOAD, { status: 410 });
}

export function POST(): Response {
  return NextResponse.json(DISABLED_PAYLOAD, { status: 410 });
}
