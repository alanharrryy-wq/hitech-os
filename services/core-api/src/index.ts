import { buildServer } from "./server.js";
import { loadRuntimeConfig } from "./lib/config.js";

async function start(): Promise<void> {
  const config = loadRuntimeConfig();
  const { server } = buildServer({ runtimeConfig: config });

  try {
    await new Promise<void>((resolve, reject) => {
      server.once("error", reject);
      server.listen(config.port, config.host, () => resolve());
    });

    console.log(`core-api listening on http://${config.host}:${config.port}`);
  } catch (error) {
    console.error("core-api failed to start", error);
    process.exitCode = 1;
  }
}

void start();
