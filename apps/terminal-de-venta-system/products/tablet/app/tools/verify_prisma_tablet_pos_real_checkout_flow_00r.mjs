#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const failures = [];
function read(rel){ const p=path.join(root,rel); if(!fs.existsSync(p)){failures.push(`missing ${rel}`); return '';} return fs.readFileSync(p,'utf8'); }
function inc(rel, needle){ if(!read(rel).includes(needle)) failures.push(`${rel} missing ${needle}`); }
function notInc(rel, needle){ if(read(rel).includes(needle)) failures.push(`${rel} still includes ${needle}`); }
inc('products/tablet/app/components/pos/pos-payment-panel.tsx','Método de pago');
inc('products/tablet/app/components/pos/pos-payment-panel.tsx','OK, generar ticket');
inc('products/tablet/app/components/pos/pos-payment-panel.tsx','Cambio a entregar');
inc('products/tablet/app/components/pos/pos-payment-panel.tsx','Billetes y monedas sugeridas');
inc('products/tablet/app/components/pos/pos-ticket-panel.tsx','Cancelar venta');
inc('products/tablet/app/components/pos/pos-ticket-panel.tsx','Reembolso');
inc('products/tablet/app/src/lib/pos/payment-state.ts','Transferencia interbancaria');
inc('products/tablet/app/src/lib/pos/payment-state.ts','Tarjeta bancaria');
inc('products/tablet/app/src/lib/pos/payment-state.ts','Efectivo');
inc('products/tablet/app/src/lib/pos/payment-tender.ts','Toca OK para generar ticket');
inc('products/tablet/app/components/pos/pos.module.css','PRISMA_POS_REAL_CHECKOUT_FLOW_00R::START');
inc('products/tablet/app/components/pos/pos.module.css','.paymentOverlay');
inc('products/tablet/app/components/pos/pos.module.css','.paymentOkButton');
inc('products/tablet/app/components/pos/pos.module.css','.cashSuggestions');
notInc('products/tablet/app/components/pos/pos-payment-panel.tsx','Confirmar venta</h2>');
if(failures.length){ console.error('BLOCKED PRISMA_TABLET_POS_REAL_CHECKOUT_FLOW_00R'); for(const f of failures) console.error(`- ${f}`); process.exit(1); }
console.log('READY PRISMA_TABLET_POS_REAL_CHECKOUT_FLOW_00R');
