import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
const root = process.argv[2];
if (!root) throw new Error("Usage: node verify_pc_suppliers_real_actions_09.mjs <pc-app-root>");
function read(rel){const file=join(root,rel); if(!existsSync(file)) throw new Error(`Missing ${rel}`); return readFileSync(file,"utf8");}
function must(text,needle,label){if(!text.includes(needle)) throw new Error(`Missing ${label}: ${needle}`); console.log(`OK ${label}`);}
function mustNot(text,needle,label){if(text.includes(needle)) throw new Error(`Forbidden ${label}: ${needle}`); console.log(`OK no ${label}`);}
const workbench=read("components/suppliers/smart-purchase-workbench.tsx");
const cockpit=read("components/suppliers/supplier-action-cockpit.tsx");
const css=read("app/suppliers-ux-v08.css");
const doc=read("docs/PC_SUPPLIERS_REAL_ACTIONS_09.md");
must(workbench,"SupplierActionCockpit","cockpit mounted");
must(cockpit,'"use client"',"client component");
must(cockpit,"Simular compra","simulation action");
must(cockpit,"Crear pedido sugerido","order action");
must(cockpit,"Confirmar recepción","receiving action");
must(cockpit,"Registrar pago","payment action");
must(cockpit,"Ver auditoría","audit action");
must(cockpit,"fetch(endpoint","post action fetch");
must(css,"supplier-action-cockpit-v09","v09 styles");
must(css,"supplier-action-result-v09","v09 result styles");
must(doc,"No introduce persistencia real","v10 boundary");
mustNot(cockpit,"POST /api","visible api route copy");
mustNot(cockpit,"order_cutoff","raw order cutoff");
mustNot(cockpit,"expected_receiving","raw expected receiving");
mustNot(cockpit,"blocked","raw blocked");
mustNot(workbench,"sincronización/module.manifest","translated import path");
console.log("NODE READY suppliers real actions v09 16 checks");
