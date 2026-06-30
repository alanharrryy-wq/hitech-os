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
  if (source === "computed") return "auto";
  return "fallback";
}

function disabledReason(catalog: DropdownCatalog) {
  if (catalog.source === "database") return "";
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

  if (!catalogs.length) return null;

  return (
    <section
      className={styles.dock}
      data-prisma-component="SmartDropdownDock"
      data-prisma-route={currentPath}
      data-prisma-dropdown-version={dropdownContract.version}
      aria-label={`${title} de ${contract.humanName}`}
    >
      <div className={styles.header}>
        <div>
          <div className={styles.kicker}>automatización funcional</div>
          <h2>{title}</h2>
          <p>
            Filtra por catálogos reales cuando existen en DB y usa fallback honesto cuando la superficie aún no tiene datos vivos.
          </p>
        </div>
        <div className={styles.healthPill}>
          <strong>{dbBackedCount}/{catalogs.length}</strong>
          <span>DB-backed</span>
        </div>
      </div>

      <form className={styles.form} action={currentPath} method="get">
        <input type="hidden" name="pcDropdowns" value="1" />

        <label className={styles.searchBox}>
          <span>Buscar en esta superficie</span>
          <input
            name="q"
            placeholder="Folio, producto, proveedor, equipo, sucursal..."
            aria-label={`Buscar en ${contract.humanName}`}
          />
        </label>

        <div className={styles.grid}>
          {catalogs.map((catalog) => {
            const reason = disabledReason(catalog);
            return (
              <label key={catalog.key} className={styles.selectCard}>
                <span className={styles.labelRow}>
                  <strong>{catalog.label}</strong>
                  <em>{sourceLabel(catalog.source)}</em>
                </span>
                <select name={catalog.key} defaultValue="" aria-label={catalog.label}>
                  <option value="">Todos</option>
                  {catalog.options.slice(0, 80).map((option) => (
                    <option key={`${catalog.key}-${option.value}`} value={option.value} disabled={option.disabled}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <small>{reason || catalog.usage.join(" · ")}</small>
                {renderQuickCreate(catalog)}
              </label>
            );
          })}
        </div>

        <div className={styles.actions}>
          <button type="submit">Aplicar filtros</button>
          <a href={currentPath}>Limpiar</a>
          <details>
            <summary>Ver comportamiento</summary>
            <ul>
              {dropdownContract.behavior.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </details>
        </div>
      </form>
    </section>
  );
}
