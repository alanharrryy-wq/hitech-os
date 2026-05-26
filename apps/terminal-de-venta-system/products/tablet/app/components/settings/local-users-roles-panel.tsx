"use client";

import { useMemo, useState, type ChangeEvent, type FormEvent, type ReactNode } from "react";
import { requestJson } from "@/lib/pos/cart-state";
import type { LocalAdminSnapshot } from "@/server/pos-api/local-admin.prisma";
import styles from "@components/license/license-ui.module.css";

type UserForm = {
  userId: string;
  fullName: string;
  alias: string;
  email: string;
  phone: string;
  roleCode: string;
  pin: string;
  status: string;
};

type Props = {
  initialSnapshot: LocalAdminSnapshot;
};

type SnapshotRole = { code: string; label: string; description?: string | null; permissions: string[] };
type SnapshotUser = LocalAdminSnapshot["users"][number];

const emptyForm = (roleCode = "cashier"): UserForm => ({
  userId: "",
  fullName: "",
  alias: "",
  email: "",
  phone: "",
  roleCode,
  pin: "",
  status: "ACTIVE"
});

function splitDisplayName(displayName: string) {
  const match = displayName.match(/^(.*)\s\((.*)\)$/);
  if (!match) return { fullName: displayName, alias: "" };
  return { fullName: match[1] ?? displayName, alias: match[2] ?? "" };
}

export function LocalUsersRolesPanel({ initialSnapshot }: Props) {
  const [snapshot, setSnapshot] = useState(initialSnapshot);
  const [form, setForm] = useState<UserForm>(() => emptyForm(initialSnapshot.roles[0]?.code ?? "cashier"));
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const editing = Boolean(form.userId);
  const canSubmit = form.fullName.trim().length > 1 && form.roleCode && (!editing ? /^\d{6}$/.test(form.pin) : !form.pin || /^\d{6}$/.test(form.pin)) && !busy;

  const activeRole = useMemo(() => snapshot.roles.find((role: SnapshotRole) => role.code === form.roleCode), [form.roleCode, snapshot.roles]);

  function update<K extends keyof UserForm>(key: K, value: UserForm[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function reloadFrom(response: { data: { snapshot: LocalAdminSnapshot } }) {
    setSnapshot(response.data.snapshot);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setMessage(null);
    try {
      const response = await requestJson<{ snapshot: LocalAdminSnapshot }>("/api/pos/admin/local-users", {
        method: "POST",
        body: JSON.stringify({
          action: editing ? "update_user" : "create_user",
          businessId: snapshot.businessId,
          userId: form.userId || undefined,
          fullName: form.fullName,
          alias: form.alias,
          email: form.email,
          phone: form.phone,
          roleCode: form.roleCode,
          pin: form.pin || undefined,
          status: form.status
        })
      });
      await reloadFrom(response);
      setForm(emptyForm(snapshot.roles[0]?.code ?? "cashier"));
      setMessage(editing ? "Usuario actualizado y auditado." : "Usuario creado con employee ID automático y PIN hash local.");
    } catch (error) {
      setMessage(readError(error, "No fue posible guardar el usuario local."));
    } finally {
      setBusy(false);
    }
  }

  async function runUserAction(action: "deactivate_user" | "reactivate_user" | "soft_delete_user", userId: string) {
    setBusy(true);
    setMessage(null);
    try {
      const response = await requestJson<{ snapshot: LocalAdminSnapshot }>("/api/pos/admin/local-users", {
        method: "POST",
        body: JSON.stringify({ action, businessId: snapshot.businessId, userId })
      });
      await reloadFrom(response);
      setMessage(action === "soft_delete_user" ? "Usuario dado de baja suave." : "Estado del usuario actualizado.");
    } catch (error) {
      setMessage(readError(error, "No fue posible actualizar el usuario."));
    } finally {
      setBusy(false);
    }
  }

  function editUser(user: SnapshotUser) {
    const display = splitDisplayName(user.displayName);
    setForm({
      userId: user.id,
      fullName: display.fullName,
      alias: display.alias,
      email: user.email ?? "",
      phone: "",
      roleCode: user.roles[0]?.code ?? "cashier",
      pin: "",
      status: user.status
    });
  }

  return (
    <section className={styles.card}>
      <p className={styles.eyebrow}>Usuarios y permisos</p>
      <h2 className={styles.title}>Administración local operativa</h2>
      <p className={styles.copy}>
        Usuarios reales de la Tablet con employee ID automático, roles, permisos, baja suave y auditoría. El rol técnico de soporte queda fuera de la lista operativa.
      </p>

      <div className={styles.metricGrid}>
        <Metric label="Usuarios activos" value={String(snapshot.users.filter((user: SnapshotUser) => user.status === "ACTIVE").length)} />
        <Metric label="Roles" value={String(snapshot.roles.length)} />
        <Metric label="Permisos" value={String(snapshot.permissions.length)} />
        <Metric label="Auditoría usuarios" value={String(snapshot.auditTrailCount)} />
      </div>

      <form className={styles.refreshForm} onSubmit={submit}>
        <div className={styles.metricGrid}>
          <Field label="Nombre completo" id="local-user-full-name">
            <input id="local-user-full-name" value={form.fullName} onChange={(event) => update("fullName", event.target.value)} style={inputStyle} />
          </Field>
          <Field label="Alias visible" id="local-user-alias">
            <input id="local-user-alias" value={form.alias} onChange={(event) => update("alias", event.target.value)} style={inputStyle} />
          </Field>
          <Field label="Email" id="local-user-email">
            <input id="local-user-email" value={form.email} onChange={(event) => update("email", event.target.value)} style={inputStyle} />
          </Field>
          <Field label="Teléfono opcional" id="local-user-phone">
            <input id="local-user-phone" value={form.phone} onChange={(event) => update("phone", event.target.value)} style={inputStyle} />
          </Field>
          <Field label="Rol" id="local-user-role">
            <select id="local-user-role" value={form.roleCode} onChange={(event: ChangeEvent<HTMLSelectElement>) => update("roleCode", event.target.value)} style={inputStyle}>
              {snapshot.roles.map((role: SnapshotRole) => <option key={role.code} value={role.code}>{role.label}</option>)}
            </select>
          </Field>
          <Field label={editing ? "Nuevo PIN opcional" : "PIN de 6 dígitos"} id="local-user-pin">
            <input
              id="local-user-pin"
              value={form.pin}
              onChange={(event) => update("pin", event.target.value.replace(/\D/g, "").slice(0, 6))}
              inputMode="numeric"
              type="password"
              autoComplete="new-password"
              placeholder="000000"
              style={inputStyle}
            />
          </Field>
        </div>
        {editing ? (
          <Field label="Estado" id="local-user-status">
            <select id="local-user-status" value={form.status} onChange={(event: ChangeEvent<HTMLSelectElement>) => update("status", event.target.value)} style={inputStyle}>
              <option value="ACTIVE">Activo</option>
              <option value="INACTIVE">Inactivo</option>
            </select>
          </Field>
        ) : null}
        {activeRole ? <p className={styles.helper}>{activeRole.description}</p> : null}
        <div className={styles.refreshActions}>
          <button className={styles.primaryButton} type="submit" disabled={!canSubmit} aria-disabled={!canSubmit}>
            {busy ? "Guardando..." : editing ? "Guardar cambios" : "Crear usuario"}
          </button>
          {editing ? (
            <button type="button" className={styles.secondaryLink} onClick={() => setForm(emptyForm(snapshot.roles[0]?.code ?? "cashier"))}>
              Cancelar edición
            </button>
          ) : null}
        </div>
      </form>

      {message ? <div className={styles.warning}>{message}</div> : null}

      <div className={styles.warningList}>
        {snapshot.users.length ? snapshot.users.map((user: SnapshotUser) => (
          <article key={user.id} className={styles.metric}>
            <strong>{user.displayName}</strong>
            <div className={styles.metricValue}>{user.employeeId}</div>
            <p className={styles.helper}>{user.email ?? "Sin email"} · {user.status} · {user.roles.map((role: SnapshotRole) => role.label).join(", ")}</p>
            <div className={styles.refreshActions}>
              <button type="button" className={styles.secondaryLink} onClick={() => editUser(user)}>Editar</button>
              {user.status === "ACTIVE" ? (
                <button type="button" className={styles.secondaryLink} onClick={() => void runUserAction("deactivate_user", user.id)}>Desactivar</button>
              ) : (
                <button type="button" className={styles.secondaryLink} onClick={() => void runUserAction("reactivate_user", user.id)}>Reactivar</button>
              )}
              <button type="button" className={styles.secondaryLink} onClick={() => void runUserAction("soft_delete_user", user.id)}>Baja suave</button>
            </div>
          </article>
        )) : (
          <div className={styles.warning}>No hay usuarios operativos registrados todavía.</div>
        )}
      </div>

      <details className={styles.metric}>
        <summary>Permisos por rol</summary>
        {snapshot.roles.map((role: SnapshotRole) => (
          <p key={role.code} className={styles.helper}>
            <strong>{role.label}</strong>: {role.permissions.join(", ")}
          </p>
        ))}
      </details>
    </section>
  );
}

const inputStyle = { width: "100%", minHeight: 46, margin: "8px 0 12px", padding: "0 12px" };

function Field({ label, id, children }: { label: string; id: string; children: ReactNode }) {
  return (
    <label className={styles.metricLabel} htmlFor={id}>
      {label}
      {children}
    </label>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.metric}>
      <span className={styles.metricLabel}>{label}</span>
      <span className={styles.metricValue}>{value}</span>
    </div>
  );
}

function readError(error: unknown, fallback: string) {
  if (error && typeof error === "object" && "message" in error) return String((error as { message?: string }).message);
  return fallback;
}
