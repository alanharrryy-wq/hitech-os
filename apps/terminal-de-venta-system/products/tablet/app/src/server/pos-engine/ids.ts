import { randomUUID } from "node:crypto";

export function makePosId(prefix: string) {
  return `${prefix}_${randomUUID()}`;
}

export function makeLocalSaleFolio(now = new Date()) {
  const yyyy = String(now.getFullYear());
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  const hh = String(now.getHours()).padStart(2, "0");
  const mi = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  const short = randomUUID().slice(0, 8).toUpperCase();
  return `T-${yyyy}${mm}${dd}-${hh}${mi}${ss}-${short}`;
}
