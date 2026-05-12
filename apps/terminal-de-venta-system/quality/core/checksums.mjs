import crypto from 'node:crypto';
import fs from 'node:fs';
export function sha256File(p) { const h = crypto.createHash('sha256'); h.update(fs.readFileSync(p)); return h.digest('hex'); }
export function sha256Text(text) { return crypto.createHash('sha256').update(String(text)).digest('hex'); }
