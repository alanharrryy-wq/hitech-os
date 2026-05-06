import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const marker = "PRISMA_VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM";

const files = {
  pro: "products/tablet/app/app/visual-os/PrismaStudioProQaClient.tsx",
  binding: "products/tablet/app/components/pos/pos-live-binding.tsx",
  css: "products/tablet/app/app/visual-os/prisma-studio-pro-qa.module.css",
  doc: "tools/prisma-visual-os/docs/VISUAL_OS_ROUTE_TRUTH_LAN_POS_BINDING_00ZM.md",
};

function read(rel) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) throw new Error(`missing ${rel}`);
  return fs.readFileSync(abs, "utf8");
}

function must(text, needle, label) {
  if (!text.includes(needle)) throw new Error(`missing ${label}: ${needle}`);
}

const pro = read(files.pro);
const binding = read(files.binding);
const css = read(files.css);
const doc = read(files.doc);

[
  marker,
  "buildPrismaRouteTruth",
  "getDefaultPrismaRealtimeUrl",
  "window.location.hostname",
  "tabletPosUrl",
  "visualOsProUrl",
  "realtimeHealthUrl",
  "realtimeEventsUrl",
  "realtimeStateUrl",
  "routeTruthPanel",
  "data-prisma-vos-route-truth"
].forEach((needle) => must(pro, needle, "pro route truth"));

[
  marker,
  "getPrismaRealtimeBaseUrl",
  "getPrismaRealtimeEventsUrl",
  "getPrismaRealtimeStateUrl",
  "window.location.hostname",
  'payload.surface !== "tablet_pos"'
].forEach((needle) => must(binding, needle, "pos live binding route truth"));

[
  marker,
  ".routeTruthPanel"
].forEach((needle) => must(css, needle, "css route truth"));

[
  marker,
  "/pos",
  ":4177",
  "Tablet POS runtime"
].forEach((needle) => must(doc, needle, "doc route truth"));

const forbidden = [
  "completeSale(",
  "cartTotal =",
  "paymentSession",
  "updateStock(",
  "createTicket("
];

const hits = forbidden.filter((needle) => pro.includes(needle) || binding.includes(needle));
if (hits.length) throw new Error(`forbidden business logic touch signals: ${hits.join(", ")}`);

console.log(JSON.stringify({
  ok: true,
  verifier: marker,
  checks: {
    lanHostRealtime: true,
    tabletPosRoute: true,
    routeTruthPanel: true,
    posLiveBindingLan: true,
    noBusinessLogicTouchSignals: true
  }
}, null, 2));
