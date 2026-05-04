import fs from "node:fs";
import path from "node:path";

const systemRoot = process.cwd();
const readmePath = path.join(systemRoot, "tools", "prisma-visual-os", "README_PRISMA_VISUAL_OS_LIVE_STUDIO_00O_00T.md");
const designPath = path.join(systemRoot, "docs", "design", "PRISMA_VISUAL_OS_README_STATUS_00W.md");
const qaPath = path.join(systemRoot, "docs", "qa", "PRISMA_VISUAL_OS_README_STATUS_00W_ACCEPTANCE.md");

function exists(filePath) {
  return fs.existsSync(filePath);
}

function read(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

const checks = [];
function check(name, ok) {
  checks.push({ name, ok });
}

check("readme exists", exists(readmePath));
check("design doc exists", exists(designPath));
check("qa doc exists", exists(qaPath));

let text = "";
if (exists(readmePath)) text = read(readmePath);

check("readme has 00W marker", text.includes("00W README Status"));
check("readme declares 00T safe no layout", text.includes("00T") && text.includes("safe-no-layout"));
check("readme declares 00U doctor", text.includes("00U") && text.includes("doctor"));
check("readme declares 00V touch only", text.includes("00V") && text.includes("Touch Only"));
check("readme mentions doctor launcher", text.includes("run_prisma_show_pos_doctor_00u.cmd"));
check("readme mentions 04H verifier", text.includes("verify_pos_touch_only_actions_04h.mjs"));
check("readme mentions this verifier", text.includes("verify_prisma_visual_os_readme_status_00w.mjs"));
check("readme keeps descargasf as logs", text.includes("F:\\descargasf"));
check("readme forbids layout moving CSS", text.includes("no acepta CSS live que mueva layout") || text.includes("mueva layout"));
check("readme keeps POS selling as conclusion", text.includes("POS vende"));

const ok = checks.every((item) => item.ok);
const result = {
  ok,
  systemRoot,
  package: "PRISMA_VISUAL_OS_README_STATUS_00W",
  checks,
};

if (!ok) {
  console.error(JSON.stringify(result, null, 2));
  process.exit(1);
}

console.log(JSON.stringify(result, null, 2));
