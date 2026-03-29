import path from "node:path";
import process from "node:process";
import { NextResponse } from "next/server";
import { buildSceneStudioRunnerArgs, parseSceneStudioRunPayload } from "./run-contract";
import { runProcessCaptured } from "./run-process";

const ARTIFACT_ROOT = "artifacts/keystone-scene-studio";
const OUTPUT_SLICE_CHARS = 20_000;
const MAX_CAPTURE_BYTES = 512_000;

export const runtime = "nodejs";

function hasDebugAccess(url: URL): boolean {
  return url.searchParams.get("debug") === "1" || process.env["NEXT_PUBLIC_SCENE_STUDIO"] === "1";
}

interface RunnerJsonResult {
  readonly kind?: "exited" | "timeout" | "spawn_failed";
  readonly command?: string;
  readonly cwd?: string;
  readonly exitCode?: number | null;
  readonly signal?: string | null;
  readonly durationMs?: number;
  readonly stdout?: string;
  readonly stderr?: string;
  readonly errorMessage?: string | null;
}

function trimTail(value: string | undefined): string {
  if (!value) {
    return "";
  }

  return value.length > OUTPUT_SLICE_CHARS ? value.slice(-OUTPUT_SLICE_CHARS) : value;
}

function parseRunnerJson(stdout: string): RunnerJsonResult | null {
  const trimmed = stdout.trim();
  if (trimmed.length === 0) {
    return null;
  }

  try {
    return JSON.parse(trimmed) as RunnerJsonResult;
  } catch {
    const lines = trimmed.split(/\r?\n/g).reverse();
    for (const line of lines) {
      if (!line.trim().startsWith("{")) {
        continue;
      }

      try {
        return JSON.parse(line) as RunnerJsonResult;
      } catch {
        continue;
      }
    }
    return null;
  }
}

function joinCommand(command: string, args: readonly string[]): string {
  return [command, ...args].join(" ");
}

export async function POST(request: Request): Promise<Response> {
  if (process.env["NODE_ENV"] === "production") {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const url = new URL(request.url);
  if (!hasDebugAccess(url)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  let payloadRaw: unknown;
  try {
    payloadRaw = await request.json();
  } catch {
    return NextResponse.json(
      {
        kind: "invalid_payload",
        error: "Request body must be valid JSON.",
        artifactRoot: ARTIFACT_ROOT
      },
      { status: 400 }
    );
  }

  const parsed = parseSceneStudioRunPayload(payloadRaw);
  if (!parsed.ok) {
    return NextResponse.json(
      {
        kind: "invalid_payload",
        error: parsed.error,
        artifactRoot: ARTIFACT_ROOT
      },
      { status: 400 }
    );
  }

  const cwd = process.cwd();
  const runnerScriptPath = path.join(cwd, "scripts", "scene-studio-runner.mjs");
  const runnerArgs = buildSceneStudioRunnerArgs(runnerScriptPath, parsed.payload);
  const command = process.execPath;

  const result = await runProcessCaptured({
    command,
    args: runnerArgs,
    cwd,
    env: {
      ...process.env,
      SCENE_STUDIO_FROM_API: "1"
    },
    timeoutMs: parsed.payload.timeoutMs + 10_000,
    maxOutputBytes: MAX_CAPTURE_BYTES
  });

  const runnerJson = parseRunnerJson(result.stdout);
  const summary = {
    kind: runnerJson?.kind ?? result.kind,
    command: runnerJson?.command ?? joinCommand(command, runnerArgs),
    cwd: runnerJson?.cwd ?? cwd,
    exitCode: typeof runnerJson?.exitCode === "number" ? runnerJson.exitCode : (result.exitCode ?? 1),
    signal: runnerJson?.signal ?? result.signal,
    durationMs: runnerJson?.durationMs ?? result.durationMs,
    stdout: trimTail(runnerJson?.stdout ?? ""),
    stderr: trimTail(runnerJson?.stderr ?? ""),
    errorMessage: runnerJson?.errorMessage ?? result.errorMessage
  };

  if (result.kind === "spawn_failed") {
    return NextResponse.json(
      {
        ...summary,
        kind: "spawn_failed",
        artifactRoot: ARTIFACT_ROOT,
        runnerStdout: trimTail(result.stdout),
        runnerStderr: trimTail(result.stderr)
      },
      { status: 500 }
    );
  }

  if (summary.kind === "timeout" || result.kind === "timeout") {
    return NextResponse.json(
      {
        ...summary,
        kind: "timeout",
        artifactRoot: ARTIFACT_ROOT,
        runnerStdout: trimTail(result.stdout),
        runnerStderr: trimTail(result.stderr)
      },
      { status: 504 }
    );
  }

  const status = summary.exitCode === 0 ? 200 : 422;
  return NextResponse.json(
    {
      ...summary,
      kind: summary.exitCode === 0 ? "ok" : "runner_failed",
      artifactRoot: ARTIFACT_ROOT,
      runnerStdout: trimTail(result.stdout),
      runnerStderr: trimTail(result.stderr)
    },
    { status }
  );
}
