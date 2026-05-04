#!/usr/bin/env node
/* 11C sanitized: no embedded PEM private key. Reads local-runtime dev signing material. */
const fs=require("fs"), path=require("path"), crypto=require("crypto");
const root=path.resolve(__dirname,"..","..");
const matPath=path.join(root,"local-runtime","license-keys","dev","dev-signing-secret.local.json");
function b64u(b){return Buffer.from(b).toString("base64").replace(/=/g,"").replace(/\+/g,"-").replace(/\//g,"_");}
function canonical(o){return JSON.stringify(o,Object.keys(o).sort());}
function material(){const raw=JSON.parse(fs.readFileSync(matPath,"utf8")); const keyId=raw.key_id||raw.keyId; const sec=raw.secret_b64url||raw.secretMaterialBase64Url; const alg=raw.algorithm==="HS256_DEV_ONLY"?"HS256_DEV_LOCAL":(raw.algorithm||"HS256_DEV_LOCAL"); if(!keyId||!sec) throw new Error("Missing local dev signing material fields"); return {keyId,sec,alg};}
function signPayload(payload){const m=material(); const secret=Buffer.from(m.sec.replace(/-/g,"+").replace(/_/g,"/"),"base64"); const value=b64u(crypto.createHmac("sha256",secret).update(canonical(payload)).digest()); return {payload, signature:{schemaVersion:"11C",algorithm:m.alg,keyId:m.keyId,value}};}
if(require.main===module){process.stdout.write(JSON.stringify(signPayload({licenseId:"lic_dev_signed_local",plan:"TABLET_PC_REQUIRED",state:"active",issuedAt:new Date().toISOString()}),null,2)+"
");}
module.exports={signPayload};
