export const tabletMessages = {
  metadata: {
    title: "Terminal de venta 6.1.1",
    description: "Base operativa con ventas, cobro, turno, devoluciones, existencias operativas, sincronización visible, tablero KPI, seguridad operativa y capa touch-first."
  },
  productName: "Terminal de venta",
  shell: {
    brand: "Terminal de venta",
    subtitle: "Ventas, cobro, turno, devoluciones, existencias, sincronización, tablero KPI y operación touch-first.",
    footer: "Gemela: panel administrativo de inventario. Dominio: terminal de venta.",
    home: "Inicio"
  },
  home: {
    kicker: "tablero operativo",
    title: "Terminal de venta",
    subtitle: "Ahora con lectura KPI, seguridad operativa y una capa experiencia operativa para que el flujo diario no se sienta como pelea con impresora vieja."
  },
  pages: {
    sales: {
      kicker: "modulo vivo",
      title: "Ventas",
      subtitle: "Venta rapida con favoritos, carril de acciones y senales suaves para no matar velocidad.",
      bullets: ["ventas netas del dia", "numero de tickets", "ticket promedio", "unidades por ticket"]
    },
    checkout: {
      kicker: "cobro guiado",
      title: "Cobro",
      subtitle: "Rail de pago, alertas operativas y cierre express sin calculadora mental clandestina.",
      bullets: ["metodos de pago", "cambio", "candados operativos", "confirmacion final"]
    },
    returns: {
      kicker: "devolucion segura",
      title: "Devoluciones",
      subtitle: "Motivos, folio y evidencia rapida para que el retorno quede trazable y no en modo loteria.",
      bullets: ["folio", "motivo", "evidencia", "resolucion"]
    },
    shift: {
      kicker: "turno vivo",
      title: "Turno",
      subtitle: "Checklist corto, arqueo visible y notas del turno para que la jornada no se vaya chueca.",
      bullets: ["apertura", "corte intermedio", "arqueo", "cierre"]
    },
    existencias: {
      kicker: "senal operativa",
      title: "Existencias",
      subtitle: "Existencias ligeras, quiebres y reabasto express para no vender humo con ticket bonito.",
      quickActions: [
        { kicker: "atajo", title: "Buscar SKU critico", description: "Abrir consulta rapida por barcode, SKU o nombre." },
        { kicker: "atajo", title: "Pedir reabasto", description: "Levantar senal corta al area de apoyo sin salir del flujo." },
        { kicker: "atajo", title: "Marcar precio dudoso", description: "Escalar diferencia de anaquel contra caja." },
        { kicker: "atajo", title: "Bloquear venta asistida", description: "Poner candado temporal cuando el riesgo ya esta cantado." }
      ]
    },
    sincronización: {
      kicker: "motor offline",
      title: "Sincronización",
      subtitle: "Pendientes visibles, reintentos, conflictos y latencia para que operar sin red no sea caja negra.",
      bullets: ["pendientes por enviar", "reintentos", "conflictos", "confirmacion"],
      quickActions: [
        { kicker: "atajo", title: "Forzar reintento", description: "Disparar lote corto cuando regresa la red." },
        { kicker: "atajo", title: "Ver conflictos", description: "Abrir la lista de movimientos atorados o incompatibles." },
        { kicker: "atajo", title: "Congelar cierre", description: "Bloquear corte hasta que el pendientes baje de nivel rojo." },
        { kicker: "atajo", title: "Exportar bitacora", description: "Sacar foto operativa para supervisor o soporte." }
      ]
    }
  },
  statuses: {
    pending: "pendiente",
    sent: "enviado",
    failed: "fallido"
  }
} as const;
