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
    <section className={styles.card} data-prisma-client-final="users-readonly"
      data-surface="tablet"
      data-screen="settings"
      data-zone="pos"
      data-panel="local-users-roles-panel"
      data-target="local-users-roles-panel-panel-37"
      data-kind="panel"
      data-role="revenue-core"
    >
      <div className={styles.sectionHeader}
        data-surface="tablet"
        data-screen="settings"
        data-zone="pos"
        data-panel="local-users-roles-panel"
        data-target="local-users-roles-panel-panel-38"
        data-kind="panel"
        data-role="revenue-core"
      >
        <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-div-1" data-kind="panel" data-role="container">
          <p className={styles.eyebrow}
            data-surface="tablet"
            data-screen="settings"
            data-zone="pos"
            data-panel="local-users-roles-panel"
            data-target="local-users-roles-panel-panel-40"
            data-kind="panel"
            data-role="revenue-core"
          >Usuarios y permisos</p>
          <h2 className={styles.sectionTitle}
            data-surface="tablet"
            data-screen="settings"
            data-zone="pos"
            data-panel="local-users-roles-panel"
            data-target="local-users-roles-panel-panel-41"
            data-kind="panel"
            data-role="revenue-core"
          >Consulta de acceso</h2>
          <p className={styles.copy}
            data-surface="tablet"
            data-screen="settings"
            data-zone="pos"
            data-panel="local-users-roles-panel"
            data-target="local-users-roles-panel-panel-42"
            data-kind="panel"
            data-role="revenue-core"
          >
            Esta vista explica quién está operando, qué permisos tiene y qué acciones requieren autorización. La edición de usuarios queda fuera del flujo de operador.
          </p>
        </div>
        <span className={styles.readonlyPill}
          data-surface="tablet"
          data-screen="settings"
          data-zone="pos"
          data-panel="local-users-roles-panel"
          data-target="local-users-roles-panel-badge-46"
          data-kind="badge"
          data-role="revenue-core"
        >Sólo lectura</span>
      </div>

      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-div-2" data-kind="panel" data-role="container" className={styles.metricGrid}>
        <Metric label="Usuario actual" value={currentUser?.displayName ?? "Sin usuario activo"} />
        <Metric label="Rol" value={currentUser ? userPrimaryRole(currentUser) : "Sin rol"} />
        <Metric label="Estado" value={currentUser ? statusCopy(currentUser.status) : "Sin acceso activo"} />
        <Metric label="Roles visibles" value={String(initialSnapshot.roles.length)} />
      </div>

      <div className={styles.warningList} aria-label="Usuarios visibles"
        data-surface="tablet"
        data-screen="settings"
        data-zone="pos"
        data-panel="local-users-roles-panel"
        data-target="local-users-roles-panel-usuarios-visibles-56"
        data-kind="badge"
        data-role="state-feedback"
      >
        {initialSnapshot.users.length ? initialSnapshot.users.map((user: SnapshotUser) => (
          <article key={user.id} className={styles.metric}
            data-surface="tablet"
            data-screen="settings"
            data-zone="pos"
            data-panel="local-users-roles-panel"
            data-target="local-users-roles-panel-panel-58"
            data-kind="panel"
            data-role="revenue-core"
          >
            <span className={styles.metricLabel}
              data-surface="tablet"
              data-screen="settings"
              data-zone="pos"
              data-panel="local-users-roles-panel"
              data-target="local-users-roles-panel-panel-59"
              data-kind="panel"
              data-role="revenue-core"
            >{statusCopy(user.status)}</span>
            <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-strong-3" data-kind="panel" data-role="panel">{user.displayName}</strong>
            <p className={styles.helper}
              data-surface="tablet"
              data-screen="settings"
              data-zone="pos"
              data-panel="local-users-roles-panel"
              data-target="local-users-roles-panel-panel-61"
              data-kind="panel"
              data-role="revenue-core"
            >
              {userPrimaryRole(user)}. {user.status === "ACTIVE" ? "Puede operar dentro de sus permisos." : "No puede operar hasta autorización administrativa."}
            </p>
          </article>
        )) : (
          <div className={styles.warning}
            data-surface="tablet"
            data-screen="settings"
            data-zone="pos"
            data-panel="local-users-roles-panel"
            data-target="local-users-roles-panel-badge-66"
            data-kind="badge"
            data-role="state-feedback"
          >No hay usuarios operativos registrados para mostrar.</div>
        )}
      </div>

      <div className={styles.featureGroups} aria-label="Permisos por rol"
        data-surface="tablet"
        data-screen="settings"
        data-zone="pos"
        data-panel="local-users-roles-panel"
        data-target="local-users-roles-panel-permisos-por-rol-70"
        data-kind="panel"
        data-role="revenue-core"
      >
        {initialSnapshot.roles.map((role: SnapshotRole) => (
          <details key={role.code} className={styles.featureGroup}>
            <summary>
              <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-span-4" data-kind="panel" data-role="panel">{role.label}</span>
              <em data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-em-5" data-kind="panel" data-role="panel">{role.permissions.length} permiso(s)</em>
            </summary>
            <p className={styles.helper}
              data-surface="tablet"
              data-screen="settings"
              data-zone="pos"
              data-panel="local-users-roles-panel"
              data-target="local-users-roles-panel-panel-77"
              data-kind="panel"
              data-role="revenue-core"
            >{role.description ?? "Rol operativo de Tablet."}</p>
            <div className={styles.featureList}
              data-surface="tablet"
              data-screen="settings"
              data-zone="pos"
              data-panel="local-users-roles-panel"
              data-target="local-users-roles-panel-panel-78"
              data-kind="panel"
              data-role="revenue-core"
            >
              {role.permissions.map((permission) => (
                <article key={`${role.code}-${permission}`} className={styles.featureItem}
                  data-surface="tablet"
                  data-screen="settings"
                  data-zone="pos"
                  data-panel="local-users-roles-panel"
                  data-target="local-users-roles-panel-cart-80"
                  data-kind="cart"
                  data-role="revenue-core"
                >
                  <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-div-6" data-kind="panel" data-role="container">
                    <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-strong-7" data-kind="panel" data-role="panel">{permission}</strong>
                    <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-span-8" data-kind="panel" data-role="panel">{permissionCopy(permission)}</span>
                  </div>
                  <span className={styles.featurePill}
                    data-surface="tablet"
                    data-screen="settings"
                    data-zone="pos"
                    data-panel="local-users-roles-panel"
                    data-target="local-users-roles-panel-badge-85"
                    data-kind="badge"
                    data-role="revenue-core"
                  >Visible</span>
                </article>
              ))}
            </div>
          </details>
        ))}
      </div>

      <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-div-9" data-kind="panel" data-role="container" className={styles.operatorNotice}>
        <strong data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-strong-10" data-kind="panel" data-role="panel">Sin edición en Tablet final</strong>
        <span data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-span-11" data-kind="panel" data-role="panel">Para crear usuarios, cambiar roles o desactivar accesos, pide autorización al administrador. El operador no ve controles destructivos ni mutadores de permisos.</span>
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div data-surface="tablet" data-screen="pos" data-zone="unknown_group" data-panel="local_users_roles_panel" data-target="local-users-roles-panel-div-12" data-kind="panel" data-role="container" className={styles.metric}>
      <span className={styles.metricLabel}
        data-surface="tablet"
        data-screen="settings"
        data-zone="pos"
        data-panel="local-users-roles-panel"
        data-target="local-users-roles-panel-panel-104"
        data-kind="panel"
        data-role="revenue-core"
      >{label}</span>
      <span className={styles.metricValue}
        data-surface="tablet"
        data-screen="settings"
        data-zone="pos"
        data-panel="local-users-roles-panel"
        data-target="local-users-roles-panel-panel-105"
        data-kind="panel"
        data-role="revenue-core"
      >{value}</span>
    </div>
  );
}
