# PRISMA tri-superficie hardening 260611

Este paquete corrige conexiones estáticas y botones/filtros decorativos encontrados en la auditoría `PRISMA_AUDIT_260611`. No mata procesos vivos, no levanta servicios, no corre `pc:typecheck`, no regenera Prisma y no toca bases de datos.

## Mejoras incluidas

1. PC: crear alias /api/backoffice/branches para que Mobile tenga contrato de sucursales/terminales verificable.
2. PC: crear alias /api/backoffice/inventory conectado al módulo real stock.
3. PC: crear alias /api/backoffice/purchases conectado al módulo real purchasing.
4. PC: crear alias /api/backoffice/suppliers conectado a snapshot real de proveedores.
5. PC: crear alias /api/backoffice/reorder conectado al módulo real replenishment.
6. PC: crear /api/proveedores base para que verificadores y consumidores no caigan en 404.
7. Mobile: crear /api/incidents como alias 307 hacia /api/mobile/alerts.
8. Mobile: crear /api/incidents/timeline como alias 307 hacia /api/mobile/pulse-timeline.
9. Mobile: crear /api/reports como alias 307 hacia /api/mobile/reports/daily.
10. Tablet: crear guard /api/backoffice que responde explícitamente que backoffice vive en PC.
11. Tablet POS: botón Vaciar carrito emite prisma:pos-cart-action.
12. Tablet POS: botón Quitar línea emite acción con productId.
13. Tablet POS: botón Restar cantidad emite acción decrement con productId.
14. Tablet POS: botón Sumar cantidad emite acción increment con productId.
15. Tablet POS: botón COBRAR emite acción charge.
16. Tablet POS: botón COTIZACIÓN emite acción quote.
17. Tablet POS: botón GUARDAR emite acción save-ticket.
18. Tablet POS: botón LIMPIAR emite acción clear-current.
19. Tablet POS: categorías emiten prisma:pos-category-action con label activo.
20. Tablet POS: botón Ver más categorías emite acción more.
21. Tablet POS: paginación conserva estado local de página.
22. Tablet POS: flecha anterior de productos ya tiene handler y borde mínimo.
23. Tablet POS: flecha siguiente de productos ya tiene handler y borde máximo.
24. Tablet POS: botones de página exponen aria-current para accesibilidad.
25. Tablet POS: favorito de producto emite prisma:pos-product-action.
26. Tablet POS: búsqueda ahora mantiene query controlado.
27. Tablet POS: Enter en búsqueda emite acción search.
28. Tablet POS: botón ESCANEAR emite acción scan.
29. Tablet POS: botón Más opciones emite acción more-options.
30. Tablet POS: barra superior emite tema, notificaciones y perfil.
31. Tablet Pulse: filtros rápidos ahora tienen estado activo.
32. Tablet Pulse: filtros rápidos actualizan foco local visible.
33. Tablet Pulse: filtros rápidos exponen aria-pressed.
34. PC Liquid Glass: botón de navegación emite evento prisma:glass-action.
35. PC Liquid Glass: acción Editar default ya tiene handler real.
36. PC Liquid Glass: acción Más opciones default ya tiene handler real.
37. PC Liquid Glass: actions sin callback reciben fallback trazable.
38. PC Insights: filtros preview ahora tienen estado por grupo.
39. PC Insights: botones de filtro exponen aria-pressed.
40. PC Insights: Reset limpia filtros y actualiza foco local.
41. Mobile Command: filtros rápidos ahora tienen estado activo.
42. Mobile Command: filtros rápidos actualizan foco owner.
43. Mobile Command: filtros rápidos exponen aria-pressed.
44. Mobile Crystal: ranking de inventario ya selecciona punto activo.
45. Mobile Crystal: ranking de inventario muestra resumen del punto elegido.
46. Mobile Crystal: timeline preview ya selecciona evento activo.
47. Mobile Crystal: timeline preview muestra motivo activo.
48. Bridge: endpoints externos conservan fallback local sin inventar datos.
49. QA: se instala verificador estático tri-superficie sin Prisma generate.
50. Ops: se instala manifiesto de hardening con límites, evidencia y rollback.

## Validación honesta

El paquete instala verificaciones estáticas compatibles con hot-injection. Para cierre runtime se recomienda una fase posterior con servicios ya vivos: HTTP probes, browser/device emulation y comparación DB→API→UI.
