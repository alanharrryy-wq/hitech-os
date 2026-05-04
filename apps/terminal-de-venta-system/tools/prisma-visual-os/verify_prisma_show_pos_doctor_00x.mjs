import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const doctor = join(root, "tools", "prisma-visual-os", "doctor_prisma_show_pos_scan_00x.py");
const launcher = join(root, "tools", "prisma-visual-os", "run_prisma_show_pos_doctor_00x.cmd");
const alias = join(root, "tools", "prisma-visual-os", "run_prisma_show_pos_doctor.cmd");
const design = join(root, "docs", "design", "PRISMA_SHOW_POS_DOCTOR_SMART_00X.md");
const qa = join(root, "docs", "qa", "PRISMA_SHOW_POS_DOCTOR_SMART_00X_ACCEPTANCE.md");
const policy = join(root, "config", "prisma-visual-os", "doctor-policy-00x.json");

function read(p) { return readFileSync(p, "utf8"); }
const checks = [];
function check(name, ok) { checks.push({ name, ok }); }

check("doctor exists", existsSync(doctor));
check("launcher exists", existsSync(launcher));
check("canonical launcher exists", existsSync(alias));
check("design doc exists", existsSync(design));
check("qa doc exists", existsSync(qa));
check("policy exists", existsSync(policy));

if (existsSync(doctor)) {
  const text = read(doctor);
  check("doctor package marker", text.includes("PRISMA_SHOW_POS_DOCTOR_SMART_00X"));
  check("doctor has smart log scan", text.includes("scan_logs_smart"));
  check("doctor separates historical signals", text.includes("historicalSignals"));
  check("doctor suppresses structured ready reports", text.includes("structured JSON ready"));
  check("doctor emits release verdict", text.includes("releaseVerdict"));
  check("doctor computes health score", text.includes("healthScore"));
  check("doctor has self-check", text.includes("--self-check"));
  check("doctor probes pos", text.includes("route /pos"));
  check("doctor probes realtime", text.includes("realtime health"));
  check("doctor verifies 00T", text.includes("verify 00T"));
  check("doctor verifies touch 04H", text.includes("verify touch only 04H"));
}
if (existsSync(launcher)) {
  const text = read(launcher);
  check("launcher calls 00x", text.includes("doctor_prisma_show_pos_scan_00x.py"));
  check("launcher uses descargasf", text.includes("F:\\descargasf"));
}
if (existsSync(alias)) {
  const text = read(alias);
  check("canonical launcher calls 00x", text.includes("doctor_prisma_show_pos_scan_00x.py"));
}

const failed = checks.filter((c) => !c.ok);
if (failed.length) {
  console.error(JSON.stringify({ ok: false, root, package: "PRISMA_SHOW_POS_DOCTOR_SMART_00X", failed, checks }, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ ok: true, root, package: "PRISMA_SHOW_POS_DOCTOR_SMART_00X", checks }, null, 2));
