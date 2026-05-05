export type Tone = "ok" | "warn" | "danger";

export function getUxProKit() {
  return {
    homeActions: [
      { title: "Caja express", description: "Abre ticket rapido con los atajos que mas se usan en mostrador.", meta: "3 toques", tone: "ok" as Tone },
      { title: "Cobro guiado", description: "Prioriza pago, cambio y alertas de riesgo sin andar cazando botones.", meta: "checkout", tone: "ok" as Tone },
      { title: "Turno blindado", description: "Checklist corto para abrir, pausar y cerrar sin huecos tontos.", meta: "turno", tone: "warn" as Tone },
      { title: "Devolucion segura", description: "Motivos, folio y candados para que la operacion no se vuelva feria.", meta: "returns", tone: "danger" as Tone },
    ],
    operatorLane: [
      { title: "Ticket 1842", description: "Cliente listo para pagar con sustitucion sugerida en pantalla.", signal: "listo", tone: "ok" as Tone },
      { title: "Turno tarde", description: "Falta arqueo intermedio y el efectivo ya paso de umbral.", signal: "revisar", tone: "warn" as Tone },
      { title: "Devolucion R-19", description: "Producto sin barcode claro. Pide validacion antes de cerrar.", signal: "candado", tone: "danger" as Tone },
    ],
    focusBars: [
      { label: "Velocidad de venta", value: 82, note: "checkout express con ahorro medio de 18 segundos.", tone: "ok" as Tone },
      { label: "Claridad operativa", value: 76, note: "menos pasos muertos y menos scroll de safari laboral.", tone: "ok" as Tone },
      { label: "Friccion por excepcion", value: 41, note: "sigue pesada en devoluciones con barcode raro.", tone: "warn" as Tone },
    ],
    salesDeck: {
      queue: [
        { step: "01", title: "Escanear o buscar", description: "Caja abre con favoritos, SKU recientes y resultado mas probable arriba.", tone: "ok" as Tone, aside: "scan" },
        { step: "02", title: "Ajuste rapido", description: "Cambiar cantidad, marcar observacion o suspender sin brincar de pantalla.", tone: "ok" as Tone, aside: "edita" },
        { step: "03", title: "Validar riesgo", description: "Si el stock esta apretado, la venta lo canta sin gritarte con popups locos.", tone: "warn" as Tone, aside: "stock" },
      ],
      favorites: ["Coca 600", "Agua 1L", "Sabritas 45g", "Cafe americano"],
      suggestions: ["Combo cafe + pan", "Sustituir SKU agotado", "Aplicar promo del turno"],
    },
    checkoutRail: {
      payments: [
        { title: "Cobro en efectivo", description: "Cambio visible y monto pendiente siempre a la vista.", meta: "preferido", tone: "ok" as Tone },
        { title: "Tarjeta", description: "Marca si ya fue autorizada o si sigue pendiente de terminal.", meta: "pin-pad", tone: "ok" as Tone },
        { title: "Mixto", description: "Evita cuentas mentales con reparto guiado por metodo.", meta: "2 fuentes", tone: "warn" as Tone },
      ],
      guards: [
        { title: "Stock insuficiente", description: "Candado suave con propuesta de sustitucion o cantidad maxima.", signal: "stock", tone: "warn" as Tone },
        { title: "Sync atrasado", description: "No bloquea la venta, pero si sube la alerta antes del cierre.", signal: "sync", tone: "warn" as Tone },
        { title: "Monto irregular", description: "Pide doble confirmacion cuando la diferencia ya huele raro.", signal: "control", tone: "danger" as Tone },
      ],
    },
    shiftKit: {
      checklist: [
        { step: "A", title: "Abrir turno", description: "Validar caja inicial, red y modo offline antes de cobrar.", tone: "ok" as Tone, aside: "inicio" },
        { step: "B", title: "Punto medio", description: "Revisar efectivo, devoluciones y pendientes de sync.", tone: "warn" as Tone, aside: "corte" },
        { step: "C", title: "Cerrar", description: "Arqueo, eventos pendientes y resumen del turno sin brincarse pasos.", tone: "danger" as Tone, aside: "cierre" },
      ],
      notes: ["Caja inicial confirmada", "Outbox en amarillo", "2 devoluciones con evidencia"],
    },
    returnsKit: {
      reasons: ["ticket duplicado", "producto danado", "cobro incorrecto", "caducidad visible"],
      guardrails: [
        { title: "Folio obligatorio", description: "Sin folio no sale la devolucion completa.", signal: "folio", tone: "danger" as Tone },
        { title: "Motivo clasificado", description: "Elige causa para que auditoria no ande adivinando.", signal: "causa", tone: "ok" as Tone },
        { title: "Evidencia rapida", description: "Nota o foto cuando la devolucion ya pinta sospechosa.", signal: "evidencia", tone: "warn" as Tone },
      ],
    },
  };
}
