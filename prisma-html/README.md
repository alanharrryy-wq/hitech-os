# PRISMA HTML · Baseline modular y páginas narrativas

Proyecto HTML aislado dentro del Draft PR `feature/prisma-html-investor-site`.

Conserva únicamente el código activo necesario para renderizar, desarrollar y validar:

- Página 1: qué es PRISMA y cómo convierte operación en verdad útil;
- Página 2: investor deck interactivo;
- Página 3: comparador estratégico de diferenciación;
- Página 4: mapa interactivo del ecosistema del producto;
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
- Página 4: `paginas/pagina-4-ecosistema-producto/index.html`
- Catálogo UI: `sistema-ui/catalogo/index.html`

## Página 3 · Por qué PRISMA

Responde:

> ¿Por qué PRISMA y no otro POS, ERP, dashboard o conjunto de integraciones?

Incluye comparador por categoría, reconciliación interactiva, decisiones estructurales y lentes por rol.

La versión anterior permanece como respaldo histórico en:

`stash/prisma-html-page3-before-clean-baseline-20260713`

## Página 4 · Ecosistema del producto

Responde:

> ¿Qué productos y superficies componen PRISMA, y por qué no son fuentes de verdad separadas?

Incluye:

- órbita interactiva de seis superficies;
- contratos de responsabilidad para Tablet, PC, Mobile, Chart Lab, Control Center y Web;
- recorrido Scope → Evento → Evidencia → Canonical → Proyección → UI;
- cuatro familias de capacidades;
- navegación por teclado;
- composición responsive con breakpoint específico para iPhone SE.

La tesis central es:

> Una superficie no posee la verdad. La proyecta desde el núcleo neutral.

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

Evidencia de Página 3:

- `governance/PAGE3_AUTHORITY_READSET.lock.json`
- `governance/PAGE3_VISUAL_CHANGE_MANIFEST.json`
- `reports/page3-static-validation.json`

Evidencia de Página 4:

- `governance/PAGE4_AUTHORITY_READSET.lock.json`
- `governance/PAGE4_VISUAL_CHANGE_MANIFEST.json`
- `reports/page4-static-validation.json`

## Estado

- Clasificación: `BUILD`
- Página 3: `PASS_STATIC_PREVIEW_PENDING`, 330 checks, 0 errores
- Página 4: `PASS_SOURCE_PREVIEW_PENDING`
- Full project validator después de Página 4: pendiente
- Browser harness de Página 4: pendiente
- Revisión móvil: pendiente
- Certificación visual: pendiente
- Merge a `main`: bloqueado hasta aprobación explícita

## Reglas activas

- Sin `document.write()`.
- Sin `!important`.
- Sin imágenes Base64 activas.
- JavaScript compartido mediante ES Modules.
- CSS de página reservado para composición exclusiva.
- UI como proyección, nunca como fuente de verdad.
- Sin tocar Tablet, PC, Mobile, Chart Lab, Control Center, bases de datos, procesos o puertos.
