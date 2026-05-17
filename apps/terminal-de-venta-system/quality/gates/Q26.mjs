import { runPhase5Gate, runCli, isDirectModule } from "./_phase5_release_operator_readiness_common.mjs";

export const gateId = "Q26";
export const code = "Q26";
export const phase = 5;
export const title = "Launcher OS release readiness";
export const metadata = {
  id: "Q26",
  code: "Q26",
  phase: 5,
  title,
  category: "release-operator-readiness",
  required: true,
};

export async function run(context = {}) {
  return await runPhase5Gate("Q26", context);
}

export async function check(context = {}) {
  return await run(context);
}

export async function evaluate(context = {}) {
  return await run(context);
}

export default run;

if (isDirectModule(import.meta.url)) {
  await runCli("Q26");
}
