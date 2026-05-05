# PRISMA License Server Signing Scan Policy 11D

## Objetivo

Cerrar el bloqueo de 11C sin relajar seguridad: los corpus de regresion que contienen bloques PEM intencionales deben tratarse como fixtures aprobados, mientras que cualquier PEM privado real en scripts, configuracion, runtime o codigo operativo debe bloquear la entrega.

## Regla operativa

Un bloque PEM de private key se considera permitido solo cuando cumple las tres condiciones:

1. Esta bajo `tooling/licensing/`.
2. El archivo es JSONL/JSON/MD de fixture, regression, tamper o corpus aprobado.
3. La ruta coincide con la politica de allowlist instalada en `tooling/licensing/server11d/repo_secret_scan_policy_11d.json`.

Todo lo demas bloquea.

## Alcance

- Reemplaza el smoke `license-server-signing-smoke` por el motor 11D.
- Conserva firma local dev usando el material generado por 10D/11B.
- Conserva rechazo de tamper de payload, firma y keyId.
- Conserva bloqueo de material dev en production.
- Sanitiza `tooling/licensing/create_dev_signed_license.js` si conserva PEM privado embebido.

## No objetivos

- No mete KMS real.
- No permite llaves privadas productivas en repo.
- No ignora hallazgos fuera de fixtures aprobados.

## Criterio de salida

`terminal_de_venta.cmd license-server-signing-smoke` debe terminar en `FINAL READY` cuando:

- el material local dev firma y verifica;
- el repo no contiene PEMs privados reales;
- los PEMs intencionales en corpus aprobados se reportan como fixtures permitidos;
- los tamper cases son rechazados;
- production se niega a firmar con material dev-local.
