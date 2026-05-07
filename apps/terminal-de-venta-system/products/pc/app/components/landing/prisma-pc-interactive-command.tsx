"use client";

import { useMemo, useState } from "react";

const modes = [
  { id: "dueno", label: "Dueño", eyebrow: "Vista ejecutiva", headline: "Qué pasó, dónde dolió y qué urge mover.", focus: "Prioriza ventas, caja, stock crítico y sucursales con fuga de control." },
  { id: "gerente", label: "Gerente", eyebrow: "Vista operativa", headline: "Qué equipo necesita acción antes del corte.", focus: "Cruza pedidos, recepción, conteos y ajustes para operar sin andar persiguiendo papelitos." },
  { id: "auditor", label: "Auditoría", eyebrow: "Vista de control", headline: "Quién tocó inventario, caja o precios sensibles.", focus: "Enfoca movimientos delicados, diferencias y eventos pendientes de conciliación." }
] as const;

type ModeId = (typeof modes)[number]["id"];
type ModuleId = "dashboard" | "inventario" | "compras" | "auditoria" | "sync";
const scopes = ["Todas las tiendas", "Centro", "Norte", "Mostrador 2"];

const modules: Array<{ id: ModuleId; label: string; title: string; metric: string; signal: string; health: number; actions: string[]; }> = [
  { id: "dashboard", label: "Dashboard", title: "Pulso general del negocio", metric: "$128,430 venta neta", signal: "4 alertas que sí merecen café fuerte", health: 82, actions: ["Ver ventas", "Comparar sucursales", "Revisar margen"] },
  { id: "inventario", label: "Inventario", title: "Existencias, quiebres y sobreinventario", metric: "18 SKUs críticos", signal: "3 productos se agotan antes del viernes", health: 68, actions: ["Filtrar quiebres", "Ver sobreinventario", "Abrir conteos"] },
  { id: "compras", label: "Compras", title: "Pedido sugerido y recepción", metric: "7 órdenes pendientes", signal: "2 recepciones traen diferencia contra pedido", health: 74, actions: ["Simular pedido", "Ver proveedores", "Confirmar recepción"] },
  { id: "auditoria", label: "Auditoría", title: "Movimientos sensibles", metric: "11 ajustes revisables", signal: "Un usuario concentró 5 cambios de precio", health: 59, actions: ["Rastrear ajustes", "Ver bitácora", "Bloquear revisión"] },
  { id: "sync", label: "Sincronización", title: "Eventos Tablet y conciliación", metric: "42 eventos recibidos", signal: "2 conflictos esperando criterio de PC", health: 77, actions: ["Ingestar eventos", "Resolver conflictos", "Ver outbox"] }
];

const moduleRoutes: Record<ModuleId, string> = {
  dashboard: "/dashboard",
  inventario: "/stock",
  compras: "/purchasing",
  auditoria: "/audit",
  sync: "/sync"
};

const actionRoutes: Record<string, string> = {
  "Ver ventas": "/metricas-dia",
  "Comparar sucursales": "/vistas-ejecutivas",
  "Revisar margen": "/tablero-kpi",
  "Filtrar quiebres": "/existencias-criticas",
  "Ver sobreinventario": "/stock",
  "Abrir conteos": "/counts",
  "Simular pedido": "/replenishment",
  "Ver proveedores": "/proveedores",
  "Confirmar recepción": "/receiving",
  "Rastrear ajustes": "/ajustes-inventario",
  "Ver bitácora": "/audit",
  "Bloquear revisión": "/alertas-operativas",
  "Ingestar eventos": "/sync",
  "Resolver conflictos": "/sync-operativo",
  "Ver outbox": "/outbox-operativo",
  "Abrir Inventario": "/existencias-criticas",
  "Abrir Compras": "/replenishment",
  "Abrir Auditoría": "/audit",
  "Abrir Sincronización": "/sync-operativo",
  "Abrir Catálogo": "/salud-barcodes"
};

const incidents = [
  { severity: "Alta", area: "Inventario", branch: "Centro", text: "Refresco 600ml llegó a quiebre y siguió vendiéndose en mostrador.", owner: "Caja 1" },
  { severity: "Media", area: "Compras", branch: "Norte", text: "Pedido sugerido supera cobertura máxima en botanas.", owner: "Gerencia" },
  { severity: "Alta", area: "Auditoría", branch: "Mostrador 2", text: "Ajuste manual de precio fuera de política aprobada.", owner: "Supervisor" },
  { severity: "Media", area: "Sincronización", branch: "Centro", text: "Tablet reportó dos eventos pendientes de conciliación.", owner: "Backoffice" },
  { severity: "Baja", area: "Catálogo", branch: "Todas", text: "5 SKUs activos no tienen código de barras completo.", owner: "Catálogo" }
];

export function PrismaPcInteractiveCommand() {
  const [modeId, setModeId] = useState<ModeId>("dueno");
  const [scope, setScope] = useState(scopes[0]);
  const [activeModuleId, setActiveModuleId] = useState<ModuleId>("dashboard");
  const [query, setQuery] = useState("");
  const [actionLog, setActionLog] = useState("Listo para revisar operación.");
  const selectedMode = modes.find((mode) => mode.id === modeId) ?? modes[0];
  const activeModule = modules.find((moduleItem) => moduleItem.id === activeModuleId) ?? modules[0];
  const filteredIncidents = useMemo(() => {
    const q = query.trim().toLowerCase();
    return incidents.filter((i) => (scope === "Todas las tiendas" || i.branch === scope || i.branch === "Todas") && (q.length === 0 || `${i.severity} ${i.area} ${i.branch} ${i.text} ${i.owner}`.toLowerCase().includes(q)));
  }, [query, scope]);
  function runAction(label: string) {
    const href = actionRoutes[label] ?? moduleRoutes[activeModuleId] ?? "/dashboard";
    setActionLog(`${label}: abriendo ${href} para ${scope}.`);
    window.location.href = href;
  }
  return (
    <section className="prisma-command-center" id="control-en-vivo" aria-labelledby="prisma-command-title">
      <div className="prisma-command-heading"><span className="prisma-home-kicker">Control interactivo PC</span><h2 id="prisma-command-title">Ahora sí: toca, filtra, compara y dispara acciones.</h2><p>Este bloque convierte la PC en cabina de mando: no solo enseña tarjetas bonitas, también deja jugar con rol, sucursal, módulo, búsqueda y acciones operativas.</p></div>
      <div className="prisma-command-tabs" role="tablist" aria-label="Cambiar vista de trabajo">{modes.map((m) => <button type="button" role="tab" aria-selected={m.id === modeId} className={m.id === modeId ? "is-active" : ""} key={m.id} onClick={() => setModeId(m.id)}>{m.label}</button>)}</div>
      <div className="prisma-command-hero" role="tabpanel" aria-label={`Vista ${selectedMode.label}`}><div><span>{selectedMode.eyebrow}</span><h3>{selectedMode.headline}</h3><p>{selectedMode.focus}</p></div><label className="prisma-command-select"><span>Sucursal</span><select value={scope} onChange={(event) => setScope(event.target.value)}>{scopes.map((s) => <option key={s}>{s}</option>)}</select></label></div>
      <div className="prisma-command-kpis" aria-label="Indicadores rápidos"><article><span>Ventas netas</span><strong>$128,430</strong><small>+12% contra ayer</small></article><article><span>Quiebres</span><strong>18</strong><small>3 urgentes</small></article><article><span>Recepción</span><strong>92%</strong><small>fill rate estimado</small></article><article><span>Sync</span><strong>2</strong><small>conflictos</small></article></div>
      <div className="prisma-command-workspace"><nav className="prisma-command-module-rail" aria-label="Módulos de backoffice">{modules.map((m) => <button type="button" key={m.id} className={m.id === activeModuleId ? "is-active" : ""} aria-current={m.id === activeModuleId ? "page" : undefined} onClick={() => setActiveModuleId(m.id)}><span>{m.label}</span><b>{m.metric}</b></button>)}</nav><article className="prisma-command-module-panel"><span className="prisma-command-panel-kicker">Módulo activo</span><h3>{activeModule.title}</h3><p>{activeModule.signal}</p><div className="prisma-command-meter" aria-label={`Salud operativa ${activeModule.health}%`}><span style={{ width: `${activeModule.health}%` }} /></div><div className="prisma-command-route-row"><a href={moduleRoutes[activeModule.id]}>Abrir {activeModule.label}</a><small>Ruta real conectada, no boton de utileria.</small></div><div className="prisma-command-actions" aria-label="Acciones rápidas">{activeModule.actions.map((a) => <button type="button" data-prisma-route="true" key={a} onClick={() => runAction(a)}>{a}</button>)}</div></article><aside className="prisma-command-incidents" aria-labelledby="prisma-command-incidents-title"><div className="prisma-command-search-row"><div><span className="prisma-command-panel-kicker">Alertas filtrables</span><h3 id="prisma-command-incidents-title">Incidentes vivos</h3></div><label><span>Buscar</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="stock, sync, auditoría..." aria-label="Buscar incidentes" /></label></div><div className="prisma-command-incident-list" aria-live="polite">{filteredIncidents.length === 0 ? <div className="prisma-command-empty">Sin coincidencias. Milagro: el changarro respiró tres segundos.</div> : filteredIncidents.map((i) => <button type="button" data-prisma-route="true" key={`${i.area}-${i.branch}-${i.text}`} className={`severity-${i.severity.toLowerCase()}`} onClick={() => runAction(`Abrir ${i.area}`)}><span>{i.severity}</span><b>{i.area} · {i.branch}</b><small>{i.text}</small></button>)}</div></aside></div>
      <div className="prisma-command-live" data-prisma-nav-ready="true" aria-live="polite"><strong>Última acción:</strong> {actionLog}</div>
    </section>
  );
}
