# PRISMA HTML · Cloudflare Pages Runbook

## Estado

`CONFIGURED_NOT_DEPLOYED`

## Modelo

```text
fuente gobernada
→ build de salida pública
→ verificación no-leak y enlaces
→ dist/
→ Cloudflare Pages
→ URL *.pages.dev
```

## Proyecto

- Project root: `F:\repos\hitech-os-prisma-html\prisma-html`
- Pages project name propuesto: `prisma-html`
- Production branch: `main`
- Public output: `dist`
- Wrangler version gobernada: `4.93.0`

## Seguridad

La salida pública se construye con whitelist. No publica:

- documentación operativa;
- governance y reportes;
- scripts PowerShell/Python;
- bases SQLite;
- ZIPs, logs o backups;
- `.git`, `.wrangler`, `node_modules`;
- rutas locales de Windows;
- tokens o secretos.

## Comandos

```powershell
# construir y verificar dist
& '.\tools\cloudflare\PRISMA_HTML_CLOUDFLARE.ps1' -Action Build

# ver proyectos/deployments, sólo lectura de Cloudflare
& '.\tools\cloudflare\PRISMA_HTML_CLOUDFLARE.ps1' -Action Status

# preview. Requiere que el proyecto Pages ya exista.
& '.\tools\cloudflare\PRISMA_HTML_CLOUDFLARE.ps1' -Action Preview

# producción. Requiere autorización explícita y proyecto Pages existente.
& '.\tools\cloudflare\PRISMA_HTML_CLOUDFLARE.ps1' -Action Production
```

## Creación del proyecto

No se automatiza en el instalador. Elegir primero uno de estos modelos:

1. Git integration, recomendado para deploy automático por `main` y previews por rama.
2. Direct Upload, adecuado si se desea desplegar manualmente desde la PC.

Cloudflare documenta que un proyecto creado como Direct Upload no puede convertirse después a Git integration. Por eso el script no crea el proyecto por sorpresa.

## Gates previos a deploy

- source validator PASS;
- Atlas validator PASS;
- public output validator PASS;
- no rutas `F:\` o `C:\Users\` dentro de `dist`;
- cero `.env`, `.db`, `.zip`, `.ps1`, `.py`, `.md` dentro de `dist`;
- Git status registrado;
- autorización explícita del operador.
