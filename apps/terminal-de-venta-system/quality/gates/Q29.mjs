import { runPhase5Gate, runCli, isDirectModule } from "./_phase5_release_operator_readiness_common.mjs";

export const gateId = "Q29";
export const code = "Q29";
export const phase = 5;
export const title = "Operator docs readiness";
export const metadata = {
  id: "Q29",
  code: "Q29",
  phase: 5,
  title,
  category: "release-operator-readiness",
  required: true,
};

export async function run(context = {}) {
  return await runPhase5Gate("Q29", context);
}

export async function check(context = {}) {
  return await run(context);
}

export async function evaluate(context = {}) {
  return await run(context);
}

export default run;

if (isDirectModule(import.meta.url)) {
  await runCli("Q29");
}
