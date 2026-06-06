import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const pcApp = process.cwd();
const rel = path.join('components', 'prisma-glass-capsule', 'prisma-glass-capsule.tsx');
const file = path.join(pcApp, rel);
function fail(msg) {
  console.error('FAIL ' + msg);
  process.exit(1);
}
if (!fs.existsSync(file)) fail('missing ' + rel);
const src = fs.readFileSync(file, 'utf8');
const firstLine = src.split(/\r?\n/, 1)[0];
if (firstLine !== "'use client';") {
  fail(`client directive first line must be exact "'use client';", got ${JSON.stringify(firstLine)}`);
}
if (/^use client';/m.test(src)) {
  fail('found malformed directive: use client\';');
}
for (const token of ['styles.refraction', 'styles.lobeLens', 'styles.edgeFrame', 'styles.volumeFrame', 'styles.innerFrame', 'styles.content']) {
  if (!src.includes(token)) fail('missing optical layer token ' + token);
}
console.log('PASS Prisma glass capsule client directive is valid and optical layers are present');
