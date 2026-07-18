import type {ReleaseGateCheck,ReleaseGateSnapshot} from "@/lib/operable-release-gate/release-gate-contract";
const verificationPending="Esta API no ejecuta la validación operativa; requiere evidencia vigente.";
const checks:ReleaseGateCheck[]=[
{id:"sale-flow",surface:"venta",label:"Venta y ticket",description:"La Tablet conserva flujo de venta, cobro, ticket y devolución.",status:"attention",evidence:verificationPending,owner:"Tablet"},
{id:"catalog-stock",surface:"catalogo",label:"Catálogo vende",description:"Catálogo y existencias agregan productos a venta sin abrir pantallas muertas.",status:"attention",evidence:verificationPending,owner:"Tablet"},
{id:"shift-close",surface:"turno",label:"Corte de caja",description:"Turno calcula caja inicial, efectivo esperado, conteo y diferencia.",status:"attention",evidence:verificationPending,owner:"Tablet"},
{id:"pending-panel",surface:"pendientes",label:"Pendientes visibles",description:"El cajero entiende qué falta enviar, qué falló y qué requiere revisión.",status:"attention",evidence:verificationPending,owner:"Tablet"},
{id:"exports",surface:"exportacion",label:"Exportación contextual",description:"Ventas, existencias y pendientes pueden preparar JSON o CSV.",status:"attention",evidence:verificationPending,owner:"Tablet"},
{id:"nav-gate",surface:"navegacion",label:"Rutas críticas",description:"Las rutas principales requieren smoke vigente antes de liberar.",status:"attention",evidence:verificationPending,owner:"QA"},
{id:"copy-gate",surface:"copy",label:"Copy humano",description:"El lenguaje visible requiere revisión vigente antes de liberar.",status:"attention",evidence:verificationPending,owner:"QA"},
{id:"installer-gate",surface:"rollback",label:"Instalador reversible",description:"La entrega requiere comprobar dry-run, apply, verify, rollback, backups y checksums.",status:"attention",evidence:verificationPending,owner:"Instalador"}];
const expectedCaptures=[{id:"capture-pos",route:"/pos",label:"Prisma app / venta",purpose:"Venta operativa con carrito y cobro visible"},{id:"capture-tablet",route:"/catalog",label:"Tablet catálogo-stock",purpose:"Búsqueda, existencia y agregar a venta"},{id:"capture-pc",route:"/release-gate",label:"PC/revisión de release",purpose:"Estado integral y gates de cierre"}];
export function buildReleaseGateSnapshot():ReleaseGateSnapshot{return{packageName:"PRISMA_TABLET_OPERABLE_RELEASE_GATE_03Z",generatedAt:new Date().toISOString(),checks,expectedCaptures}}
