"use client";

import { type FormEvent, useMemo, useState } from "react";
import { AppShell } from "@components/layout/app-shell";
import { DataTable } from "@components/backoffice/data-table";

type CustomerSummary = {
  id: string;
  displayName: string;
  phone: string | null;
  email: string | null;
  segment: string | null;
  creditCents: number;
  isActive: boolean;
  updatedAt: string;
};

type CustomerDetail = CustomerSummary & {
  version: number;
  contacts: Array<{ id: string; label: string; channel: string; value: string; isPrimary: boolean }>;
  fiscalProfiles: Array<{ id: string; legalName: string; rfc: string | null; taxRegime: string | null; postalCode: string | null; invoicingEmail: string | null; isPrimary: boolean }>;
  segments: Array<{ id: string; name: string; color: string | null }>;
  history: { ticketCount: number; totalCents: number; lastSaleAt: string | null };
};

type CustomerWorkspaceModel = {
  customers: CustomerSummary[];
  meta: { source: "canonical_prisma" | "unavailable"; generatedAt: string; warnings: string[] };
};

function money(cents: number) {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: "MXN" }).format(cents / 100);
}

function dateTime(value: string | null) {
  if (!value) return "Sin ventas";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Sin fecha" : new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(date);
}

async function readApi<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible completar la operación.");
  return body.data;
}

export function CustomerWorkspace({ initialWorkspace }: { initialWorkspace: CustomerWorkspaceModel }) {
  const [customers, setCustomers] = useState(initialWorkspace.customers);
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"active" | "all">("active");
  const [selected, setSelected] = useState<CustomerDetail | null>(null);
  const [status, setStatus] = useState(initialWorkspace.meta.warnings[0] ?? "");
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ displayName: "", phone: "", email: "", segment: "", legalName: "", rfc: "" });
  const [editForm, setEditForm] = useState({ displayName: "", phone: "", email: "", segment: "", legalName: "", rfc: "", isActive: true });

  const visibleCount = useMemo(() => customers.filter((customer) => customer.isActive).length, [customers]);

  async function searchCustomers(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setStatus("");
    try {
      const data = await readApi<CustomerWorkspaceModel>(await fetch(`/api/backoffice/customers?q=${encodeURIComponent(query)}&includeInactive=${statusFilter === "all"}`, { cache: "no-store" }));
      setCustomers(data.customers);
      setSelected(null);
      setStatus(`${data.customers.length} cliente(s) encontrados.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible buscar clientes.");
    } finally {
      setIsLoading(false);
    }
  }

  async function openCustomer(customerId: string) {
    setIsLoading(true);
    setStatus("");
    try {
      const data = await readApi<{ customer: CustomerDetail }>(await fetch(`/api/backoffice/customers/${encodeURIComponent(customerId)}`, { cache: "no-store" }));
      setSelected(data.customer);
      setEditForm({
        displayName: data.customer.displayName,
        phone: data.customer.phone ?? "",
        email: data.customer.email ?? "",
        segment: data.customer.segment ?? "",
        legalName: data.customer.fiscalProfiles[0]?.legalName ?? "",
        rfc: data.customer.fiscalProfiles[0]?.rfc ?? "",
        isActive: data.customer.isActive
      });
      setIsEditing(false);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible abrir el cliente.");
    } finally {
      setIsLoading(false);
    }
  }

  async function saveCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setIsSaving(true);
    setStatus("");
    try {
      const fiscalProfile = editForm.legalName.trim() ? { legalName: editForm.legalName.trim(), rfc: editForm.rfc.trim() || null } : undefined;
      const data = await readApi<{ customer: CustomerDetail }>(await fetch(`/api/backoffice/customers/${encodeURIComponent(selected.id)}`, {
        method: "PATCH",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          displayName: editForm.displayName,
          phone: editForm.phone || null,
          email: editForm.email || null,
          segment: editForm.segment || null,
          isActive: editForm.isActive,
          fiscalProfile,
          expectedVersion: selected.version
        })
      }));
      setSelected(data.customer);
      setCustomers((current) => current.map((customer) => customer.id === data.customer.id ? data.customer : customer).sort((a, b) => a.displayName.localeCompare(b.displayName, "es-MX")));
      setIsEditing(false);
      setStatus("Cliente actualizado correctamente.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible actualizar el cliente.");
    } finally {
      setIsSaving(false);
    }
  }

  async function createCustomer(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setStatus("");
    try {
      const fiscalProfile = form.legalName.trim() ? { legalName: form.legalName.trim(), rfc: form.rfc.trim() || null } : undefined;
      const data = await readApi<{ customer: CustomerDetail }>(await fetch("/api/backoffice/customers", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          displayName: form.displayName,
          phone: form.phone || null,
          email: form.email || null,
          segment: form.segment || null,
          fiscalProfile
        })
      }));
      setCustomers((current) => [...current.filter((customer) => customer.id !== data.customer.id), data.customer].sort((a, b) => a.displayName.localeCompare(b.displayName, "es-MX")));
      setSelected(data.customer);
      setForm({ displayName: "", phone: "", email: "", segment: "", legalName: "", rfc: "" });
      setStatus("Cliente creado correctamente.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible crear el cliente.");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <AppShell currentPath="/clientes">
      <section className="hero">
        <div className="hero-header">
          <div className="hero-copy">
            <div className="kicker">clientes</div>
            <h1 className="hero-title">Clientes y venta identificada</h1>
            <p>Consulta y administra fichas de clientes, datos fiscales, contacto e historial de compra.</p>
          </div>
          <div className="inline-list">
            <span className="chip">Activos: {visibleCount}</span>
            <span className="chip">Información: {initialWorkspace.meta.source === "canonical_prisma" ? "disponible" : "no disponible"}</span>
          </div>
        </div>
      </section>

      {status ? <div className="alert-strip" role="status" aria-live="polite"><strong>Clientes</strong><span className="subtle">{status}</span></div> : null}

      <section className="dashboard-grid">
        <article className="card">
          <div className="section-head"><div><div className="kicker">buscar</div><h2 className="section-title">Encontrar cliente</h2></div></div>
          <form onSubmit={searchCustomers} className="stack-form">
            <label htmlFor="customer-query">Nombre, teléfono o correo</label>
            <input id="customer-query" value={query} onChange={(event) => setQuery(event.target.value)} maxLength={120} />
            <label htmlFor="customer-status-filter">Estado</label>
            <select id="customer-status-filter" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value === "all" ? "all" : "active")}>
              <option value="active">Sólo activos</option>
              <option value="all">Todos, incluidos inactivos</option>
            </select>
            <button className="button button-secondary" type="submit" disabled={isLoading}>{isLoading ? "Buscando…" : "Buscar"}</button>
          </form>
        </article>
        <article className="card">
          <div className="section-head"><div><div className="kicker">nuevo registro</div><h2 className="section-title">Nuevo cliente</h2></div></div>
          <form onSubmit={createCustomer} className="stack-form">
            <label htmlFor="customer-name">Nombre</label>
            <input id="customer-name" value={form.displayName} onChange={(event) => setForm((current) => ({ ...current, displayName: event.target.value }))} minLength={2} maxLength={140} required />
            <label htmlFor="customer-phone">Teléfono</label>
            <input id="customer-phone" value={form.phone} onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))} maxLength={40} />
            <label htmlFor="customer-email">Correo</label>
            <input id="customer-email" type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} maxLength={160} />
            <label htmlFor="customer-segment">Segmento</label>
            <input id="customer-segment" value={form.segment} onChange={(event) => setForm((current) => ({ ...current, segment: event.target.value }))} maxLength={80} />
            <label htmlFor="customer-fiscal-name">Razón social (opcional)</label>
            <input id="customer-fiscal-name" value={form.legalName} onChange={(event) => setForm((current) => ({ ...current, legalName: event.target.value }))} maxLength={180} />
            <label htmlFor="customer-rfc">RFC (opcional)</label>
            <input id="customer-rfc" value={form.rfc} onChange={(event) => setForm((current) => ({ ...current, rfc: event.target.value }))} maxLength={20} />
            <button className="button button-primary" type="submit" disabled={isCreating}>{isCreating ? "Guardando…" : "Guardar cliente"}</button>
          </form>
        </article>
      </section>

      <section className="card">
        <div className="section-head"><div><div className="kicker">directorio</div><h2 className="section-title">Clientes disponibles</h2><div className="section-copy">Los clientes activos pueden utilizarse en las operaciones que admitan venta identificada.</div></div></div>
        <DataTable
          columns={["Nombre", "Contacto", "Segmento", "Crédito", "Estado"]}
          rows={customers.map((customer) => ({
            Nombre: customer.displayName,
            Contacto: customer.phone || customer.email || "Sin contacto",
            Segmento: customer.segment || "Sin segmento",
            Crédito: money(customer.creditCents),
            Estado: customer.isActive ? "Activo" : "Inactivo",
            __rowActionHref: `#customer-${customer.id}`,
            __rowActionLabel: "Abrir ficha"
          }))}
          emptyMessage="Aún no hay clientes disponibles para mostrar."
        />
        <div className="inline-list" style={{ marginTop: 12 }}>
          {customers.map((customer) => <button key={customer.id} type="button" className="button button-secondary" onClick={() => void openCustomer(customer.id)} disabled={isLoading}>Abrir {customer.displayName}</button>)}
        </div>
      </section>

      {selected ? (
        <section className="card" id={`customer-${selected.id}`}>
          <div className="section-head"><div><div className="kicker">ficha de cliente</div><h2 className="section-title">{selected.displayName}</h2><div className="section-copy">Actualizada {dateTime(selected.updatedAt)}</div></div><button className="button button-secondary" type="button" onClick={() => setIsEditing((current) => !current)}>{isEditing ? "Cerrar edición" : "Editar ficha"}</button></div>
          <div className="dashboard-grid">
            <article className="metric-card"><div className="card-title">Tickets</div><div className="metric">{selected.history.ticketCount}</div><div className="metric-note">Última venta: {dateTime(selected.history.lastSaleAt)}</div></article>
            <article className="metric-card"><div className="card-title">Venta acumulada</div><div className="metric">{money(selected.history.totalCents)}</div><div className="metric-note">Ventas asociadas a esta ficha.</div></article>
            <article className="metric-card"><div className="card-title">Crédito</div><div className="metric">{money(selected.creditCents)}</div><div className="metric-note">Saldo registrado para este cliente.</div></article>
          </div>
          <DataTable
            columns={["Dato", "Valor"]}
            rows={[
              ...selected.contacts.map((contact) => ({ Dato: `${contact.label}${contact.isPrimary ? " (principal)" : ""}`, Valor: contact.value })),
              ...selected.fiscalProfiles.map((profile) => ({ Dato: `Fiscal${profile.isPrimary ? " (principal)" : ""}`, Valor: [profile.legalName, profile.rfc, profile.taxRegime, profile.postalCode, profile.invoicingEmail].filter(Boolean).join(" · ") })),
              { Dato: "Segmentos", Valor: selected.segments.map((segment) => segment.name).join(", ") || selected.segment || "Sin segmento" }
            ]}
            emptyMessage="La ficha no tiene contactos ni datos fiscales adicionales."
          />
          {isEditing ? (
            <form onSubmit={saveCustomer} className="stack-form">
              <div className="kicker">editar ficha</div>
              <label htmlFor="edit-customer-name">Nombre</label>
              <input id="edit-customer-name" value={editForm.displayName} onChange={(event) => setEditForm((current) => ({ ...current, displayName: event.target.value }))} minLength={2} maxLength={140} required />
              <label htmlFor="edit-customer-phone">Teléfono</label>
              <input id="edit-customer-phone" value={editForm.phone} onChange={(event) => setEditForm((current) => ({ ...current, phone: event.target.value }))} maxLength={40} />
              <label htmlFor="edit-customer-email">Correo</label>
              <input id="edit-customer-email" type="email" value={editForm.email} onChange={(event) => setEditForm((current) => ({ ...current, email: event.target.value }))} maxLength={160} />
              <label htmlFor="edit-customer-segment">Segmento</label>
              <input id="edit-customer-segment" value={editForm.segment} onChange={(event) => setEditForm((current) => ({ ...current, segment: event.target.value }))} maxLength={80} />
              <label htmlFor="edit-customer-fiscal-name">Razón social</label>
              <input id="edit-customer-fiscal-name" value={editForm.legalName} onChange={(event) => setEditForm((current) => ({ ...current, legalName: event.target.value }))} maxLength={180} />
              <label htmlFor="edit-customer-rfc">RFC</label>
              <input id="edit-customer-rfc" value={editForm.rfc} onChange={(event) => setEditForm((current) => ({ ...current, rfc: event.target.value }))} maxLength={20} />
              <label><input type="checkbox" checked={editForm.isActive} onChange={(event) => setEditForm((current) => ({ ...current, isActive: event.target.checked }))} /> Cliente activo</label>
              <button className="button button-primary" type="submit" disabled={isSaving}>{isSaving ? "Guardando…" : "Guardar cambios"}</button>
            </form>
          ) : null}
        </section>
      ) : null}
    </AppShell>
  );
}
