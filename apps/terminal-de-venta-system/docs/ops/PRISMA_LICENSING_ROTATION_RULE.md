# PRISMA Admin Token Generation Rule

**Fecha:** 2026-07-05
**Superficie:** Cloudflare Worker `licflow3`, Cloud Center 3160, License Admin Bridge
**Marcador interno:** `OPS-20260705-CLI000003-F13`
**Estado:** regla operativa canónica

---

## Objetivo

Documentar la regla segura para generar, rotar y evidenciar `PRISMA_ADMIN_TOKEN` sin exponer el valor real del token.

Esta regla existe porque Cloudflare Worker secrets son write-only: se pueden escribir o reemplazar, pero no recuperar.

---

## Regla principal

No se pide, no se imprime, no se pega y no se guarda el valor real de:

```text
PRISMA_ADMIN_TOKEN
ADMIN_TOKEN
```

Si se requiere un token admin nuevo, se genera localmente en memoria:

```python
import secrets
token = "prisma_" + secrets.token_urlsafe(48)
```

Luego se calcula fingerprint truncado para evidencia:

```python
import hashlib
fingerprint = hashlib.sha256(token.encode("utf-8")).hexdigest()[:16]
```

Después se rota el secret:

```text
wrangler secret put PRISMA_ADMIN_TOKEN
```

o con `npx wrangler`, pasando el valor por stdin desde un proceso seguro.

---

## Evidencia permitida

Sólo se conserva fingerprint truncado.

Fingerprint observado en la última rotación operativa:

```text
aac47e57afec80b6
```

---

## Prohibido

- Pedir token real en chat.
- Imprimir token en consola.
- Guardar token en Markdown.
- Guardar token en JSON.
- Guardar token en logs.
- Guardar token en ZIPs.
- Guardar token en screenshots.
- Pegar token en navegador.
- Intentar recuperar un secret viejo desde Cloudflare.
- Confundir `READ_ONLY_ADMIN_TOKEN_PRESENT` con valor recuperable.

---

## Interpretación operativa

`READ_ONLY_ADMIN_TOKEN_PRESENT` significa que alguna capa puede detectar presencia del token, pero no significa que el operador pueda leer su valor.

Si PowerShell no tiene `PRISMA_ADMIN_TOKEN`, eso no es falla por sí solo. Para operar admin real se debe usar bridge server-side o pedir autorización explícita para rotar un token nuevo.

---

## Operaciones customer-safe

Las siguientes operaciones no requieren admin token:

- Consultar setup customer-safe.
- Reclamar devices con `/api/customer/devices/claim`.
- Consultar status customer-safe.
- Ejecutar refresh customer-safe.
- Verificar que diagnostics sin token responda `ADMIN_TOKEN_REQUIRED`.

---

## Freno de seguridad

Si una respuesta trae:

```json
{
  "secretsExposed": true
}
```

detener la operación y preservar evidencia.
