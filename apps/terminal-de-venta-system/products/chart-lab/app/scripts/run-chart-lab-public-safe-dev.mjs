import { fail, pass, run } from "./chart-lab-script-utils.mjs";

const result = run("pnpm", ["dev"], {
  env: {
    PRISMA_CHART_LAB_PUBLIC_SAFE: "true",
    NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE: "true",
    NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE: "cloudflare-tunnel"
  },
  stdio: "inherit"
});

if (result.status === 0) pass("public-safe dev server exited cleanly");
else fail(`public-safe dev server exited with code ${result.status}`);
