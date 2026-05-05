import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

const root = process.cwd();
const checks = [
  {
    file: "src/components/prisma-app/PrismaMobileDashboard.tsx",
    mustInclude: ["PrismaMobilePremiumNavigator"],
    mustNotInclude: ["PrismaMobilePwaInstallCard compact", "./PrismaMobilePwaInstallCard"]
  },
  {
    file: "src/components/prisma-app/PrismaMobilePwaInstallPage.tsx",
    mustInclude: ["LLEGASTE DESDE WHATSAPP", "Instala PRISMA", "prisma_whatsapp_install_icon.png", "phoneShell", "dynamicIsland"],
    mustNotInclude: ["Dos opciones. Sin menú raro", "mueble sueco"]
  },
  {
    file: "src/components/prisma-app/PrismaMobilePwaInstallCard.tsx",
    mustInclude: ["Ves ambas opciones porque abriste un enlace de PRISMA desde WhatsApp", "Abrir PRISMA", "Si ya la tienes instalada", "ANDROID", "IPHONE", "Copiar enlace"],
    mustNotInclude: []
  },
  {
    file: "src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
    mustInclude: ["PRISMA en línea. Tu negocio ya responde."],
    mustNotInclude: ["La conexión existe; falta que el negocio genere datos de hoy.", "Todo conectado. Ahora toca vender."]
  }
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



const requiredAssets = [
  "public/icons/prisma_whatsapp_install_icon.png",
  "public/icons/prisma_playstore_icon_192.png",
  "public/icons/prisma_playstore_icon_512.png",
  "public/icons/prisma_ios_touch_icon_180.png",
  "public/apple-touch-icon.png",
  "public/apple-touch-icon-precomposed.png",
  "public/screenshots/prisma-mobile-pwa-dashboard.png"
];

for (const asset of requiredAssets) {
  if (!existsSync(resolve(root, asset))) failures.push(`MISSING ${asset}`);
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exit(1);
}

console.log("OK PRISMA App Mobile 29 WhatsApp install gate");
