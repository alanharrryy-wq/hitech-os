import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const systemRoot = root.endsWith('terminal-de-venta-system')
  ? root
  : path.join(root, 'apps', 'terminal-de-venta-system');

const visualRoot = path.join(systemRoot, 'tools', 'prisma-visual-os');

const doctorRootPath = path.join(visualRoot, 'doctor_prisma_show_pos_scan_00x.py');
const doctorImplPath = path.join(visualRoot, 'doctors', 'doctor_prisma_show_pos_scan_00x.py');
const launcher = path.join(visualRoot, 'run_prisma_show_pos_doctor_00x.cmd');
const alias = path.join(visualRoot, 'run_prisma_show_pos_doctor.cmd');
const design = path.join(systemRoot, 'docs', 'design', 'PRISMA_SHOW_POS_DOCTOR_SMART_00X.md');
const qa = path.join(systemRoot, 'docs', 'qa', 'PRISMA_SHOW_POS_DOCTOR_SMART_00X_ACCEPTANCE.md');
const policy = path.join(systemRoot, 'config', 'prisma-visual-os', 'doctor-policy-00x.json');

function exists(file) {
  return fs.existsSync(file);
}

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

function readMaybe(file) {
  return exists(file) ? read(file) : '';
}

function is00zdPythonShim(text) {
  return text.includes('PRISMA 00ZD shim target missing')
    || (text.includes('runpy.run_path') && text.includes('doctors'))
    || text.includes("/ 'doctors' /")
    || text.includes("\\ 'doctors' \\");
}

const checks = [];
function check(name, ok, detail = undefined) {
  const row = { name, ok: Boolean(ok) };
  if (detail !== undefined) row.detail = detail;
  checks.push(row);
}

const rootDoctorText = readMaybe(doctorRootPath);
const implDoctorText = readMaybe(doctorImplPath);
const useImpl = exists(doctorImplPath) && (is00zdPythonShim(rootDoctorText) || rootDoctorText.includes('doctors/doctor_prisma_show_pos_scan_00x.py'));
const doctorText = useImpl ? implDoctorText : rootDoctorText;

check('doctor root exists', exists(doctorRootPath), doctorRootPath);
check('doctor implementation exists or root is full implementation', exists(doctorImplPath) || doctorText.length > 1000, doctorImplPath);
check('doctor root shim compatible', exists(doctorImplPath) ? rootDoctorText.includes('doctor_prisma_show_pos_scan_00x.py') : true);
check('launcher exists', exists(launcher), launcher);
check('canonical launcher exists', exists(alias), alias);
check('design doc exists', exists(design), design);
check('qa doc exists', exists(qa), qa);
check('policy exists', exists(policy), policy);

if (doctorText) {
  check('doctor package marker', doctorText.includes('PRISMA_SHOW_POS_DOCTOR_SMART_00X'));
  check('doctor has smart log scan', doctorText.includes('scan_logs_smart'));
  check('doctor separates historical signals', doctorText.includes('historicalSignals'));
  check('doctor suppresses structured ready reports', doctorText.includes('structured JSON ready'));
  check('doctor emits release verdict', doctorText.includes('releaseVerdict'));
  check('doctor computes health score', doctorText.includes('healthScore'));
  check('doctor has self-check', doctorText.includes('--self-check'));
  check('doctor probes pos', doctorText.includes('route /pos'));
  check('doctor probes realtime', doctorText.includes('realtime health'));
  check('doctor verifies 00T', doctorText.includes('verify 00T'));
  check('doctor verifies touch 04H', doctorText.includes('verify touch only 04H'));
} else {
  check('doctor readable text', false, 'No doctor text found in root or doctors/');
}

if (exists(launcher)) {
  const text = read(launcher);
  check('launcher calls 00x', text.includes('doctor_prisma_show_pos_scan_00x.py'));
  check('launcher uses descargasf', text.includes('F:\\descargasf'));
}
if (exists(alias)) {
  const text = read(alias);
  check('canonical launcher calls 00x', text.includes('doctor_prisma_show_pos_scan_00x.py'));
}

const failed = checks.filter((c) => !c.ok);
const payload = {
  ok: failed.length === 0,
  systemRoot,
  visualRoot,
  package: 'PRISMA_SHOW_POS_DOCTOR_SMART_00X_VERIFIER_REORG_AWARE_00ZE',
  doctorRootPath,
  doctorImplPath,
  resolvedDoctorSource: useImpl ? doctorImplPath : doctorRootPath,
  failed,
  checks,
};

if (failed.length) {
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}
console.log(JSON.stringify(payload, null, 2));
