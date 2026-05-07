import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

type CommandResult = {
  command: string;
  code: number | null;
  stdout: string;
  stderr: string;
};

export type TriDbSyncNowResult = {
  ok: boolean;
  status: "READY" | "BLOCKED";
  terminalRoot: string;
  repoRoot: string;
  outRoot: string;
  bridge: CommandResult;
  statusRefresh: CommandResult | null;
  message: string;
};

function resolveTerminalRoot(): string {
  const cwd = process.cwd();
  const candidates = [
    process.env.PRISMA_TERMINAL_ROOT,
    cwd,
    path.resolve(cwd, "../../.."),
    path.resolve(cwd, "../../../apps/terminal-de-venta-system"),
    path.resolve(cwd, "apps/terminal-de-venta-system")
  ].filter((item): item is string => Boolean(item && item.trim()));

  for (const candidate of Array.from(new Set(candidates))) {
    const marker = path.join(candidate, "terminal_de_venta.cmd");
    const products = path.join(candidate, "products");
    if (existsSync(marker) && existsSync(products)) return candidate;
  }

  throw new Error(`No pude resolver terminal-de-venta-system desde cwd=${cwd}`);
}

function resolveRepoRoot(terminalRoot: string): string {
  const parent = path.basename(path.dirname(terminalRoot)).toLowerCase();
  if (parent === "apps") return path.resolve(terminalRoot, "../..");
  return terminalRoot;
}

function resolvePython(repoRoot: string): string {
  const envPython = process.env.PRISMA_PYTHON || process.env.PYTHON;
  if (envPython && envPython.trim()) return envPython;
  const venvPython = path.join(repoRoot, ".venv", "Scripts", "python.exe");
  if (existsSync(venvPython)) return venvPython;
  return "python";
}

function runCommand(command: string, args: string[], cwd: string, timeoutMs = 300000): Promise<CommandResult> {
  return new Promise((resolve) => {
    const nodeEnv: NodeJS.ProcessEnv["NODE_ENV"] =       process.env.NODE_ENV === "production" || process.env.NODE_ENV === "test"         ? process.env.NODE_ENV         : "development";      const childEnv: NodeJS.ProcessEnv = {       ...process.env,       NODE_ENV: nodeEnv,     };     const child = spawn(command, args, {
      cwd,
      windowsHide: true,
      shell: false,
      env: childEnv
    });

    let stdout = "";
    let stderr = "";
    const timer = setTimeout(() => {
      stderr += `\nTIMEOUT: comando excedio ${timeoutMs}ms`;
      child.kill("SIGTERM");
    }, timeoutMs);

    child.stdout.on("data", (chunk: Buffer) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk: Buffer) => {
      stderr += chunk.toString();
    });
    child.on("error", (error: Error) => {
      clearTimeout(timer);
      resolve({ command: [command, ...args].join(" "), code: 1, stdout, stderr: stderr + `\n${error.message}` });
    });
    child.on("close", (code: number | null) => {
      clearTimeout(timer);
      resolve({ command: [command, ...args].join(" "), code, stdout, stderr });
    });
  });
}

export async function runTriDbSyncNow(): Promise<TriDbSyncNowResult> {
  const terminalRoot = resolveTerminalRoot();
  const repoRoot = resolveRepoRoot(terminalRoot);
  const outRoot = process.env.PRISMA_OUT_ROOT || "F:\\descargasf";
  const python = resolvePython(repoRoot);
  const bridgeTool = path.join(terminalRoot, "tools", "prisma", "tri_db_bridge.py");
  const statusTool = path.join(terminalRoot, "tools", "prisma", "tri_db_status.py");

  if (!existsSync(bridgeTool)) {
    throw new Error(`No existe tri_db_bridge.py. Instala primero v04: ${bridgeTool}`);
  }
  if (!existsSync(statusTool)) {
    throw new Error(`No existe tri_db_status.py. Instala primero v06: ${statusTool}`);
  }

  const bridge = await runCommand(
    python,
    [bridgeTool, "--run", "--target-root", repoRoot, "--out-root", outRoot],
    terminalRoot
  );

  if (bridge.code !== 0) {
    return {
      ok: false,
      status: "BLOCKED",
      terminalRoot,
      repoRoot,
      outRoot,
      bridge,
      statusRefresh: null,
      message: "El bridge Tablet -> PC fallo. Revisa stdout/stderr."
    };
  }

  const statusRefresh = await runCommand(
    python,
    [statusTool, "--run", "--target-root", repoRoot, "--out-root", outRoot],
    terminalRoot
  );

  const ok = statusRefresh.code === 0;
  return {
    ok,
    status: ok ? "READY" : "BLOCKED",
    terminalRoot,
    repoRoot,
    outRoot,
    bridge,
    statusRefresh,
    message: ok ? "Sincronizacion ejecutada y status actualizado." : "Bridge ejecuto, pero fallo la actualizacion de status."
  };
}
