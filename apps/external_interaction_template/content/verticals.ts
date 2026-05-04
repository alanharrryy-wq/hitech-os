export type Vertical = {
  slug: "commerce" | "industrial" | "field" | "control";
  name: string;
  headline: string;
  promise: string;
  image: string;
  audience: string;
  flow: string[];
  surfaces: { tablet: string; pc: string; mobile: string; core: string; control: string };
  proof: string[];
};

export const verticals: Vertical[] = [
  {
    slug: "commerce",
    name: "Commerce",
    headline: "Venta, caja e inventario sin libreta milagrosa.",
    promise: "Para negocios que venden todos los días y necesitan saber qué pasó con cada venta, cada corte y cada movimiento.",
    image: "/prisma/marketing/prisma-commerce.jpg",
    audience: "Restaurantes, tiendas, ferreterías, cafeterías, boutiques, salones y gimnasios.",
    flow: ["Venta", "Pago", "Ticket", "Caja", "Corte", "Alerta", "Reporte"],
    surfaces: {
      tablet: "Vende, cobra, imprime o genera ticket y opera el turno.",
      pc: "Administra productos, precios, usuarios, caja, inventario y reportes.",
      mobile: "Muestra ventas del día, caja, inventario bajo y descuadres.",
      core: "Registra ventas, pagos, movimientos, cortes, estados y evidencias.",
      control: "Audita cierres, anomalías, responsables e historial."
    },
    proof: ["Ticket generado", "Corte de caja", "Movimiento de inventario", "Reporte diario"]
  },
  {
    slug: "industrial",
    name: "Industrial",
    headline: "Activos, lecturas y mantenimiento con evidencia.",
    promise: "Para operaciones técnicas que necesitan controlar equipos, bitácoras, responsables, rangos y alertas.",
    image: "/prisma/marketing/prisma-industrial.jpg",
    audience: "Talleres, mantenimiento, rectificadores CRS, activos técnicos y operación industrial ligera.",
    flow: ["Activo", "Lectura", "Evidencia", "Estado", "Alerta", "Orden", "Reporte"],
    surfaces: {
      tablet: "Captura lecturas, checklist, fotos y observaciones desde operación.",
      pc: "Gobierna activos, planes, reglas, rangos, responsables e historial.",
      mobile: "Avisa fallas, lecturas fuera de rango y mantenimientos vencidos.",
      core: "Registra activos, eventos técnicos, evidencias, estados y alertas.",
      control: "Audita historial técnico, cumplimiento y riesgo operativo."
    },
    proof: ["Ficha de activo", "Lectura técnica", "Foto de evidencia", "Alerta por rango"]
  },
  {
    slug: "field",
    name: "Field",
    headline: "Órdenes de trabajo que sí regresan con prueba.",
    promise: "Para equipos que salen a campo y necesitan checklist, fotos, firmas, estado y sincronización.",
    image: "/prisma/marketing/prisma-field.jpg",
    audience: "Técnicos, instaladores, supervisores, cuadrillas y servicios en sitio.",
    flow: ["Orden", "Asignación", "Checklist", "Evidencia", "Firma", "Cierre", "Reporte"],
    surfaces: {
      tablet: "Ejecuta orden, completa checklist, captura fotos y cierra trabajo.",
      pc: "Planea rutas, asignaciones, calendarios, responsables y reportes.",
      mobile: "Supervisa avance, retrasos, bloqueos y evidencias pendientes.",
      core: "Registra órdenes, estados, evidencias, firmas, responsables y tiempos.",
      control: "Audita cumplimiento, SLA, pendientes y productividad."
    },
    proof: ["Orden asignada", "Checklist completo", "Firma capturada", "Reporte de cumplimiento"]
  },
  {
    slug: "control",
    name: "Control",
    headline: "Centro de mando para dejar de perseguir capturas.",
    promise: "Para dueños y supervisores que necesitan alertas, reportes y auditoría sin pedir veinte mensajes por WhatsApp.",
    image: "/prisma/marketing/prisma-control.jpg",
    audience: "Dueños, gerentes, administradores y supervisores multioperación.",
    flow: ["Evento", "Agregado", "Alerta", "Decisión", "Responsable", "Seguimiento", "Auditoría"],
    surfaces: {
      tablet: "Alimenta eventos reales desde piso u operación.",
      pc: "Analiza dashboards, reportes, reglas, roles e historial.",
      mobile: "Avisa anomalías críticas y resume el día.",
      core: "Normaliza eventos, estados, alertas, responsables y reportes.",
      control: "Consolida visión ejecutiva y trazabilidad."
    },
    proof: ["Resumen diario", "Alertas críticas", "Responsable visible", "Auditoría de cambios"]
  }
];

export function getVertical(slug: string) {
  return verticals.find((vertical) => vertical.slug === slug);
}
