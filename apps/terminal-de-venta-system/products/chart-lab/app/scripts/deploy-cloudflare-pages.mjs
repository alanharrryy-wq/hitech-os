import { exists, fail, pass, rel, run, writeEvidence } from "./chart-lab-script-utils.mjs";

if (!exists("out/index.html")) {
  fail("Cloudflare deploy blocked: out/index.html is missing. Run chart-lab:cf:build first.");
  process.exit(1);
}

const whoami = run("pnpm", ["exec", "wrangler", "whoami"]);
writeEvidence("wrangler-whoami.txt", `${whoami.stdout ?? ""}${whoami.stderr ?? ""}`);
if (whoami.status !== 0) {
  fail("Cloudflare deploy blocked: wrangler is not authenticated. Run: pnpm -C \"F:\\repos\\hitech-os\\apps\\terminal-de-venta-system\\products\\chart-lab\\app\" exec wrangler login");
  process.exit(1);
}
pass("wrangler authentication verified");

const deploy = run("pnpm", ["exec", "wrangler", "pages", "deploy", rel("out"), "--project-name=prisma-chart-lab", "--branch=preview"], { stdio: "pipe" });
writeEvidence("cloudflare-pages-deploy.txt", `${deploy.stdout ?? ""}${deploy.stderr ?? ""}`);
if (deploy.status === 0) pass("Cloudflare Pages deploy command completed");
else fail(`Cloudflare Pages deploy failed with exit code ${deploy.status}`);
