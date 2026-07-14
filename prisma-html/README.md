# PRISMA HTML · Baseline limpio para GitHub

Baseline funcional extraído de `prismaui clean1 1307 1943`.

Este árbol conserva únicamente el proyecto activo necesario para renderizar, desarrollar y validar:

- portada PRISMA;
- deck de inversionistas;
- catálogo del sistema UI;
- tokens, temas, layouts, componentes y patrones compartidos;
- módulos JavaScript ES;
- asset vectorial compacto del logotipo para el baseline remoto;
- configuración ligera de VS Code;
- servidor y validador local.

## Entradas

- Índice: `index.html`
- Página 1: `paginas/pagina-1-prisma/index.html`
- Página 2: `paginas/pagina-2-inversionistas/index.html`
- Catálogo UI: `sistema-ui/catalogo/index.html`

## Previsualización

Abre `PRISMA-HTML.code-workspace` en VS Code y utiliza Live Preview, o ejecuta:

```text
PREVISUALIZAR.cmd
```

El servidor local abre `http://127.0.0.1:8010/`.

## Validación

```powershell
python -m pip install -r requirements-dev.txt
python tools\validate_project.py --root . --report validation.json
```

## Alcance de este checkpoint

- Página 3 no está incluida.
- Página 3 permanece respaldada en `stash/prisma-html-page3-before-clean-baseline-20260713`.
- No contiene backups, capturas, diffs ni históricos.
- No contiene wrappers de instalación o rollback del ZIP original.
- El PNG binario del logo se sustituyó por un SVG compacto para la transferencia remota; su equivalencia visual se revisará desde móvil antes de aprobar el baseline.

## Estado

- Validación estática local: `PASS`, 305 checks, 0 errores.
- Certificación visual: pendiente.
- Merge a `main`: bloqueado hasta aprobación explícita.

## Reglas activas

- Sin `document.write()`.
- Sin `!important`.
- Sin imágenes Base64 activas.
- JavaScript compartido mediante ES Modules.
- CSS de página reservado para composición exclusiva.
