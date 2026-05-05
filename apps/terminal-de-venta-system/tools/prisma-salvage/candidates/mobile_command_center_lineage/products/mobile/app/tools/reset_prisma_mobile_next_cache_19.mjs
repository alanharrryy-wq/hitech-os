#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function findMobileAppRoot() {
  const cwd = process.cwd();
  const direct = path.join(cwd, "package.json");
  if (fs.existsSync(direct)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(direct, "utf8"));
      if (pkg.name === "@hitech/mobile" && fs.existsSync(path.join(cwd, "src/components/prisma-app/PrismaMobileDashboard.tsx"))) return cwd;
    } catch {}
  }
  const fromRepo = path.join(cwd, "products/mobile/app");
  if (fs.existsSync(path.join(fromRepo, "package.json"))) return fromRepo;
  throw new Error("No pude ubicar products/mobile/app. Ejecuta desde la raíz del repo o desde products/mobile/app.");
}

const appRoot = findMobileAppRoot();
const nextDir = path.join(appRoot, ".next");
if (!fs.existsSync(nextDir)) {
  console.log(`[PRISMA APP MOBILE 19] No existe caché Next en ${nextDir}. Nada que limpiar.`);
  process.exit(0);
}
try {
  fs.rmSync(nextDir, { recursive: true, force: true, maxRetries: 3, retryDelay: 250 });
  console.log(`[PRISMA APP MOBILE 19] Caché Next eliminado: ${nextDir}`);
  console.log("Arranca de nuevo la app móvil para recompilar limpio.");
} catch (error) {
  console.error(`[PRISMA APP MOBILE 19] No pude eliminar ${nextDir}. Cierra el dev server y vuelve a correr este script.`);
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
