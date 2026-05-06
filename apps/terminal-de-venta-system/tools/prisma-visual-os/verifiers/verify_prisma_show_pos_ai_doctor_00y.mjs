import { readFileSync, existsSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const systemRoot = root.endsWith('terminal-de-venta-system')
  ? root
  : path.join(root, 'apps', 'terminal-de-venta-system');

const visualRoot = path.join(systemRoot, 'tools', 'prisma-visual-os');
const doctorRootPath = path.join(visualRoot, 'ai_doctor_prisma_show_pos_00y.py');
const doctorImplPath = path.join(visualRoot, 'doctors', 'ai_doctor_prisma_show_pos_00y.py');

function exists(file) { return existsSync(file); }
function read(file) { return readFileSync(file, 'utf8'); }
function readMaybe(file) { return exists(file) ? read(file) : ''; }
function is00zdPythonShim(text) {
  return text.includes('PRISMA 00ZD shim target missing')
    || (text.includes('runpy.run_path') && text.includes('doctors'))
    || text.includes("/ 'doctors' /")
    || text.includes("\\ 'doctors' \\");
}

const required = [
  'tools/prisma-visual-os/ai_doctor_prisma_show_pos_00y.py',
  'tools/prisma-visual-os/run_prisma_show_pos_ai_doctor_00y.cmd',
  'tools/prisma-visual-os/run_prisma_show_pos_ai_doctor.cmd',
  'config/prisma-visual-os/ai-doctor-policy-00y.json',
  'docs/design/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y.md',
  'docs/qa/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y_ACCEPTANCE.md',
];

const checks = [];
function add(name, ok, detail = undefined) {
  const row = { name, ok: Boolean(ok) };
  if (detail !== undefined) row.detail = detail;
  checks.push(row);
}

for (const rel of required) {
  add(`${rel} exists`, exists(path.join(systemRoot, rel)), path.join(systemRoot, rel));
}
add('doctor implementation exists or root is full implementation', exists(doctorImplPath) || readMaybe(doctorRootPath).length > 1000, doctorImplPath);

const rootDoctorText = readMaybe(doctorRootPath);
const implDoctorText = readMaybe(doctorImplPath);
const useImpl = exists(doctorImplPath) && (is00zdPythonShim(rootDoctorText) || rootDoctorText.includes('doctors/ai_doctor_prisma_show_pos_00y.py'));
const doctor = useImpl ? implDoctorText : rootDoctorText;

add('doctor root shim compatible', exists(doctorImplPath) ? rootDoctorText.includes('ai_doctor_prisma_show_pos_00y.py') : true);
add('doctor package marker', doctor.includes('PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y'));
add('doctor offline only', doctor.includes('offline_rules') && doctor.includes('zero_api_cost'));
add('doctor reads doctor 00X', doctor.includes('prisma_show_pos_doctor_smart_00x_*.json'));
add('doctor computes classification', doctor.includes('def classify'));
add('doctor proposes next package', doctor.includes('def propose_next_package'));
add('doctor writes markdown', doctor.includes('render_markdown'));
add('doctor has self-check', doctor.includes('--self-check'));
add('doctor does not import openai', !doctor.includes('import openai'));

const policyPath = path.join(systemRoot, 'config/prisma-visual-os/ai-doctor-policy-00y.json');
let policy = {};
try {
  policy = exists(policyPath) ? JSON.parse(read(policyPath)) : {};
} catch (error) {
  policy = { __parseError: String(error) };
}
add('policy provider none', policy.defaultProvider === 'none');
add('policy no runtime mutation', policy.allowRuntimeMutation === false);
add('policy no api cost', policy.apiCost === 'none');

const launcherPath = path.join(visualRoot, 'run_prisma_show_pos_ai_doctor.cmd');
const launcher = exists(launcherPath) ? read(launcherPath) : '';
add('canonical launcher calls 00Y', launcher.includes('ai_doctor_prisma_show_pos_00y.py'));
add('canonical launcher writes descargasf', launcher.includes('F:\\descargasf'));

const failed = checks.filter((c) => !c.ok);
const out = {
  ok: failed.length === 0,
  systemRoot,
  visualRoot,
  package: 'PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y_VERIFIER_REORG_AWARE_00ZE',
  doctorRootPath,
  doctorImplPath,
  resolvedDoctorSource: useImpl ? doctorImplPath : doctorRootPath,
  failed,
  checks,
};
console.log(JSON.stringify(out, null, 2));
if (failed.length) process.exit(1);
