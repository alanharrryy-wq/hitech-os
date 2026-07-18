import { getPcDropdownContract } from "@/server/services/pc-data-mode-contract.service";
import { getPcRouteContract } from "@/uiux/decision-model";
import styles from "./smart-dropdown-dock.module.css";

type DropdownContract = Awaited<ReturnType<typeof getPcDropdownContract>>;
type DropdownCatalog = DropdownContract["dropdowns"][number];

const GROUP_CATALOG_KEYS: Record<string, string[]> = {
  hoy: ["branches", "periods", "users", "severity", "operationalStatus"],
  "ventas-caja": ["branches", "devices", "users", "periods", "paymentMethods", "operationalStatus"],
  inventario: ["products", "categories", "suppliers", "stockStatus", "units", "taxRates", "adjustmentReasons"],
  compras: ["suppliers", "products", "purchaseTypes", "purchaseStatus", "paymentTerms", "receivingActions", "differenceReasons"],
  proveedores: ["suppliers", "supplierTypes", "supplierStatus", "supplierCategories", "paymentTerms", "riskLevels", "products"],
  sincronizacion: ["devices", "syncTypes", "syncStatus", "severity", "syncActions"],
  reportes: ["reportTypes", "periods", "branches", "exportFormats"],
  analisis: ["metricTypes", "comparisonModes", "groupingModes", "branches", "periods"],
  sistema: ["systemAreas", "severity", "operationalStatus", "devices"],
  configuracion: ["roles", "permissions", "branches", "currency", "timezones"],
  ayuda: ["systemAreas", "operationalStatus"]
};

function catalogByKey(catalogs: DropdownCatalog[]) {
  return new Map(catalogs.map((catalog) => [catalog.key, catalog]));
}

function routeCatalogKeys(currentPath: string, group: string) {
  if (currentPath === "/sales-control" || currentPath === "/cash-sessions" || currentPath === "/metricas-dia") return GROUP_CATALOG_KEYS["ventas-caja"];
  if (currentPath === "/devices") return GROUP_CATALOG_KEYS.sistema;
  if (currentPath === "/proveedores") return GROUP_CATALOG_KEYS.proveedores;
  return GROUP_CATALOG_KEYS[group] ?? GROUP_CATALOG_KEYS.sistema;
}

function sourceLabel(source: string) {
  if (source === "database") return "DB";
  if (source === "computed") return "Auto";
  return "Respaldo";
}

function disabledReason(catalog: DropdownCatalog) {
  if (catalog.source === "database") return "Catálogo conectado a datos reales.";
  if (catalog.options.length === 0) return "No hay datos disponibles todavía.";
  return "Catálogo operativo de respaldo hasta conectar datos reales.";
}

function renderQuickCreate(catalog: DropdownCatalog) {
  const quickCreate = catalog.quickCreate;
  if (!quickCreate) return null;

  return (
    <a className={styles.quickCreateLink} href={quickCreate.href}>
      {quickCreate.label}
    </a>
  );
}

export async function SmartDropdownDock({
  currentPath,
  title = "Filtros inteligentes"
}: {
  currentPath: string;
  title?: string;
}) {
  const contract = getPcRouteContract(currentPath);
  const dropdownContract = await getPcDropdownContract();
  const byKey = catalogByKey(dropdownContract.dropdowns);
  const keys = routeCatalogKeys(currentPath, contract.group);
  const catalogs = keys.map((key) => byKey.get(key)).filter((catalog): catalog is DropdownCatalog => Boolean(catalog));
  const dbBackedCount = catalogs.filter((catalog) => catalog.source === "database").length;
  const summaryId = `pc-dropdown-summary-${contract.group.replace(/[^a-z0-9-]+/gi, "-").toLowerCase()}`;

  if (!catalogs.length) return null;

  return (
    <details
      className={styles.dock}
      data-prisma-component="SmartDropdownDock"
      data-prisma-route={currentPath}
      data-prisma-dropdown-version={dropdownContract.version}
      open
    >
      <summary className={styles.summary} id={summaryId}>
        <span className={styles.summaryCopy}>
          <span className={styles.kicker}>Filtros de la superficie</span>
          <span className={styles.title} role="heading" aria-level={2}>{title}</span>
          <span className={styles.summaryDescription}>Búsqueda y catálogos sin ocultar el origen de los datos.</span>
        </span>
        <span className={styles.healthPill} aria-label={`${dbBackedCount} de ${catalogs.length} catálogos conectados a base de datos`}>
          <strong>{dbBackedCount}/{catalogs.length}</strong>
          <span>DB</span>
        </span>
      </summary>

      <form className={styles.form} action={currentPath} method="get" aria-labelledby={summaryId}>
        <input type="hidden" name="pcDropdowns" value="1" />

        <label className={styles.searchBox}>
          <span>Buscar en {contract.humanName}</span>
          <input
            name="q"
            type="search"
            placeholder="Folio, producto, proveedor, equipo o sucursal"
            aria-label={`Buscar en ${contract.humanName}`}
            autoComplete="off"
          />
        </label>

        <div className={styles.grid}>
          {catalogs.map((catalog) => {
            const reason = disabledReason(catalog);
            const helpId = `pc-dropdown-help-${catalog.key.replace(/[^a-z0-9-]+/gi, "-").toLowerCase()}`;
            return (
              <label key={catalog.key} className={styles.selectCard}>
                <span className={styles.labelRow}>
                  <strong>{catalog.label}</strong>
                  <em data-source={catalog.source}>{sourceLabel(catalog.source)}</em>
                </span>
                <select name={catalog.key} defaultValue="" aria-label={catalog.label} aria-describedby={helpId}>
                  <option value="">Todos</option>
                  {catalog.options.slice(0, 80).map((option) => (
                    <option key={`${catalog.key}-${option.value}`} value={option.value} disabled={option.disabled}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <small id={helpId}>{reason || catalog.usage.join(" · ")}</small>
                {renderQuickCreate(catalog)}
              </label>
            );
          })}
        </div>

        <div className={styles.actions}>
          <button type="submit">Aplicar filtros</button>
          <a href={currentPath}>Limpiar</a>
          <details className={styles.behaviorDetails}>
            <summary>Cómo se comportan</summary>
            <ul>
              {dropdownContract.behavior.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </details>
        </div>
      </form>
    </details>
  );
}
