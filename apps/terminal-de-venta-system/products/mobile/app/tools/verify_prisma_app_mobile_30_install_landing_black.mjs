import { readFileSync, existsSync, statSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const checks = [
  {
    file: "src/components/prisma-app/PrismaMobilePwaInstallPage.tsx",
    mustInclude: [
      "data-prisma-surface=\"prisma.mobile.pwa.install.whatsapp.black.landing\"",
      "phoneShell",
      "dynamicIsland",
      "LLEGASTE DESDE WHATSAPP",
      "Instala PRISMA",
      "prisma_whatsapp_install_icon.png"
    ],
    mustNotInclude: ["Dos opciones. Sin menú raro", "mueble sueco"]
  },
  {
    file: "src/components/prisma-app/PrismaMobilePwaInstallCard.tsx",
    mustInclude: [
      "ANDROID",
      "IPHONE",
      "Copiar enlace",
      "Ves ambas opciones porque abriste un enlace de PRISMA desde WhatsApp.",
      "Abrir PRISMA",
      "Si ya la tienes instalada"
    ],
    mustNotInclude: ["🤖", "🍏", "☘️"]
  },
  {
    file: "src/components/prisma-app/prisma-mobile-pwa.module.css",
    mustInclude: [
      ".phoneShell",
      ".phoneScreen",
      ".platformArrow",
      ".androidGlyph",
      ".appleGlyph",
      "backdrop-filter",
      "PRISMA"
    ],
    mustNotInclude: []
  },
  {
    file: "src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
    mustInclude: ["PRISMA en línea. Tu negocio ya responde."],
    mustNotInclude: ["Todo conectado. Ahora toca vender."]
  },
  {
    file: "public/prisma-mobile-sw.js",
    mustInclude: ["prisma-mobile-pwa-v30-install-landing-black", "prisma_whatsapp_install_icon.png"],
    mustNotInclude: []
  },
  {
    file: "public/manifest.webmanifest",
    mustInclude: ["prisma_playstore_icon_192.png", "prisma_playstore_icon_512.png", "apple-touch-icon.png"],
    mustNotInclude: []
  }
];

const requiredAssets = [
  "public/icons/prisma_whatsapp_install_icon.png",
  "public/icons/prisma_playstore_icon_192.png",
  "public/icons/prisma_playstore_icon_512.png",
  "public/icons/prisma_ios_touch_icon_180.png",
  "public/apple-touch-icon.png",
  "public/apple-touch-icon-precomposed.png",
  "public/screenshots/prisma-mobile-pwa-dashboard.png"
];

const failures = [];

for (const check of checks) {
  const path = resolve(root, check.file);
  if (!existsSync(path)) {
    failures.push(`MISSING ${check.file}`);
    continue;
  }
  const text = readFileSync(path, "utf8");
  for (const needle of check.mustInclude) {
    if (!text.includes(needle)) failures.push(`MISSING_TEXT ${check.file}: ${needle}`);
  }
  for (const needle of check.mustNotInclude) {
    if (text.includes(needle)) failures.push(`FORBIDDEN_TEXT ${check.file}: ${needle}`);
  }
}

for (const asset of requiredAssets) {
  const path = resolve(root, asset);
  if (!existsSync(path)) {
    failures.push(`MISSING ${asset}`);
    continue;
  }
  const size = statSync(path).size;
  if (size < 1024) failures.push(`TINY_ASSET ${asset}: ${size} bytes`);
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("OK PRISMA App Mobile 30 install landing black");
