        import fs from 'node:fs';
        import path from 'node:path';
        export function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }
        export function writeJson(p, value) { fs.mkdirSync(path.dirname(p), { recursive: true }); fs.writeFileSync(p, JSON.stringify(value, null, 2) + '\\n', 'utf8'); }
