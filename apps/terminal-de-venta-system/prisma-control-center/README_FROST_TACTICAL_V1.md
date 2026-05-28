# PRISMA Control Center · Tactical Frost V1

Cambio visual sin dependencias externas.

## Qué cambia

- Reemplaza el lugar del tema `Tactical` por `Tactical Frost`.
- Usa `internal/web/assets/simon-spring-zmMrlEHsFQY-unsplash.jpg` como background local.
- Agrega `internal/web/prisma_frost_tactical.css` y `internal/web/prisma_frost_tactical.js`.
- Mantiene endpoints, Python, wrappers, configuración y lógica operativa intactos.
- Primer arranque limpio apunta a Tactical Frost; si el navegador ya tenía otro tema guardado, usa `Ctrl+2` o el selector de tema.

## Archivos añadidos

- `internal/web/assets/simon-spring-zmMrlEHsFQY-unsplash.jpg`
- `internal/web/prisma_frost_tactical.css`
- `internal/web/prisma_frost_tactical.js`
- `internal/tools/verify_frost_tactical.py`

## Pruebas incluidas

- Verificación de asset local.
- Verificación de links CSS/JS en `index.html`.
- Revisión de que no haya URLs externas nuevas.
- Compilación Python.
- Smoke del panel 3150.

## Uso

Abrir Control Center y seleccionar `Tactical Frost` o presionar `Ctrl+2`.
