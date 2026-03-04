import { promises as fs, existsSync } from "node:fs";
import path from "node:path";
import type { ArtifactRunIndex, ArtifactTriageItem, PitchProgram } from "../../../../components/pitch-engine/types";
import { ArtifactRunIndexSchema, PitchProgramSchema } from "../../../../components/pitch-engine/schemas";
import { DEFAULT_PROGRAM_LIBRARY } from "../../../../components/pitch-engine/program-library/default-programs";

function findRepoRoot(start: string): string {
  let current = path.resolve(start);

  while (true) {
    const marker = path.join(current, "pnpm-workspace.yaml");
    if (existsSync(marker)) {
      return current;
    }

    const parent = path.dirname(current);
    if (parent === current) {
      return path.resolve(start);
    }

    current = parent;
  }
}

const REPO_ROOT = findRepoRoot(process.cwd());
const ACTIVE_RUN_ID = process.env.RUN_ID ?? "20260304_061005_61C9";
const RUNTIME_DIR = path.join(
  REPO_ROOT,
  "tools",
  "codex",
  "runs",
  ACTIVE_RUN_ID,
  "C_features",
  "runtime",
  "pitch-engine"
);
const PROGRAMS_FILE = path.join(RUNTIME_DIR, "programs.json");
const TRIAGE_NOTES_DIR = path.join(RUNTIME_DIR, "triage-notes");

async function ensureRuntimeDir(): Promise<void> {
  await fs.mkdir(RUNTIME_DIR, { recursive: true });
  await fs.mkdir(TRIAGE_NOTES_DIR, { recursive: true });
}

export async function readProgramLibrary(): Promise<PitchProgram[]> {
  await ensureRuntimeDir();

  try {
    const raw = await fs.readFile(PROGRAMS_FILE, "utf8");
    const parsed = JSON.parse(raw) as unknown;
    return PitchProgramSchema.array().parse(parsed);
  } catch {
    await writeProgramLibrary(DEFAULT_PROGRAM_LIBRARY);
    return DEFAULT_PROGRAM_LIBRARY;
  }
}

export async function writeProgramLibrary(programs: PitchProgram[]): Promise<void> {
  await ensureRuntimeDir();
  const payload = JSON.stringify(programs, null, 2);
  await fs.writeFile(PROGRAMS_FILE, payload, "utf8");
}

interface ToolingIndexItem {
  readonly runId?: string;
  readonly sceneId?: string;
  readonly sequenceId?: string;
  readonly status?: "pending" | "accepted" | "rejected";
  readonly score?: number;
  readonly before?: string;
  readonly after?: string;
  readonly diff?: string;
  readonly createdAt?: string;
  readonly updatedAt?: string;
}

interface ToolingIndex {
  readonly runId?: string;
  readonly createdAt?: string;
  readonly items?: ToolingIndexItem[];
}

function toTriageItem(runId: string, sourcePath: string, item: ToolingIndexItem, index: number): ArtifactTriageItem {
  return {
    id: `${runId}-${item.sceneId ?? `scene-${index + 1}`}-${item.sequenceId ?? `seq-${index + 1}`}`,
    runId,
    sceneId: item.sceneId ?? `scene-${index + 1}`,
    sequenceId: item.sequenceId ?? `sequence-${index + 1}`,
    status: item.status ?? "pending",
    score: typeof item.score === "number" ? item.score : 0.5,
    notesPath: null,
    diff: {
      beforePath: item.before ?? null,
      afterPath: item.after ?? null,
      diffPath: item.diff ?? null,
      width: 1280,
      height: 720
    },
    createdAt: item.createdAt ?? new Date().toISOString(),
    updatedAt: item.updatedAt ?? new Date().toISOString()
  };
}

function buildFallbackRuns(): ArtifactRunIndex[] {
  const now = new Date().toISOString();
  return [
    {
      runId: "fallback-run-1",
      createdAt: now,
      sourcePath: "tools/codex/runs/fallback/index.json",
      items: [
        {
          id: "fallback-run-1-scene-01-seq-01",
          runId: "fallback-run-1",
          sceneId: "scene-01",
          sequenceId: "seq-01",
          status: "pending",
          score: 0.63,
          notesPath: null,
          diff: {
            beforePath: null,
            afterPath: null,
            diffPath: null,
            width: 1280,
            height: 720
          },
          createdAt: now,
          updatedAt: now
        }
      ]
    }
  ];
}

async function findIndexFiles(dir: string): Promise<string[]> {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files: string[] = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await findIndexFiles(fullPath)));
      continue;
    }

    if (entry.name.toLowerCase() === "index.json") {
      files.push(fullPath);
    }
  }

  return files;
}

export async function readArtifactIndices(): Promise<ArtifactRunIndex[]> {
  const runsRoot = path.join(REPO_ROOT, "tools", "codex", "runs");

  try {
    const indexFiles = await findIndexFiles(runsRoot);
    const parsedRuns: ArtifactRunIndex[] = [];

    for (const filePath of indexFiles) {
      try {
        const content = await fs.readFile(filePath, "utf8");
        const parsed = JSON.parse(content) as ToolingIndex;
        const runId = parsed.runId ?? path.basename(path.dirname(filePath));
        const items = (parsed.items ?? []).map((item, index) =>
          toTriageItem(runId, filePath, item, index)
        );

        const run: ArtifactRunIndex = {
          runId,
          createdAt: parsed.createdAt ?? new Date().toISOString(),
          sourcePath: path.relative(REPO_ROOT, filePath).replaceAll("\\", "/"),
          items
        };

        parsedRuns.push(run);
      } catch {
        // Ignore malformed index files in dev triage listing.
      }
    }

    const valid = ArtifactRunIndexSchema.array().safeParse(parsedRuns);
    if (valid.success && valid.data.length > 0) {
      return valid.data;
    }

    return buildFallbackRuns();
  } catch {
    return buildFallbackRuns();
  }
}

export async function writeDiffNotes(input: {
  readonly runId: string;
  readonly sceneId: string;
  readonly sequenceId: string;
  readonly notes: string;
}): Promise<string> {
  await ensureRuntimeDir();

  const dir = path.join(TRIAGE_NOTES_DIR, input.runId, input.sceneId, input.sequenceId);
  await fs.mkdir(dir, { recursive: true });

  const filePath = path.join(dir, "DIFF_NOTES.md");
  await fs.writeFile(filePath, input.notes, "utf8");
  return filePath;
}

export async function readDoDResultsPath(): Promise<string | null> {
  const expectedPath = path.join(
    REPO_ROOT,
    "tools",
    "codex",
    "runs",
    "20260304_061005_61C9",
    "C_features",
    "DOD_RESULTS.json"
  );

  try {
    await fs.access(expectedPath);
    return expectedPath;
  } catch {
    return null;
  }
}

export function resolveRepoPath(...parts: string[]): string {
  return path.join(REPO_ROOT, ...parts);
}
