# PRISMA HTML · Sistema narrativo y Atlas

Proyecto canónico:

`F:\repos\hitech-os-prisma-html\prisma-html`

## Entradas públicas

- Recorrido principal: `index.html`
- Catálogo UI: `sistema-ui/catalogo/index.html`
- Atlas completo: `extras/atlasfin/index.html`

## Estado integrado

- Recorrido narrativo principal presente.
- Atlas: 27 páginas, 26 secciones y 418 elementos.
- Glass owner repair estable incorporado.
- Premium target owners incorporados para Product Card/CAFÉ, Circular Progress y overlays.
- Evidencia y targets premium conservados bajo `docs/evidence/premium-overlay-glass/`.
- Cloudflare Pages preparado con salida pública gobernada `dist/`.
- Publicación autorizada por el usuario y trazada en el PR existente `#178`.
- Deploy de Cloudflare Pages, DNS y dominio todavía no ejecutados por este paquete.

## Validación

```powershell
python tools/validate_project.py --root . --report reports/source-validator-current.json
python extras/atlasfin/generator/validate_atlas.py extras/atlasfin
& '.\tools\cloudflare\PRISMA_HTML_CLOUDFLARE.ps1' -Action Build
```

## Cloudflare

Este sitio usa Cloudflare Pages para publicación estática. No usa el Worker LICFLOW3 ni los launchers de Cloudflare Tunnel para servir su contenido.

- Runbook: `docs/ops/PRISMA_HTML_CLOUDFLARE_PAGES_RUNBOOK.md`
- Rollback: `docs/ops/PRISMA_HTML_CLOUDFLARE_PAGES_ROLLBACK.md`
- Contrato: `governance/PRISMA_HTML_CLOUDFLARE_PAGES_CONTRACT.json`

## Límites

Este paquete no modifica Tablet, PC, Mobile, Chart Lab, Control Center, bases de datos, Prisma schema, procesos, puertos, Tunnel, Worker, D1, DNS, Git remoto ni Cloudflare.
