import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const systemRoot = root.endsWith('terminal-de-venta-system') ? root : path.join(root, 'apps', 'terminal-de-venta-system');
const doctorPath = path.join(systemRoot, 'tools', 'prisma-visual-os', 'doctor_prisma_show_pos_scan_00u.py');
const cmdPath = path.join(systemRoot, 'tools', 'prisma-visual-os', 'run_prisma_show_pos_doctor_00u.cmd');
const designDoc = path.join(systemRoot, 'docs', 'design', 'PRISMA_SHOW_POS_DOCTOR_00U.md');
const qaDoc = path.join(systemRoot, 'docs', 'qa', 'PRISMA_SHOW_POS_DOCTOR_00U_ACCEPTANCE.md');

function read(file) {
  return fs.readFileSync(file, 'utf8');
}

const checks = [];
function check(name, ok) {
  checks.push({ name, ok: Boolean(ok) });
}

check('doctor exists', fs.existsSync(doctorPath));
check('launcher exists', fs.existsSync(cmdPath));
check('design doc exists', fs.existsSync(designDoc));
check('qa doc exists', fs.existsSync(qaDoc));

if (fs.existsSync(doctorPath)) {
  const text = read(doctorPath);
  check('doctor package marker', text.includes('PRISMA_SHOW_POS_DOCTOR_00U'));
  check('doctor scans pos route', text.includes('route /pos'));
  check('doctor checks realtime health', text.includes('realtime health'));
  check('doctor checks no-layout css', text.includes('00T css no-layout markers'));
  check('doctor writes descargasf report', text.includes('F:\\descargasf'));
  check('doctor has self-check mode', text.includes('--self-check'));
  check('doctor can start missing services optionally', text.includes('--start-missing'));
}

if (fs.existsSync(cmdPath)) {
  const text = read(cmdPath);
  check('launcher calls doctor', text.includes('doctor_prisma_show_pos_scan_00u.py'));
  check('launcher uses target repo', text.includes('F:\\repos\\hitech-os'));
  check('launcher writes descargasf logs', text.includes('F:\\descargasf'));
}

const failed = checks.filter((c) => !c.ok);
if (failed.length) {
  console.error(JSON.stringify({ ok: false, systemRoot, failed, checks }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({ ok: true, systemRoot, package: 'PRISMA_SHOW_POS_DOCTOR_00U', checks }, null, 2));
