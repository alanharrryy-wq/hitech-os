// PRISMA_PRICING_OWNER_V1
"use client";

import { type FormEvent, useMemo, useState } from "react";

type Row = Record<string, unknown>;
type Workspace = {
  businessId: string;
  mutationReady: boolean;
  warnings: string[];
  products: Array<{ id: string; sku: string; name: string; priceCents: number; isActive: boolean }>;
  priceLists: Row[];
  priceListItems: Row[];
  taxRates: Row[];
  promotions: Row[];
  discounts: Row[];
  authorizationRules: Row[];
  authorizationRequests: Row[];
  generatedAt: string;
};

function text(row: Row, key: string, fallback = "") {
  const value = row[key];
  return value === null || value === undefined ? fallback : String(value);
}

function number(row: Row, key: string) {
  const value = Number(row[key]);
  return Number.isFinite(value) ? value : 0;
}

function bool(row: Row, key: string) {
  return row[key] === true || row[key] === 1 || row[key] === "1";
}

function dateInput() {
  return new Date().toISOString().slice(0, 16);
}

function idempotencyKey(prefix: string) {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") return `${prefix}:${crypto.randomUUID()}`;
  return `${prefix}:${Date.now()}:${Math.random().toString(36).slice(2, 14)}`;
}

async function readApi<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible completar la operación.");
  return body.data;
}

function formObject(event: FormEvent<HTMLFormElement>) {
  const data = new FormData(event.currentTarget);
  return Object.fromEntries(Array.from(data.entries()).map(([key, value]) => [key, typeof value === "string" ? value : value.name]));
}

function Section({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section className="card">
      <div className="section-head">
        <div>
          <div className="kicker">pricing owner</div>
          <h2 className="section-title">{title}</h2>
          <div className="section-copy">{subtitle}</div>
        </div>
      </div>
      {children}
    </section>
  );
}

export function PricingPolicyWorkspace({ initialWorkspace }: { initialWorkspace: Workspace }) {
  const [workspace, setWorkspace] = useState(initialWorkspace);
  const [status, setStatus] = useState(initialWorkspace.warnings[0] ?? "");
  const [pending, setPending] = useState<string | null>(null);

  const summary = useMemo(() => ({
    priceLists: workspace.priceLists.length,
    taxes: workspace.taxRates.length,
    promotions: workspace.promotions.length,
    discounts: workspace.discounts.length,
    pendingAuthorizations: workspace.authorizationRequests.filter((row) => text(row, "status").toUpperCase() === "PENDING").length
  }), [workspace]);

  async function reload() {
    const data = await readApi<{ workspace: Workspace }>(await fetch("/api/backoffice/pricing/workspace", { cache: "no-store" }));
    setWorkspace(data.workspace);
  }

  async function create(entity: string, payload: Record<string, unknown>, form?: HTMLFormElement) {
    setPending(entity);
    setStatus("");
    try {
      const data = await readApi<{ record: Row; replayed: boolean }>(await fetch(`/api/backoffice/pricing/${entity}`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ ...payload, idempotencyKey: idempotencyKey(`pricing:${entity}`) })
      }));
      await reload();
      form?.reset();
      setStatus(data.replayed ? "La solicitud ya existía; se recuperó el owner canónico." : "Cambio guardado, auditado y releído desde Pricing canónico.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible guardar.");
    } finally {
      setPending(null);
    }
  }

  async function patch(entity: string, row: Row, change: Record<string, unknown>) {
    const id = text(row, "id");
    setPending(`${entity}:${id}`);
    setStatus("");
    try {
      await readApi<{ record: Row }>(await fetch(`/api/backoffice/pricing/${entity}/${encodeURIComponent(id)}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ expectedVersion: number(row, "version"), ...change })
      }));
      await reload();
      setStatus("Cambio confirmado mediante read-after-write.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible actualizar.");
    } finally {
      setPending(null);
    }
  }

  const blocked = !workspace.mutationReady;

  return (
    <div className="grid">
      {status ? <div className="alert-strip" role="status" aria-live="polite"><strong>Pricing</strong><span className="subtle">{status}</span></div> : null}

      <section className="dashboard-grid">
        <article className="card metric-card"><div className="kicker">listas</div><div className="metric">{summary.priceLists}</div><div className="metric-note">Owners de precios</div></article>
        <article className="card metric-card"><div className="kicker">impuestos</div><div className="metric">{summary.taxes}</div><div className="metric-note">Tasas canónicas</div></article>
        <article className="card metric-card"><div className="kicker">promociones</div><div className="metric">{summary.promotions}</div><div className="metric-note">Reglas vigentes</div></article>
        <article className="card metric-card"><div className="kicker">descuentos</div><div className="metric">{summary.discounts}</div><div className="metric-note">Políticas durables</div></article>
        <article className="card metric-card"><div className="kicker">autorizaciones</div><div className="metric">{summary.pendingAuthorizations}</div><div className="metric-note">Pendientes</div></article>
      </section>

      {blocked ? <div className="alert-strip"><strong>Mutaciones bloqueadas</strong><span className="subtle">Aplica la migración canónica antes de crear o editar políticas. La lectura existente sigue disponible.</span></div> : null}

      <Section title="Listas de precio" subtitle="Completa el owner existente sin duplicar PriceList ni PriceListItem.">
        <form className="inline-list" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          void create("price-lists", {
            name: values.name,
            currency: values.currency || "MXN",
            isDefault: values.isDefault === "on",
            startsAt: values.startsAt,
            endsAt: values.endsAt || null
          }, event.currentTarget);
        }}>
          <label className="field"><span>Nombre</span><input name="name" required minLength={2} maxLength={140} /></label>
          <label className="field"><span>Moneda</span><input name="currency" defaultValue="MXN" maxLength={3} /></label>
          <label className="field"><span>Inicio</span><input name="startsAt" type="datetime-local" defaultValue={dateInput()} required /></label>
          <label className="field"><span>Fin</span><input name="endsAt" type="datetime-local" /></label>
          <label><input name="isDefault" type="checkbox" /> Predeterminada</label>
          <button className="btn btn-primary" disabled={blocked || pending === "price-lists"}>{pending === "price-lists" ? "Guardando…" : "Crear lista"}</button>
        </form>
        <div className="list">
          {workspace.priceLists.map((row) => <div className="list-item" key={text(row, "id")}>
            <div><strong>{text(row, "name")}</strong><div className="subtle">{text(row, "currency", "MXN")} · {number(row, "itemCount")} producto(s) · v{number(row, "version")}</div></div>
            <button className="btn" type="button" disabled={blocked || pending === `price-lists:${text(row, "id")}`} onClick={() => void patch("price-lists", row, { isActive: !bool(row, "isActive") })}>{bool(row, "isActive") ? "Desactivar" : "Activar"}</button>
          </div>)}
        </div>
      </Section>

      <Section title="Precios por producto" subtitle="Cada importe conserva lista, producto, vigencia, versión y evidencia.">
        <form className="inline-list" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          void create("price-list-items", {
            priceListId: values.priceListId,
            productId: values.productId,
            priceCents: Math.round(Number(values.price || 0) * 100),
            startsAt: values.startsAt,
            endsAt: values.endsAt || null
          }, event.currentTarget);
        }}>
          <label className="field"><span>Lista</span><select name="priceListId" required><option value="">Seleccionar</option>{workspace.priceLists.map((row) => <option key={text(row, "id")} value={text(row, "id")}>{text(row, "name")}</option>)}</select></label>
          <label className="field"><span>Producto</span><select name="productId" required><option value="">Seleccionar</option>{workspace.products.map((product) => <option key={product.id} value={product.id}>{product.sku} · {product.name}</option>)}</select></label>
          <label className="field"><span>Precio MXN</span><input name="price" type="number" min="0" step="0.01" required /></label>
          <label className="field"><span>Inicio</span><input name="startsAt" type="datetime-local" defaultValue={dateInput()} required /></label>
          <label className="field"><span>Fin</span><input name="endsAt" type="datetime-local" /></label>
          <button className="btn btn-primary" disabled={blocked || pending === "price-list-items"}>{pending === "price-list-items" ? "Guardando…" : "Agregar precio"}</button>
        </form>
        <div className="list">{workspace.priceListItems.slice(0, 50).map((row) => <div className="list-item" key={text(row, "id")}><strong>{text(row, "productSku")} · {text(row, "productName")}</strong><span>{text(row, "priceListName")} · ${(number(row, "priceCents") / 100).toFixed(2)} · v{number(row, "version")}</span></div>)}</div>
      </Section>

      <Section title="Impuestos" subtitle="TaxRate conserva su identidad; ahora suma comandos gobernados.">
        <form className="inline-list" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          void create("tax-rates", {
            name: values.name,
            rateBps: Math.round(Number(values.rate || 0) * 100),
            isDefault: values.isDefault === "on"
          }, event.currentTarget);
        }}>
          <label className="field"><span>Nombre</span><input name="name" required maxLength={140} /></label>
          <label className="field"><span>Tasa %</span><input name="rate" type="number" min="0" max="100" step="0.01" required /></label>
          <label><input name="isDefault" type="checkbox" /> Predeterminado</label>
          <button className="btn btn-primary" disabled={blocked || pending === "tax-rates"}>{pending === "tax-rates" ? "Guardando…" : "Crear impuesto"}</button>
        </form>
        <div className="list">{workspace.taxRates.map((row) => <div className="list-item" key={text(row, "id")}><div><strong>{text(row, "name")}</strong><div className="subtle">{(number(row, "rateBps") / 100).toFixed(2)}% · v{number(row, "version")}</div></div><button className="btn" type="button" disabled={blocked || pending === `tax-rates:${text(row, "id")}`} onClick={() => void patch("tax-rates", row, { isActive: !bool(row, "isActive") })}>{bool(row, "isActive") ? "Desactivar" : "Activar"}</button></div>)}</div>
      </Section>

      <Section title="Promociones" subtitle="Reglas con elegibilidad, beneficio, prioridad y política de acumulación.">
        <form className="stack-form" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          void create("promotions", {
            name: values.name,
            description: values.description || null,
            ruleType: values.ruleType || "ORDER",
            priority: Number(values.priority || 100),
            stackingPolicy: values.stackingPolicy || "EXCLUSIVE",
            eligibilityJson: values.eligibilityJson || "{}",
            benefitJson: values.benefitJson || "{}",
            startsAt: values.startsAt,
            endsAt: values.endsAt || null
          }, event.currentTarget);
        }}>
          <label>Nombre<input name="name" required maxLength={160} /></label>
          <label>Descripción<input name="description" maxLength={800} /></label>
          <div className="inline-list">
            <label className="field"><span>Tipo</span><select name="ruleType"><option value="ORDER">Orden</option><option value="PRODUCT">Producto</option><option value="CUSTOMER">Cliente</option></select></label>
            <label className="field"><span>Prioridad</span><input name="priority" type="number" defaultValue="100" min="0" /></label>
            <label className="field"><span>Acumulación</span><select name="stackingPolicy"><option value="EXCLUSIVE">Exclusiva</option><option value="STACKABLE">Acumulable</option></select></label>
            <label className="field"><span>Inicio</span><input name="startsAt" type="datetime-local" defaultValue={dateInput()} required /></label>
            <label className="field"><span>Fin</span><input name="endsAt" type="datetime-local" /></label>
          </div>
          <label>Elegibilidad JSON<textarea name="eligibilityJson" defaultValue='{"minimumSubtotalCents":0}' /></label>
          <label>Beneficio JSON<textarea name="benefitJson" defaultValue='{"type":"PERCENT","valueBps":0}' /></label>
          <button className="btn btn-primary" disabled={blocked || pending === "promotions"}>{pending === "promotions" ? "Guardando…" : "Crear promoción"}</button>
        </form>
        <div className="list">{workspace.promotions.map((row) => <div className="list-item" key={text(row, "id")}><div><strong>{text(row, "name")}</strong><div className="subtle">{text(row, "ruleType")} · {text(row, "stackingPolicy")} · v{number(row, "version")}</div></div><button className="btn" type="button" disabled={blocked || pending === `promotions:${text(row, "id")}`} onClick={() => void patch("promotions", row, { status: text(row, "status").toUpperCase() === "ACTIVE" ? "INACTIVE" : "ACTIVE" })}>{text(row, "status").toUpperCase() === "ACTIVE" ? "Desactivar" : "Activar"}</button></div>)}</div>
      </Section>

      <Section title="Descuentos" subtitle="Políticas separadas del descuento ya aplicado al ticket.">
        <form className="inline-list" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          const type = String(values.discountType || "PERCENT");
          void create("discounts", {
            name: values.name,
            discountType: type,
            valueBps: type === "PERCENT" ? Math.round(Number(values.value || 0) * 100) : null,
            valueCents: type === "FIXED" ? Math.round(Number(values.value || 0) * 100) : null,
            minimumSubtotalCents: Math.round(Number(values.minimumSubtotal || 0) * 100),
            maximumDiscountCents: values.maximumDiscount ? Math.round(Number(values.maximumDiscount) * 100) : null,
            scopeJson: values.scopeJson || "{}",
            authorizationRuleId: values.authorizationRuleId || null,
            startsAt: values.startsAt,
            endsAt: values.endsAt || null
          }, event.currentTarget);
        }}>
          <label className="field"><span>Nombre</span><input name="name" required /></label>
          <label className="field"><span>Tipo</span><select name="discountType"><option value="PERCENT">Porcentaje</option><option value="FIXED">Importe fijo</option></select></label>
          <label className="field"><span>Valor</span><input name="value" type="number" min="0" step="0.01" required /></label>
          <label className="field"><span>Subtotal mínimo</span><input name="minimumSubtotal" type="number" min="0" step="0.01" defaultValue="0" /></label>
          <label className="field"><span>Tope</span><input name="maximumDiscount" type="number" min="0" step="0.01" /></label>
          <label className="field"><span>Regla autorización</span><select name="authorizationRuleId"><option value="">Sin autorización adicional</option>{workspace.authorizationRules.map((row) => <option key={text(row, "id")} value={text(row, "id")}>{text(row, "name")}</option>)}</select></label>
          <label className="field"><span>Inicio</span><input name="startsAt" type="datetime-local" defaultValue={dateInput()} required /></label>
          <label className="field"><span>Fin</span><input name="endsAt" type="datetime-local" /></label>
          <label className="field"><span>Scope JSON</span><input name="scopeJson" defaultValue="{}" /></label>
          <button className="btn btn-primary" disabled={blocked || pending === "discounts"}>{pending === "discounts" ? "Guardando…" : "Crear descuento"}</button>
        </form>
        <div className="list">{workspace.discounts.map((row) => <div className="list-item" key={text(row, "id")}><div><strong>{text(row, "name")}</strong><div className="subtle">{text(row, "discountType")} · v{number(row, "version")}</div></div><button className="btn" type="button" disabled={blocked || pending === `discounts:${text(row, "id")}`} onClick={() => void patch("discounts", row, { status: text(row, "status").toUpperCase() === "ACTIVE" ? "INACTIVE" : "ACTIVE" })}>{text(row, "status").toUpperCase() === "ACTIVE" ? "Desactivar" : "Activar"}</button></div>)}</div>
      </Section>

      <Section title="Reglas de autorización" subtitle="Umbrales y permisos separados de licencias, proveedores o gobierno visual.">
        <form className="inline-list" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          void create("authorization-rules", {
            name: values.name,
            actionType: values.actionType || "DISCOUNT",
            thresholdType: values.thresholdType || "BPS",
            thresholdValue: Number(values.thresholdValue || 0),
            requiredPermission: values.requiredPermission || "pricing.authorization.decide"
          }, event.currentTarget);
        }}>
          <label className="field"><span>Nombre</span><input name="name" required /></label>
          <label className="field"><span>Acción</span><select name="actionType"><option value="DISCOUNT">Descuento</option><option value="PRICE_OVERRIDE">Cambio de precio</option><option value="PROMOTION">Promoción</option></select></label>
          <label className="field"><span>Umbral</span><select name="thresholdType"><option value="BPS">Puntos base</option><option value="CENTS">Centavos</option></select></label>
          <label className="field"><span>Valor</span><input name="thresholdValue" type="number" min="0" required /></label>
          <label className="field"><span>Permiso</span><input name="requiredPermission" defaultValue="pricing.authorization.decide" required /></label>
          <button className="btn btn-primary" disabled={blocked || pending === "authorization-rules"}>{pending === "authorization-rules" ? "Guardando…" : "Crear regla"}</button>
        </form>
        <div className="list">{workspace.authorizationRules.map((row) => <div className="list-item" key={text(row, "id")}><div><strong>{text(row, "name")}</strong><div className="subtle">{text(row, "actionType")} · {text(row, "thresholdType")} {number(row, "thresholdValue")} · v{number(row, "version")}</div></div><button className="btn" type="button" disabled={blocked || pending === `authorization-rules:${text(row, "id")}`} onClick={() => void patch("authorization-rules", row, { status: text(row, "status").toUpperCase() === "ACTIVE" ? "INACTIVE" : "ACTIVE" })}>{text(row, "status").toUpperCase() === "ACTIVE" ? "Desactivar" : "Activar"}</button></div>)}</div>
      </Section>

      <Section title="Solicitudes de autorización" subtitle="Toda decisión conserva actor, motivo, versión y evidencia durable.">
        <form className="inline-list" onSubmit={(event) => {
          event.preventDefault();
          const values = formObject(event);
          void create("authorization-requests", {
            ruleId: values.ruleId,
            requestedById: values.requestedById || null,
            requestedActionJson: values.requestedActionJson || "{}",
            reason: values.reason
          }, event.currentTarget);
        }}>
          <label className="field"><span>Regla</span><select name="ruleId" required><option value="">Seleccionar</option>{workspace.authorizationRules.filter((row) => text(row, "status").toUpperCase() === "ACTIVE").map((row) => <option key={text(row, "id")} value={text(row, "id")}>{text(row, "name")}</option>)}</select></label>
          <label className="field"><span>Solicitante</span><input name="requestedById" /></label>
          <label className="field"><span>Acción JSON</span><input name="requestedActionJson" defaultValue='{"type":"DISCOUNT"}' /></label>
          <label className="field"><span>Motivo</span><input name="reason" required maxLength={800} /></label>
          <button className="btn btn-primary" disabled={blocked || pending === "authorization-requests"}>{pending === "authorization-requests" ? "Guardando…" : "Solicitar"}</button>
        </form>
        <div className="list">{workspace.authorizationRequests.map((row) => <div className="list-item" key={text(row, "id")}><div><strong>{text(row, "ruleName", text(row, "ruleId"))}</strong><div className="subtle">{text(row, "status")} · {text(row, "reason")} · v{number(row, "version")}</div></div>{text(row, "status").toUpperCase() === "PENDING" ? <div className="inline-list"><button className="btn btn-primary" type="button" disabled={blocked || pending === `authorization-requests:${text(row, "id")}`} onClick={() => void patch("authorization-requests", row, { status: "APPROVED", decisionReason: "Aprobada desde Pricing PC." })}>Aprobar</button><button className="btn" type="button" disabled={blocked || pending === `authorization-requests:${text(row, "id")}`} onClick={() => void patch("authorization-requests", row, { status: "DENIED", decisionReason: "Denegada desde Pricing PC." })}>Denegar</button></div> : null}</div>)}</div>
      </Section>
    </div>
  );
}
