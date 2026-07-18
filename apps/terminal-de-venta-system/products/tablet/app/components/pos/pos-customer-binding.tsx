"use client";

import { useEffect, useState } from "react";

type PosCustomer = { id: string; displayName: string; version: number; sourceSurface: string; updatedAt: string };

async function readJson<T>(response: Response) {
  const body = await response.json().catch(() => null) as { ok?: boolean; data?: T; message?: string } | null;
  if (!response.ok || !body?.ok || !body.data) throw new Error(body?.message || "No fue posible leer clientes.");
  return body.data;
}

export function PosCustomerBinding({ customerId, onChange, disabled }: { customerId: string | null; onChange: (customerId: string | null) => void; disabled?: boolean }) {
  const [customers, setCustomers] = useState<PosCustomer[]>([]);
  const [query, setQuery] = useState("");
  const [newName, setNewName] = useState("");
  const [message, setMessage] = useState("");

  async function load(search = "") {
    try {
      const data = await readJson<{ customers: PosCustomer[] }>(await fetch(`/api/pos/customers?q=${encodeURIComponent(search)}`, { cache: "no-store" }));
      setCustomers(data.customers);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No fue posible leer clientes locales.");
    }
  }

  useEffect(() => { void load(); }, []);

  async function createCustomer() {
    if (newName.trim().length < 2 || disabled) return;
    try {
      const data = await readJson<{ customer: PosCustomer }>(await fetch("/api/pos/customers", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ displayName: newName }) }));
      setCustomers((current) => [...current.filter((customer) => customer.id !== data.customer.id), data.customer].sort((a, b) => a.displayName.localeCompare(b.displayName, "es-MX")));
      onChange(data.customer.id);
      setNewName("");
      setMessage("Cliente creado localmente; su sincronización queda pendiente.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No fue posible crear el cliente.");
    }
  }

  const selected = customers.find((customer) => customer.id === customerId) ?? null;
  return (
    <section aria-labelledby="pos-customer-binding-title">
      <div>
        <span>Paso opcional</span>
        <h2 id="pos-customer-binding-title">Cliente</h2>
      </div>
      <label htmlFor="pos-customer-search">Buscar cliente local</label>
      <input id="pos-customer-search" value={query} onChange={(event) => setQuery(event.target.value)} onBlur={() => void load(query)} disabled={disabled} maxLength={100} />
      <select aria-label="Cliente seleccionado" value={customerId ?? ""} onChange={(event) => onChange(event.target.value || null)} disabled={disabled}>
        <option value="">Venta sin cliente</option>
        {customers.map((customer) => <option key={customer.id} value={customer.id}>{customer.displayName}</option>)}
      </select>
      {selected ? <p>Cliente seleccionado: <strong>{selected.displayName}</strong> <button type="button" onClick={() => onChange(null)} disabled={disabled}>Quitar</button></p> : null}
      <label htmlFor="pos-customer-new">Alta mínima offline</label>
      <input id="pos-customer-new" value={newName} onChange={(event) => setNewName(event.target.value)} disabled={disabled} minLength={2} maxLength={140} />
      <button type="button" onClick={() => void createCustomer()} disabled={disabled || newName.trim().length < 2}>Crear y seleccionar</button>
      {message ? <p role="status">{message}</p> : null}
    </section>
  );
}
