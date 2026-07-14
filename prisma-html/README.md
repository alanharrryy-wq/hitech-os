# PRISMA HTML · Baseline limpio para GitHub

Baseline funcional extraído de `prismaui clean1 1307 1943`.

Este paquete conserva únicamente el proyecto activo necesario para renderizar, desarrollar y validar:

- portada PRISMA;
- deck de inversionistas;
- catálogo del sistema UI;
- tokens, temas, layouts, componentes y patrones compartidos;
- módulos JavaScript ES;
- logo oficial;
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
- No contiene backups.
- No contiene capturas, comparaciones visuales ni históricos.
- No contiene wrappers de instalación ni rollback del ZIP original.
- No reemplaza la rama-stash donde se conserva Página 3.

## Reglas activas

- Sin `document.write()`.
- Sin `!important`.
- Sin imágenes Base64 activas.
- JavaScript compartido mediante ES Modules.
- CSS de página reservado para composición exclusiva.
