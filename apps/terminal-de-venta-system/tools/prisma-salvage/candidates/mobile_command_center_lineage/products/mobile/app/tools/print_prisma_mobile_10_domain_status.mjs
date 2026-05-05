import fs from "node:fs";
import path from "node:path";
const root = process.cwd();
const pwa = JSON.parse(fs.readFileSync(path.join(root, "public/prisma-mobile-pwa.config.json"), "utf8"));
const bridge = JSON.parse(fs.readFileSync(path.join(root, "../infra/cloudflare/prisma-mobile-cloudflare.config.json"), "utf8"));
console.log(JSON.stringify({ ok: true, domain: pwa.domain, publicUrl: `${pwa.origin}${pwa.appPath}`, installUrl: `${pwa.origin}${pwa.installPath}`, localOrigin: pwa.localOrigin, tunnelName: bridge.tunnelName, cloudflaredRoute: `${bridge.hostname} -> ${bridge.originUrl}`, playStoreDeferred: true }, null, 2));
