> DEPRECATED.
> Reemplazado por docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md.
> Razon: Tablet ya no se define como terminal subordinada a PC.
> Tablet es POS standalone vendible por si solo; PC es backoffice/gobierno.

# PRISMA Twin App Equalization Plan

## Objetivo

Emparejar PC y Tablet sin volverlas clones. PC debe seguir siendo centro de control. Tablet debe seguir siendo herramienta de operación. La igualdad se define por contrato, eventos, lenguaje, QA y reflejo funcional.

## Fase 1: Paridad contractual

**Duración sugerida:** 1 incremento corto.

### Entregables

- `TwinCapabilityManifest` encima del `TwinModuleManifest` actual.
- Matriz de dominios canónicos: `catalog`, `stock`, `sales`, `cash`, `procurement`, `sync`, `audit`.
- Campo `parityKey` para relacionar PC y Tablet.
- Campos mínimos: `surface`, `domain`, `capabilities`, `events`, `offline`, `permissions`, `auditLevel`.

### Resultado esperado

Ya no se pregunta “¿en qué app va esto?”. Se pregunta “¿cuál es su paridad?”. Gran avance civilizatorio, considerando que la humanidad todavía imprime correos.

## Fase 2: Mapa funcional espejo

**Duración sugerida:** 1 incremento corto.

### Entregables

- Documento/JSON `twin-capability-map`.
- Para cada flujo Tablet: ventas, cobro, turno, devoluciones, stock, sync.
- Para cada flujo PC: catálogo, existencias, conteos, compras, recepción, reabasto, auditoría, sync.
- Relación obligatoria: evento -> origen -> destino -> evidencia -> resolución.

### Resultado esperado

Cada cosa que pasa en Tablet tiene dónde verse en PC. Cada regla que se cambia en PC tiene efecto entendible en Tablet.

## Fase 3: UX común sin matar roles

**Duración sugerida:** 1 incremento.

### Entregables

- Tokens compartidos: estados, severidades, badges, cards, tablas, empty states.
- Estados estándar: `ok`, `warning`, `blocked`, `offline`, `pendingSync`, `conflict`.
- Copy común es-MX para errores, vacíos y sync.
- Guía de densidad: PC permite densidad; Tablet privilegia tacto y velocidad.

### Resultado esperado

Las apps se sienten de la misma familia, no como dos locales del mismo dueño donde uno vende café de especialidad y el otro tacos bajo foco rojo.

## Fase 4: QA de paridad

**Duración sugerida:** 1 incremento.

### Entregables

- `twin-parity-acceptance.md` como gate.
- Casos mínimos:
  - Venta creada en Tablet aparece en PC.
  - Devolución creada en Tablet aparece en PC.
  - Turno cerrado en Tablet alimenta caja/reporte PC.
  - Ajuste/catálogo PC impacta Tablet.
  - Conflicto sync se genera en Tablet y se resuelve en PC.

### Resultado esperado

El sistema deja de depender de “se ve bien en mi máquina”, esa frase que debería pagar impuestos por tanto daño histórico.

## Fase 5: Preparación para verticales

**Duración sugerida:** después de paridad base.

### Entregables

- Slots declarados por dominio.
- Plugins solo por contrato.
- Ninguna vertical duplica core.
- Playbook de verticalización por giro.

### Resultado esperado

Abarrotes, farmacia, restaurante, gym o taller pueden entrar sin convertir el core en caldo de cables.

## Backlog recomendado

| Prioridad | Item | Tipo | Dueño sugerido |
|---|---|---|---|
| P0 | Definir `TwinCapabilityManifest` | Contrato | shared/twin-kernel |
| P0 | Crear matriz `twin-capability-map` | Gobierno | docs + shared |
| P0 | QA gate de paridad | QA | docs/prisma/ui/qa |
| P1 | Normalizar copy de sync/offline | UX | PC + Tablet |
| P1 | Estandarizar badges y estados | UI | componentes compartidos futuros |
| P1 | Espejo PC para ventas/caja | Producto | PC app |
| P1 | Recepción rápida Tablet | Producto | Tablet app |
| P2 | Preparar slots de plugins | Plataforma | shared/twin-kernel |

## No metas todavía

- Marketplace de plugins.
- Verticales complejas.
- Fiscal profundo.
- Refactor visual masivo.
- Librería UI compartida si antes no hay contrato de estados.

Primero se empareja el esqueleto. Luego se le pone chamarra fina.
