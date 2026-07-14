# PRISMA HTML · Baseline modular y páginas narrativas

Proyecto HTML aislado dentro del Draft PR `feature/prisma-html-investor-site`.

Conserva únicamente el código activo necesario para renderizar, desarrollar y validar:

- Página 1: qué es PRISMA y cómo convierte operación en verdad útil;
- Página 2: investor deck interactivo;
- Página 3: comparador estratégico de diferenciación;
- catálogo premium del sistema UI;
- tokens, temas, layouts, componentes y patrones compartidos;
- módulos JavaScript ES;
- logo aprobado del baseline CLEAN1;
- configuración ligera de VS Code;
- servidor y validador local.

## Entradas

- Índice: `index.html`
- Página 1: `paginas/pagina-1-prisma/index.html`
- Página 2: `paginas/pagina-2-inversionistas/index.html`
- Página 3: `paginas/pagina-3-por-que-prisma/index.html`
- Catálogo UI: `sistema-ui/catalogo/index.html`

## Página 3

La Página 3 responde:

> ¿Por qué PRISMA y no otro POS, ERP, dashboard o conjunto de integraciones?

Incluye:

- comparador por categoría;
- reconciliación interactiva de cifras contradictorias;
- cuatro decisiones estructurales;
- lentes por rol;
- composición responsive desde iPhone SE.

La versión anterior permanece como respaldo histórico en:

`stash/prisma-html-page3-before-clean-baseline-20260713`

## Identidad

Todas las páginas activas utilizan:

`assets/images/prisma-logo-approved-baseline.png`

El alias `assets/images/prisma-logo.svg` apunta a ese mismo asset para conservar compatibilidad con las páginas existentes.

## Previsualización local

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

Evidencia específica de Página 3:

- `governance/PAGE3_AUTHORITY_READSET.lock.json`
- `governance/PAGE3_VISUAL_CHANGE_MANIFEST.json`
- `reports/page3-static-validation.json`

## Estado

- Clasificación: `BUILD`
- Validación estática: `PASS`, 330 checks, 0 errores
- Revisión móvil: pendiente
- Certificación visual: pendiente
- Merge a `main`: bloqueado hasta aprobación explícita

## Reglas activas

- Sin `document.write()`.
- Sin `!important`.
- Sin imágenes Base64 activas.
- JavaScript compartido mediante ES Modules.
- CSS de página reservado para composición exclusiva.
- Sin tocar Tablet, PC, Mobile, Chart Lab, bases de datos, procesos o puertos.
