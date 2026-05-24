# PC UI/UX Simplification Debt

Generated: 2026-05-23T21:46:27  
Run ID: 20260523_214627

Este archivo documenta deuda UI/UX consciente después de instalar la capa de gobierno PC.

## Estado

La capa estructural ya existe:

- `products/pc/app/src/uiux/page-contracts.ts`
- `products/pc/app/src/uiux/route-map.ts`
- `products/pc/app/src/uiux/copy-dictionary.ts`
- `products/pc/app/src/uiux/status-translator.ts`
- `products/pc/app/src/uiux/pc-uiux-baseline.json`

## Deuda cerrada en este micro-parche

Se tradujo jerga visible detectada por `verify_pc_uiux_no_jargon.mjs`:

| Técnico | Usuario |
|---|---|
| adapter | conector |
| Adapter | Conector |
| Adapter: | Conector: |
| canonical | base principal |
| PC canonical | base principal de PC |
| TRI-DB | sincronización entre equipos |
| ingest | recepción de cambios |

## Deuda pendiente: tablas

`verify_pc_uiux_table_contract.mjs` puede seguir marcando deuda advisory en tablas que aún no expresan claramente:

```txt
Elemento
Estado
Qué pasa
Acción
```

### Rutas/componentes conocidos del diagnóstico previo

| Área | Problema | Riesgo | Plan | Prioridad |
|---|---|---|---|---|
| detalle-registros | Tabla demasiado técnica | Usuario ve registros sin decisión | Convertir a tabla accionable o mover técnica a evidencia | Media |
| exportables | Falta columna de acción clara | Descarga confusa | Normalizar con “Reporte / Para qué sirve / Formato / Descargar” | Alta |
| tablas-operativas | Puede parecer referencia técnica | Confusión usuario final | Marcar como interna o convertir a guía humana | Media |
| vistas-ejecutivas | KPI/tabla sin acción explícita | Dashboard bonito pero pasivo | Agregar lectura rápida y acción sugerida | Alta |
| data-table | Componente base no fuerza acción/estado | Reintroduce tablas mudas | Crear `ActionableTable` o props obligatorias | Alta |
| module-overview-page | Overview sin acción suficiente | Pantallas resumen sin decisión | Agregar `NextBestAction` | Alta |
| i11-table | Tabla especializada sin contrato humano | Deuda de consistencia | Revisar en parche de tablas | Media |
| ops-table | Tabla operativa debe exigir estado/acción | Riesgo sistémico | Evolucionar a contrato `ActionableTable` | Alta |
| table-simple | Tabla simple sin semántica | Puede colarse en UI final | Limitar a docs/interno o envolver | Media |

## Regla para siguientes parches

No tocar UI real sin correr:

```txt
node tools/run_verify_pc_uiux_minimum.mjs
```

Y revisar:

```txt
F:\descargasf\prisma_pc_uiux_*.log
```

## Siguiente parche recomendado

Aplicar el patrón visual/humano a módulos piloto:

1. Inventario
2. Proveedores
3. Sincronización

No hacer todo de golpe. Primero que el patrón quede perro fino, luego se replica.
