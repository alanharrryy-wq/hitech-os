import { fail, pass, run } from "./chart-lab-script-utils.mjs";

const env = {
  PRISMA_CHART_LAB_STATIC_EXPORT: "true",
  PRISMA_CHART_LAB_PUBLIC_SAFE: "true",
  NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE: "true",
  NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE: "cloudflare-pages"
};

const result = run("pnpm", ["build"], { env, stdio: "inherit" });
if (result.status === 0) pass("Cloudflare static export build complete");
else fail(`Cloudflare static export build failed with exit code ${result.status}`);
