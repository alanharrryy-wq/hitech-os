import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "tools/prisma-visual-os/ai_doctor_prisma_show_pos_00y.py",
  "tools/prisma-visual-os/run_prisma_show_pos_ai_doctor_00y.cmd",
  "tools/prisma-visual-os/run_prisma_show_pos_ai_doctor.cmd",
  "config/prisma-visual-os/ai-doctor-policy-00y.json",
  "docs/design/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y.md",
  "docs/qa/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y_ACCEPTANCE.md",
];

const checks = [];
function add(name, ok) { checks.push({ name, ok }); }

for (const rel of required) {
  add(`${rel} exists`, existsSync(path.join(root, rel)));
}

const doctorPath = path.join(root, "tools/prisma-visual-os/ai_doctor_prisma_show_pos_00y.py");
const doctor = existsSync(doctorPath) ? readFileSync(doctorPath, "utf8") : "";
add("doctor package marker", doctor.includes("PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y"));
add("doctor offline only", doctor.includes("offline_rules") && doctor.includes("zero_api_cost"));
add("doctor reads doctor 00X", doctor.includes("prisma_show_pos_doctor_smart_00x_*.json"));
add("doctor computes classification", doctor.includes("def classify"));
add("doctor proposes next package", doctor.includes("def propose_next_package"));
add("doctor writes markdown", doctor.includes("render_markdown"));
add("doctor has self-check", doctor.includes("--self-check"));
add("doctor does not import openai", !doctor.includes("import openai"));

const policyPath = path.join(root, "config/prisma-visual-os/ai-doctor-policy-00y.json");
const policy = existsSync(policyPath) ? JSON.parse(readFileSync(policyPath, "utf8")) : {};
add("policy provider none", policy.defaultProvider === "none");
add("policy no runtime mutation", policy.allowRuntimeMutation === false);
add("policy no api cost", policy.apiCost === "none");

const launcher = existsSync(path.join(root, "tools/prisma-visual-os/run_prisma_show_pos_ai_doctor.cmd"))
  ? readFileSync(path.join(root, "tools/prisma-visual-os/run_prisma_show_pos_ai_doctor.cmd"), "utf8")
  : "";
add("canonical launcher calls 00Y", launcher.includes("ai_doctor_prisma_show_pos_00y.py"));
add("canonical launcher writes descargasf", launcher.includes("F:\\descargasf"));

const ok = checks.every((c) => c.ok);
const out = { ok, root, package: "PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y", checks };
console.log(JSON.stringify(out, null, 2));
if (!ok) process.exit(1);
