import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const systemRoot = root.endsWith('terminal-de-venta-system')
  ? root
  : path.join(root, 'apps', 'terminal-de-venta-system');

const visualRoot = path.join(systemRoot, 'tools', 'prisma-visual-os');

const doctorRootPath = path.join(visualRoot, 'doctor_prisma_show_pos_scan_00u.py');
const doctorImplPath = path.join(visualRoot, 'doctors', 'doctor_prisma_show_pos_scan_00u.py');
const cmdPath = path.join(visualRoot, 'run_prisma_show_pos_doctor_00u.cmd');
const designDoc = path.join(systemRoot, 'docs', 'design', 'PRISMA_SHOW_POS_DOCTOR_00U.md');
const qaDoc = path.join(systemRoot, 'docs', 'qa', 'PRISMA_SHOW_POS_DOCTOR_00U_ACCEPTANCE.md');

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
    || (text.includes('runpy.run_path') && text.includes('/ doctors /') === false && text.includes('doctors'));
}

const checks = [];

function check(name, ok, detail = undefined) {
  const row = { name, ok: Boolean(ok) };
  if (detail !== undefined) row.detail = detail;
  checks.push(row);
}

const rootDoctorText = readMaybe(doctorRootPath);
const implDoctorText = readMaybe(doctorImplPath);
const useImpl = exists(doctorImplPath) && (is00zdPythonShim(rootDoctorText) || rootDoctorText.includes("doctors"));
const doctorText = useImpl ? implDoctorText : rootDoctorText;

check('doctor root exists', exists(doctorRootPath), doctorRootPath);
check('doctor implementation exists or root is full implementation', exists(doctorImplPath) || doctorText.length > 1000, doctorImplPath);
check('doctor root shim compatible', exists(doctorImplPath) ? rootDoctorText.includes('doctor_prisma_show_pos_scan_00u.py') : true);
check('launcher exists', exists(cmdPath), cmdPath);
check('design doc exists', exists(designDoc), designDoc);
check('qa doc exists', exists(qaDoc), qaDoc);

if (doctorText) {
  check('doctor package marker', doctorText.includes('PRISMA_SHOW_POS_DOCTOR_00U'));
  check('doctor scans pos route', doctorText.includes('route /pos'));
  check('doctor checks realtime health', doctorText.includes('realtime health'));
  check('doctor checks no-layout css', doctorText.includes('00T css no-layout markers'));
  check('doctor writes descargasf report', doctorText.includes('F:\\descargasf'));
  check('doctor has self-check mode', doctorText.includes('--self-check'));
  check('doctor can start missing services optionally', doctorText.includes('--start-missing'));
} else {
  check('doctor readable text', false, 'No doctor text found in root or doctors/');
}

if (exists(cmdPath)) {
  const text = read(cmdPath);
  check('launcher calls doctor', text.includes('doctor_prisma_show_pos_scan_00u.py'));
  check('launcher uses target repo', text.includes('F:\\repos\\hitech-os'));
  check('launcher writes descargasf logs', text.includes('F:\\descargasf'));
}

const failed = checks.filter((c) => !c.ok);

const payload = {
  ok: failed.length === 0,
  systemRoot,
  visualRoot,
  package: 'PRISMA_SHOW_POS_DOCTOR_00U_VERIFIER_REORG_AWARE_00ZE',
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
