#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const __filename=fileURLToPath(import.meta.url); const __dirname=path.dirname(__filename); const root=path.resolve(__dirname,"../../../..");
const required=["config/prisma-visual-os/prisma-visual-controls.active.json","styles/prisma-visual-os/prisma-visual-layers.css","styles/prisma-visual-os/prisma-visual-controls.generated.css","docs/design/PRISMA_VISUAL_OS_00D_00E_CONTRACT.md"];
const checks=[["products/mobile/app/app/layout.tsx", "data-prisma-visual-os=\"MOBILE_PULSE\"", "MOBILE_PULSE html binding"], ["products/mobile/app/app/layout.tsx", "prisma-mobile-pulse-binding\\.css", "Mobile binding CSS import"], ["products/mobile/app/app/prisma-mobile-pulse-binding.css", "data-prisma-surface=\"mobile-pulse\"", "Mobile pulse selector"], ["products/mobile/app/package.json", "verify:visual-os-mobile-pulse-00k", "Mobile package script"]];
let failed=false, blocked=false;
for(const rel of required){const full=path.join(root,rel); if(!fs.existsSync(full)){console.error(`BLOCKED_DEPENDENCY missing ${rel}`); blocked=true;} else console.log(`OK dependency ${rel}`);}
for(const item of checks){const [rel,pattern,label]=item; const full=path.join(root,rel); if(!fs.existsSync(full)){console.error(`FAIL missing ${rel} (${label})`); failed=true; continue;} const text=fs.readFileSync(full,"utf8"); if(!(new RegExp(pattern)).test(text)){console.error(`FAIL ${label} not found in ${rel}`); failed=true;} else console.log(`OK ${label}`);}
if(failed) process.exit(1); if(blocked){console.error("PARTIAL_VERIFY binding valid where installed, but Chat A public contract is missing."); process.exit(3);} console.log("OK PRISMA Visual OS Mobile Pulse Binding 00K");
