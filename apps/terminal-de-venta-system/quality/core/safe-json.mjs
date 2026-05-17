import fs from 'node:fs';
import path from 'node:path';

export function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

export function writeJson(filePath, value) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

export function parseJsonText(text, label = 'JSON') {
  try {
    return { ok: true, value: JSON.parse(text), error: null, label };
  } catch (error) {
    return { ok: false, value: null, error: error?.message || String(error), label };
  }
}

export function readJsonSafe(filePath) {
  try {
    return { ok: true, value: readJson(filePath), error: null, path: filePath };
  } catch (error) {
    return { ok: false, value: null, error: error?.message || String(error), path: filePath };
  }
}
