> DEPRECATED.
> Reemplazado por docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md.
> Razon: Tablet ya no se define como terminal subordinada a PC.
> Tablet es POS standalone vendible por si solo; PC es backoffice/gobierno.

# PRISMA Twin App Parity Scorecard

## Resultado ejecutivo

PRISMA tiene una base fuerte para dos apps gemelas, pero todavía necesita convertir la paridad en contrato verificable. La PC ya parece sala de control; la Tablet ya parece herramienta de piso. Lo que falta es el puente formal para que cada acción operativa tenga espejo administrativo.

## Calificación por capa

| Capa | PC | Tablet | Paridad | Nota |
|---|---:|---:|---:|---|
| Estructura Next.js | 8.5 | 8.5 | 8.5 | Ambas tienen App Router, layout, rutas y servicios claros. |
| Navegación por módulos | 8 | 8 | 7 | Ambas usan registry, pero el contrato todavía es básico. |
| Dominio operativo | 8.5 | 8 | 7.5 | PC domina control; Tablet domina ejecución. Falta matriz espejo. |
| Datos / Prisma | 9 | 9 | 9 | Canonical PASS y stubs locales bien marcados como transicionales. |
| Sync / outbox | 8 | 8 | 8 | Hay eventos compartidos y repositorios en ambas. Falta vista contractual por evento. |
| UI / lenguaje visual | 7.5 | 7.5 | 6.8 | Hay componentes comunes por app, pero no biblioteca compartida real. |
| QA / gates | 8 | 8.5 | 7 | Tablet trae mucha evidencia QA; falta gate conjunto PC <-> Tablet. |
| Preparación para plugins | 8 | 7 | 7 | La documentación es fuerte; runtime todavía debe declarar slots/capabilities. |

## Lectura rápida

**Promedio estimado:** 7.9 / 10.

No está verde tierno. Está como obra negra bien trazada: ya tiene castillos, niveles y varilla. Falta aplanar, alinear instalaciones y evitar que cada maestro llegue con su propia idea de dónde va el baño.

## Scorecard de emparejamiento por dominio

| Dominio | Estado | Acción recomendada |
|---|---|---|
| `catalog` | PC fuerte, Tablet consumo implícito | Agregar contrato de consulta/escaneo/incidencia en Tablet. |
| `stock` | Ambas tienen superficie | Unificar nombres: PC `Existencias`, Tablet `Stock operativo`, mismo dominio `stock`. |
| `sales` | Tablet fuerte, PC sin módulo explícito de supervisión | Crear espejo PC de ventas/resumen/cortes, aunque sea documento inicial. |
| `cash` | Tablet `shift`, PC caja implícita en docs | Formalizar dominio `cash` y su espejo PC. |
| `procurement` | PC fuerte, Tablet sin recepción ligera visible | Diseñar recepción rápida Tablet como complemento, no reemplazo. |
| `sync` | Ambas tienen ruta | Convertir eventos compartidos en tablero de trazabilidad por origen. |
| `audit` | PC fuerte, Tablet evidencia dispersa | Toda acción sensible en Tablet debe declararse auditable en PC. |

## Semáforo

| Color | Significado | Hallazgo |
|---|---|---|
| Verde | Base útil | Prisma canónico, rutas principales, registry modular, docs de gobierno. |
| Amarillo | Riesgo controlable | Contrato compartido débil para capacidades, UI duplicada por app, QA de paridad no obligatorio. |
| Rojo | No hacer todavía | Copiar todas las pantallas PC a Tablet o meter verticales antes del contrato espejo. |

## Criterios mínimos para declarar las apps emparejadas

1. Cada módulo tiene `domain`, `surface`, `parityKey` y `events`.
2. Cada evento operativo de Tablet aparece en una vista, reporte o auditoría PC.
3. Cada acción PC que cambia reglas tiene consecuencia visible o bloqueante en Tablet.
4. Cada flujo sensible define permisos, offline, sync y rollback.
5. La revisión de PR incluye matriz de paridad.

## Veredicto

Van bien. No están listas para crecer a lo loco, pero sí están listas para una fase de emparejamiento serio. La siguiente jugada no debe ser meter más pantallas como quien mete sillas a una fiesta; debe ser crear el contrato común que permita que ambas apps crezcan sin hacerse bolas.
