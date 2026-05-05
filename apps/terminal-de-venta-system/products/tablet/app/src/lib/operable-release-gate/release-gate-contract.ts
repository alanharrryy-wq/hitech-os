export type ReleaseGateStatus="ready"|"attention"|"blocked";
export type ReleaseGateSurface="venta"|"catalogo"|"turno"|"pendientes"|"exportacion"|"navegacion"|"copy"|"rollback";
export type ReleaseGateCheck={id:string;surface:ReleaseGateSurface;label:string;description:string;status:ReleaseGateStatus;evidence:string;owner:"Tablet"|"Instalador"|"QA"};
export type ReleaseGateSnapshot={packageName:"PRISMA_TABLET_OPERABLE_RELEASE_GATE_03Z";generatedAt:string;checks:ReleaseGateCheck[];expectedCaptures:Array<{id:string;route:string;label:string;purpose:string}>};
export const RELEASE_GATE_PACKAGE="PRISMA_TABLET_OPERABLE_RELEASE_GATE_03Z" as const;
export const RELEASE_GATE_SURFACE_LABELS:Record<ReleaseGateSurface,string>={venta:"Venta y devolución",catalogo:"Catálogo y existencias",turno:"Turno y caja",pendientes:"Pendientes y conexión",exportacion:"Exportación local",navegacion:"Navegación",copy:"Lenguaje operativo",rollback:"Instalación reversible"};
export const RELEASE_GATE_READY_COPY={ready:"Listo",attention:"Revisar",blocked:"Bloqueado"} satisfies Record<ReleaseGateStatus,string>;
