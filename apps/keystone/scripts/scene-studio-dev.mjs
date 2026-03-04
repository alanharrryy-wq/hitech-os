import { spawn } from "node:child_process";
import process from "node:process";

const env = {
  ...process.env,
  NEXT_PUBLIC_SCENE_STUDIO: process.env.NEXT_PUBLIC_SCENE_STUDIO ?? "1"
};

process.stdout.write("Keystone Scene Studio: http://127.0.0.1:3100/dev/scene-studio?debug=1\n");

const child = spawn("pnpm", ["run", "dev"], {
  cwd: process.cwd(),
  env,
  stdio: "inherit",
  shell: process.platform === "win32"
});

child.on("exit", (code) => {
  process.exit(code ?? 0);
});
