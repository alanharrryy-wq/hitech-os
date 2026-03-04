import { spawnSync } from "node:child_process";
import { NextResponse } from "next/server";

interface SceneStudioRunPayload {
  readonly sceneIds?: readonly string[];
  readonly mode?: "smoke" | "full";
  readonly updateBaseline?: boolean;
}

function parsePayload(payload: unknown): SceneStudioRunPayload {
  if (!payload || typeof payload !== "object") {
    return {};
  }

  const candidate = payload as Record<string, unknown>;
  const sceneIds = Array.isArray(candidate["sceneIds"])
    ? candidate["sceneIds"].filter((value): value is string => typeof value === "string")
    : undefined;
  const mode = candidate["mode"] === "full" ? "full" : "smoke";

  return {
    ...(sceneIds ? { sceneIds } : {}),
    mode,
    updateBaseline: candidate["updateBaseline"] === true
  };
}

function hasDebugAccess(url: URL): boolean {
  return url.searchParams.get("debug") === "1" || process.env["NEXT_PUBLIC_SCENE_STUDIO"] === "1";
}

export async function POST(request: Request): Promise<Response> {
  if (process.env["NODE_ENV"] === "production") {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const url = new URL(request.url);
  if (!hasDebugAccess(url)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const payload = parsePayload(await request.json());
  const args: string[] = ["./scripts/scene-studio-runner.mjs"];

  if (payload.mode === "smoke") {
    args.push("--smoke");
  }

  if (payload.updateBaseline) {
    args.push("--update-baseline");
  }

  for (const sceneId of payload.sceneIds ?? []) {
    args.push(`--scene-id=${sceneId}`);
  }

  const result = spawnSync("node", args, {
    cwd: process.cwd(),
    env: {
      ...process.env,
      SCENE_STUDIO_FROM_API: "1"
    },
    encoding: "utf8",
    shell: process.platform === "win32"
  });

  return NextResponse.json(
    {
      command: `node ${args.join(" ")}`,
      exitCode: result.status ?? 1,
      artifactRoot: "artifacts/keystone-scene-studio",
      stdout: result.stdout?.slice(-20_000) ?? "",
      stderr: result.stderr?.slice(-20_000) ?? ""
    },
    {
      status: result.status === 0 ? 200 : 500
    }
  );
}
