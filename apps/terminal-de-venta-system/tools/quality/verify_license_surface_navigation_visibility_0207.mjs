import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), "utf8");
const failures = [];

function expect(condition, message) {
  if (!condition) failures.push(message);
}

const tabletShell = read("products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx");
const tabletNav = read("products/tablet/app/components/tablet-shell/tablet-nav.ts");
const pcNav = read("products/pc/app/src/composition/navigation.ts");
const pcProduct = read("products/pc/app/src/uiux/pc-product-navigation.ts");
const pcManifest = JSON.parse(read("products/pc/app/src/uiux/pc-product-navigation.manifest.json"));

expect(tabletNav.includes('"/settings/license"'), "Tablet nav debe conservar /settings/license como item de navegación existente.");
expect(tabletShell.includes('"/settings/license"'), "Tablet shell debe exponer /settings/license en shell/dock.");
expect(tabletShell.includes('currentPath === "/settings/license"'), "Tablet shell debe clasificar /settings/license fuera de reference-root.");
expect(pcNav.includes('"/settings/license": { description: "Licencia, activación y modos offline/online/híbrido"'), "PC primary presentation debe tener shortcut de /settings/license.");
expect(pcProduct.includes("route: '/settings/license'") && pcProduct.includes("visibility: 'final'") && pcProduct.includes("finalMenu: true"), "PC product navigation debe promover /settings/license como final visible.");
expect(pcManifest.pc.finalMenuRoutes.includes("/settings/license"), "PC manifest debe incluir /settings/license en finalMenuRoutes.");
expect(pcProduct.includes("route: '/license-runtime'") && pcProduct.includes("visibility: 'submenu'") && pcProduct.includes("finalMenu: false"), "PC /license-runtime debe permanecer secundario/soporte, no final primary.");

if (failures.length) {
  console.error("FAIL LICENSE_SURFACE_NAVIGATION_VISIBILITY_0207");
  for (const failure of failures) console.error("- " + failure);
  process.exit(1);
}

console.log("PASS LICENSE_SURFACE_NAVIGATION_VISIBILITY_0207");
console.log("Existing license surfaces are visible without creating new LICDESK/ADLANT4/LICFLOW2 systems.");
