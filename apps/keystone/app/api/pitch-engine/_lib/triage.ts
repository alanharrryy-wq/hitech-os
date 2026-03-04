import { spawn } from "node:child_process";
import path from "node:path";
import type { ArtifactRunIndex, ArtifactTriageItem, TriageActionResult } from "../../../../components/pitch-engine/types";
import { readArtifactIndices, resolveRepoPath, writeDiffNotes } from "./fs";

function updateItemStatus(
  runs: ArtifactRunIndex[],
  input: {
    readonly runId: string;
    readonly sceneId: string;
    readonly sequenceId: string;
    readonly status: ArtifactTriageItem["status"];
  }
): ArtifactTriageItem | null {
  for (const run of runs) {
    if (run.runId !== input.runId) {
      continue;
    }

    for (const item of run.items) {
      if (item.sceneId === input.sceneId && item.sequenceId === input.sequenceId) {
        return {
          ...item,
          status: input.status,
          updatedAt: new Date().toISOString()
        };
      }
    }
  }

  return null;
}

async function runCommand(command: string, args: string[]): Promise<{
  readonly commandText: string;
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number;
}> {
  const commandText = `${command} ${args.join(" ")}`.trim();

  return new Promise((resolve) => {
    const child = spawn(command, args, {
      cwd: resolveRepoPath(),
      windowsHide: true
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("close", (exitCode) => {
      resolve({
        commandText,
        stdout,
        stderr,
        exitCode: exitCode ?? 0
      });
    });

    child.on("error", (error) => {
      resolve({
        commandText,
        stdout,
        stderr: `${stderr}\n${error.message}`,
        exitCode: 1
      });
    });
  });
}

export async function runTriageAction(input: {
  readonly action: "accept" | "reject" | "rerun";
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
}): Promise<TriageActionResult> {
  let command = "pwsh";
  let args: string[];

  if (input.action === "rerun") {
    command = "python";
    args = [
      "tools/hos/guardrails/evolutionary_sanctions.py",
      "--repo",
      ".",
      "--run-id",
      input.runId,
      "--worker-id",
      "C_features",
      "--bundle-dir",
      `tools/codex/runs/${input.runId}/C_features`
    ];
  } else {
    args = [
      "-NoProfile",
      "-Command",
      `Write-Output "pitch-engine triage ${input.action} run=${input.runId} scene=${input.sceneId} sequence=${input.sequenceId}"`
    ];
  }

  const result = await runCommand(command, args);
  const runs = await readArtifactIndices();
  const updatedItem =
    input.action === "accept" || input.action === "reject"
      ? updateItemStatus(runs, {
          runId: input.runId,
          sceneId: input.sceneId,
          sequenceId: input.sequenceId,
          status: input.action === "accept" ? "accepted" : "rejected"
        })
      : updateItemStatus(runs, {
          runId: input.runId,
          sceneId: input.sceneId,
          sequenceId: input.sequenceId,
          status: "pending"
        });

  return {
    ok: result.exitCode === 0,
    action: input.action,
    command: result.commandText,
    stdout: result.stdout,
    stderr: result.stderr,
    exitCode: result.exitCode,
    notesPath: null,
    updatedItem
  };
}

export async function saveTriageNotes(input: {
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
  readonly notes: string;
}): Promise<TriageActionResult> {
  const notesPath = await writeDiffNotes(input);
  const runs = await readArtifactIndices();
  const updatedItem = updateItemStatus(runs, {
    runId: input.runId,
    sceneId: input.sceneId,
    sequenceId: input.sequenceId,
    status: "pending"
  });

  return {
    ok: true,
    action: "notes",
    command: `write ${path.relative(resolveRepoPath(), notesPath).replaceAll("\\", "/")}`,
    stdout: "notes saved",
    stderr: "",
    exitCode: 0,
    notesPath,
    updatedItem: updatedItem
      ? {
          ...updatedItem,
          notesPath: path.relative(resolveRepoPath(), notesPath).replaceAll("\\", "/")
        }
      : null
  };
}
