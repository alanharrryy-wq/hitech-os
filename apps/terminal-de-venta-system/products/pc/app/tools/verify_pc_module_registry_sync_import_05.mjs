#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.argv[2];
if (!root) {
  console.error("Uso: node verify_pc_module_registry_sync_import_05.mjs <products/pc/app>");
  process.exit(2);
}

const registryPath = join(root, "src", "composition", "module-registry.ts");
const syncManifestPath = join(root, "src", "modules", "sync", "module.manifest.ts");
const suppliersManifestPath = join(root, "src", "modules", "suppliers", "module.manifest.ts");

function fail(message) {
  console.error(`ERROR ${message}`);
  process.exit(1);
}

if (!existsSync(registryPath)) fail(`no existe ${registryPath}`);
if (!existsSync(syncManifestPath)) fail(`no existe ${syncManifestPath}`);
if (!existsSync(suppliersManifestPath)) fail(`no existe ${suppliersManifestPath}`);

const source = readFileSync(registryPath, "utf8");

const requiredSnippets = [
  'import { SyncModule } from "@/modules/sync/module.manifest";',
  'import { SuppliersModule } from "@/modules/suppliers/module.manifest";',
  "SyncModule,",
  "SuppliersModule,"
];

for (const snippet of requiredSnippets) {
  if (!source.includes(snippet)) fail(`falta snippet requerido: ${snippet}`);
}

const forbiddenSnippets = [
  "@/modules/sincronización",
  "@/modules/sincronizacion",
  "SincronizaciónModule",
  "SincronizacionModule"
];

for (const snippet of forbiddenSnippets) {
  if (source.includes(snippet)) fail(`sigue presente texto prohibido: ${snippet}`);
}

console.log("OK module-registry usa ruta técnica sync y label visible queda en el manifest.");
