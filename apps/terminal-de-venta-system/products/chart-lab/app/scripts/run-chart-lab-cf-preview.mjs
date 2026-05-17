import { fail, pass, rel, run } from "./chart-lab-script-utils.mjs";

const outputDir = rel("out");
const result = run("pnpm", ["exec", "wrangler", "pages", "dev", outputDir, "--project-name=prisma-chart-lab"], {
  env: {
    PRISMA_CHART_LAB_PUBLIC_SAFE: "true",
    NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE: "true",
    NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE: "cloudflare-pages-preview"
  },
  stdio: "inherit"
});

if (result.status === 0) pass("Cloudflare Pages local preview exited cleanly");
else fail(`Cloudflare Pages local preview exited with code ${result.status}`);
