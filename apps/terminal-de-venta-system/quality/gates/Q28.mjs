import { runPhase5Gate, runCli, isDirectModule } from "./_phase5_release_operator_readiness_common.mjs";

export const gateId = "Q28";
export const code = "Q28";
export const phase = 5;
export const title = "Cleanup and artifact hygiene";
export const metadata = {
  id: "Q28",
  code: "Q28",
  phase: 5,
  title,
  category: "release-operator-readiness",
  required: true,
};

export async function run(context = {}) {
  return await runPhase5Gate("Q28", context);
}

export async function check(context = {}) {
  return await run(context);
}

export async function evaluate(context = {}) {
  return await run(context);
}

export default run;

if (isDirectModule(import.meta.url)) {
  await runCli("Q28");
}
