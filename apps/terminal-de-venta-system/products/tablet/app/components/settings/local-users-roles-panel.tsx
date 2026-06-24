"use client";

import type { LocalAdminSnapshot } from "@/server/pos-api/local-admin.prisma";
import styles from "@components/license/license-ui.module.css";

type Props = {
  initialSnapshot: LocalAdminSnapshot;
};

type SnapshotRole = { code: string; label: string; description?: string | null; permissions: string[] };
type SnapshotUser = LocalAdminSnapshot["users"][number];

function userPrimaryRole(user: SnapshotUser) {
  return user.roles[0]?.label ?? "Operador";
}

function statusCopy(status: string) {
  if (status === "ACTIVE") return "Acceso activo";
  if (status === "INACTIVE") return "Acceso inactivo";
  return "Requiere revisión";
}

function permissionCopy(permission: string) {
  const normalized = permission.toLowerCase();
  if (normalized.includes("return")) return "Puede iniciar o revisar devoluciones si su rol lo permite.";
  if (normalized.includes("shift") || normalized.includes("cash")) return "Puede consultar caja y turno según permisos activos.";
  if (normalized.includes("sale") || normalized.includes("pos")) return "Puede vender y revisar tickets operativos.";
  if (normalized.includes("catalog") || normalized.includes("product")) return "Puede consultar productos y existencias.";
  return "Permiso operativo visible para este rol.";
}

export function LocalUsersRolesPanel({ initialSnapshot }: Props) {
  const activeUsers = initialSnapshot.users.filter((user: SnapshotUser) => user.status === "ACTIVE");
  const currentUser = activeUsers[0] ?? initialSnapshot.users[0] ?? null;

  return (
    <section className={styles.card} data-prisma-client-final="users-readonly">
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Usuarios y permisos</p>
          <h2 className={styles.sectionTitle}>Consulta de acceso</h2>
          <p className={styles.copy}>
            Esta vista explica quién está operando, qué permisos tiene y qué acciones requieren autorización. La edición de usuarios queda fuera del flujo de operador.
          </p>
        </div>
        <span className={styles.readonlyPill}>Sólo lectura</span>
      </div>

      <div className={styles.metricGrid}>
        <Metric label="Usuario actual" value={currentUser?.displayName ?? "Sin usuario activo"} />
        <Metric label="Rol" value={currentUser ? userPrimaryRole(currentUser) : "Sin rol"} />
        <Metric label="Estado" value={currentUser ? statusCopy(currentUser.status) : "Sin acceso activo"} />
        <Metric label="Roles visibles" value={String(initialSnapshot.roles.length)} />
      </div>

      <div className={styles.warningList} aria-label="Usuarios visibles">
        {initialSnapshot.users.length ? initialSnapshot.users.map((user: SnapshotUser) => (
          <article key={user.id} className={styles.metric}>
            <span className={styles.metricLabel}>{statusCopy(user.status)}</span>
            <strong>{user.displayName}</strong>
            <p className={styles.helper}>
              {userPrimaryRole(user)}. {user.status === "ACTIVE" ? "Puede operar dentro de sus permisos." : "No puede operar hasta autorización administrativa."}
            </p>
          </article>
        )) : (
          <div className={styles.warning}>No hay usuarios operativos registrados para mostrar.</div>
        )}
      </div>

      <div className={styles.featureGroups} aria-label="Permisos por rol">
        {initialSnapshot.roles.map((role: SnapshotRole) => (
          <details key={role.code} className={styles.featureGroup}>
            <summary>
              <span>{role.label}</span>
              <em>{role.permissions.length} permiso(s)</em>
            </summary>
            <p className={styles.helper}>{role.description ?? "Rol operativo de Tablet."}</p>
            <div className={styles.featureList}>
              {role.permissions.map((permission) => (
                <article key={`${role.code}-${permission}`} className={styles.featureItem}>
                  <div>
                    <strong>{permission}</strong>
                    <span>{permissionCopy(permission)}</span>
                  </div>
                  <span className={styles.featurePill}>Visible</span>
                </article>
              ))}
            </div>
          </details>
        ))}
      </div>

      <div className={styles.operatorNotice}>
        <strong>Sin edición en Tablet final</strong>
        <span>Para crear usuarios, cambiar roles o desactivar accesos, pide autorización al administrador. El operador no ve controles destructivos ni mutadores de permisos.</span>
      </div>
    </section>
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
