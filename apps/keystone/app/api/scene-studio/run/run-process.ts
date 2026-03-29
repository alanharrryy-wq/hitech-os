import { spawn, type ChildProcess } from "node:child_process";

export interface ProcessCaptureOptions {
  readonly command: string;
  readonly args: readonly string[];
  readonly cwd: string;
  readonly env: NodeJS.ProcessEnv;
  readonly timeoutMs: number;
  readonly maxOutputBytes: number;
}

export type ProcessCaptureKind = "exited" | "timeout" | "spawn_failed";

export interface ProcessCaptureResult {
  readonly kind: ProcessCaptureKind;
  readonly command: string;
  readonly cwd: string;
  readonly exitCode: number | null;
  readonly signal: NodeJS.Signals | null;
  readonly durationMs: number;
  readonly stdout: string;
  readonly stderr: string;
  readonly errorMessage: string | null;
}

class OutputTailBuffer {
  private readonly limitBytes: number;
  private readonly chunks: Buffer[] = [];
  private sizeBytes = 0;

  constructor(limitBytes: number) {
    this.limitBytes = Math.max(1, limitBytes);
  }

  append(chunk: Buffer): void {
    if (chunk.length === 0) {
      return;
    }

    this.chunks.push(chunk);
    this.sizeBytes += chunk.length;
    this.trimHead();
  }

  toString(): string {
    if (this.chunks.length === 0) {
      return "";
    }

    return Buffer.concat(this.chunks).toString("utf8");
  }

  private trimHead(): void {
    while (this.sizeBytes > this.limitBytes && this.chunks.length > 0) {
      const head = this.chunks[0];
      if (!head) {
        break;
      }

      const overflow = this.sizeBytes - this.limitBytes;
      if (overflow >= head.length) {
        this.chunks.shift();
        this.sizeBytes -= head.length;
        continue;
      }

      this.chunks[0] = head.subarray(overflow);
      this.sizeBytes -= overflow;
      break;
    }
  }
}

function toBuffer(chunk: string | Buffer): Buffer {
  return Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk, "utf8");
}

export async function runProcessCaptured(options: ProcessCaptureOptions): Promise<ProcessCaptureResult> {
  const startedAt = Date.now();
  const stdoutTail = new OutputTailBuffer(options.maxOutputBytes);
  const stderrTail = new OutputTailBuffer(options.maxOutputBytes);

  let child: ChildProcess;
  try {
    child = spawn(options.command, [...options.args], {
      cwd: options.cwd,
      env: options.env,
      shell: false,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"]
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      kind: "spawn_failed",
      command: options.command,
      cwd: options.cwd,
      exitCode: null,
      signal: null,
      durationMs: Date.now() - startedAt,
      stdout: "",
      stderr: "",
      errorMessage: message
    };
  }

  if (child.stdout) {
    child.stdout.on("data", (chunk: string | Buffer) => {
      stdoutTail.append(toBuffer(chunk));
    });
  }

  if (child.stderr) {
    child.stderr.on("data", (chunk: string | Buffer) => {
      stderrTail.append(toBuffer(chunk));
    });
  }

  return await new Promise<ProcessCaptureResult>((resolve) => {
    let settled = false;
    let timedOut = false;
    let hardKillTimer: NodeJS.Timeout | undefined;
    const timeoutTimer =
      options.timeoutMs > 0
        ? setTimeout(() => {
            timedOut = true;
            child.kill("SIGTERM");
            hardKillTimer = setTimeout(() => {
              child.kill("SIGKILL");
            }, 5_000);
          }, options.timeoutMs)
        : undefined;

    const finalize = (result: Omit<ProcessCaptureResult, "stdout" | "stderr" | "durationMs">) => {
      if (settled) {
        return;
      }
      settled = true;

      if (timeoutTimer) {
        clearTimeout(timeoutTimer);
      }
      if (hardKillTimer) {
        clearTimeout(hardKillTimer);
      }

      resolve({
        ...result,
        durationMs: Date.now() - startedAt,
        stdout: stdoutTail.toString(),
        stderr: stderrTail.toString()
      });
    };

    child.once("error", (error) => {
      const message = error instanceof Error ? error.message : String(error);
      finalize({
        kind: "spawn_failed",
        command: options.command,
        cwd: options.cwd,
        exitCode: null,
        signal: null,
        errorMessage: message
      });
    });

    child.once("close", (code, signal) => {
      finalize({
        kind: timedOut ? "timeout" : "exited",
        command: options.command,
        cwd: options.cwd,
        exitCode: typeof code === "number" ? code : null,
        signal: signal ?? null,
        errorMessage: null
      });
    });
  });
}
