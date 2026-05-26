# PRISMA PC UIUX Simplification Debt

**Release baseline:** V02 Route Adoption Gate
**Fecha:** 2026-05-25

## Resuelto por V01

- Baseline ANSI instalado en `src/uiux`.
- Navegación principal humana.
- Componentes base de decisión.
- Verificador inicial sin fake green.

## Resuelto por V02

- `DecisionScreen` adoptado en `/dashboard`.
- Contratos humanos generados para todas las rutas PC con `page.tsx`.
- `AppShell` resuelve título, pregunta, subtítulo y acción desde el route-map/contract.
- `EvidenceDrawer` real por contrato, cerrado por defecto.
- Subnavegación estándar por módulo.
- Mapa de reubicación para rutas técnicas.
- Verificador de cobertura de rutas, navegación humana, evidencia y adopción.
- Reportes CSV/MD/JSON dentro del ZIP de resultado.

## Pendiente para V03

- Playwright y capturas 1920x1080.
- Verificación visual de overflow, alturas, scroll y jerarquía.
- Adopción profunda de `DecisionScreen` en todas las páginas principales.
- Medición de uso real de dependencias visuales por interfaz.
- Presupuestos visuales Cloudglass por pantalla.

## Regla vigente

Lo técnico no se elimina; se traduce, se reubica y vive bajo evidencia o bajo Sistema/Sincronización/Inventario según corresponda.
