# PRISMA Visual QA Two Skins Checklist

**Propósito:** validar que Dark POS y Light POS funcionen como dos skins del mismo sistema, no como dos pantallas peleadas.

---

## 1. Capturas obligatorias

Para cada skin:

```text
Dark POS full screen
Light POS full screen
Dark POS product card close-up
Light POS product card close-up
Dark POS cart close-up
Light POS cart close-up
Dark POS selector open
Light POS selector open
```

---

## 2. Comparación de esqueleto

Ambos skins deben mantener:

- [ ] 4:3 landscape.
- [ ] Sidebar izquierda.
- [ ] Main sales area.
- [ ] Cart derecho.
- [ ] Top controls.
- [ ] Search row.
- [ ] Category rail.
- [ ] ProductGrid 4x2.
- [ ] Pagination.
- [ ] `COBRAR` dominante.

Si cambia el esqueleto, no es skin: es otro diseño disfrazado.

---

## 3. Dark POS debe cumplir

- [ ] background deep/dark atmosférico;
- [ ] panels dark glass;
- [ ] active `Ventas` en gold;
- [ ] active `Todos` en gold;
- [ ] total en gold;
- [ ] `COBRAR` gold;
- [ ] product cards dark glass;
- [ ] glows visibles;
- [ ] no neon gamer;
- [ ] no dashboard genérico.

---

## 4. Light POS debe cumplir

- [ ] background white/frosted con profundidad;
- [ ] panels frosted white;
- [ ] active `Ventas` en blue;
- [ ] active `Todos` en blue;
- [ ] total en blue;
- [ ] `COBRAR` blue;
- [ ] product cards light/frosted;
- [ ] sombras suaves;
- [ ] no fintech genérico;
- [ ] no blanco plano.

---

## 5. Componentes críticos

Validar en ambos skins:

| Componente | Criterio |
|---|---|
| Sidebar | mismo contenido, distinto material |
| Nav active | dark=gold, light=blue |
| Search | misma posición, material por skin |
| ScanButton | mismo tamaño, acento por skin |
| CategoryRail | circular, activo por skin |
| ProductCard | mismo tamaño, material por skin |
| CartPanel | mismo ancho, material por skin |
| TotalsSummary | total grande, acento por skin |
| PayButton | dominante, acento por skin |
| SecondaryActionCard | visible, shortcuts correctos |

---

## 6. Texto visible

Debe seguir en es-MX:

- [ ] `Ventas`
- [ ] `Buscar producto por código, nombre o SKU...`
- [ ] `ESCANEAR`
- [ ] `Carrito de venta`
- [ ] `4 artículos`
- [ ] `Subtotal`
- [ ] `Impuestos (IVA 16%)`
- [ ] `Total`
- [ ] `COBRAR`
- [ ] `COTIZACIÓN`
- [ ] `GUARDAR`
- [ ] `LIMPIAR`
- [ ] `Terminal 01`
- [ ] `En línea`

---

## 7. Rechazo automático

Rechazar si:

- [ ] el botón `COBRAR` es verde;
- [ ] ProductGrid se volvió tabla;
- [ ] cart no está fijo a la derecha;
- [ ] productos son miniaturas;
- [ ] desaparece stock;
- [ ] se pierden shortcuts;
- [ ] aparece copy en inglés;
- [ ] light parece dashboard fintech;
- [ ] dark parece cyberpunk;
- [ ] el selector mueve layout.

---

## 8. Resultado esperado

Estado final de QA:

```text
READY
READY_WITH_CAVEATS
BLOCKED
```

Usar `READY_WITH_CAVEATS` si el skin funciona pero falta pulir fidelidad visual fina.

Usar `BLOCKED` si se rompe layout, flujo POS, tokens o selector.
