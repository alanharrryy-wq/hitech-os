import { runPhase5Gate, runCli, isDirectModule } from "./_phase5_release_operator_readiness_common.mjs";

export const gateId = "Q30";
export const code = "Q30";
export const phase = 5;
export const title = "Release profile readiness";
export const metadata = {
  id: "Q30",
  code: "Q30",
  phase: 5,
  title,
  category: "release-operator-readiness",
  required: true,
};

export async function run(context = {}) {
  return await runPhase5Gate("Q30", context);
}

export async function check(context = {}) {
  return await run(context);
}

export async function evaluate(context = {}) {
  return await run(context);
}

export default run;

if (isDirectModule(import.meta.url)) {
  await runCli("Q30");
}
