# ATLAS PC VISUAL - Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Alcance visual

Este documento registra solo la capa visual confirmada dentro del ZIP para PC Backoffice. No declara propiedad PC sobre `shared-ui/prisma`, `styles/prisma-visual-os` ni configuraciones globales de Visual OS. Esas piezas se tratan como dependencias externas.

## Entry points visuales confirmados

| Tipo | Archivo | Rol |
|---|---|---|
| Layout raíz | `products/pc/app/app/layout.tsx` | Declara shell HTML, metadata y data attributes de Visual OS PC |
| CSS global | `products/pc/app/app/globals.css` | Importa tokens/componentes Prisma compartidos y estilos PC |
| Binding Visual OS PC | `products/pc/app/app/prisma-visual-os-pc-binding.css` | Capa de adaptación PC hacia Visual OS |
| Suppliers CSS | `products/pc/app/app/suppliers.css` | Estilos específicos de proveedores |
| Suppliers UX v08 | `products/pc/app/app/suppliers-ux-v08.css` | Refinamiento visual/UX de proveedores |
| App shell | `products/pc/app/components/layout/app-shell.tsx` | Layout lateral/topbar/contenido de backoffice |

## Data attributes confirmados

`layout.tsx` confirma bindings visuales en HTML/body para PC:

| Attribute | Valor confirmado | Interpretación |
|---|---|---|
| `data-prisma-surface` | `pc-backoffice` | PC como superficie administrativa |
| `data-prisma-visual-os` | `PC_DENSE_ADMIN` | Densidad visual administrativa |
| `data-prisma-vos-binding` | `00J` | Binding/versionamiento visual PC detectado |
| `data-theme-default` | `prisma-light` | Tema inicial confirmado |

## Dependencias visuales externas

| Dependencia | Evidencia en ZIP | Clasificación |
|---|---|---|
| `shared-ui/prisma/tokens/prisma-theme.css` | import en `app/globals.css` | Externa compartida |
| `shared-ui/prisma/components/prisma-components.css` | import en `app/globals.css` | Externa compartida |
| `shared-ui/prisma/visual-os/prisma-visual-os.tokens.css` | import en `app/prisma-visual-os-pc-binding.css` | Externa compartida |
| `styles/prisma-visual-os/prisma-visual-layers.css` | import en binding PC | Externa/global |
| `styles/prisma-visual-os/prisma-visual-components.css` | import en binding PC | Externa/global |
| `styles/prisma-visual-os/prisma-visual-controls.css` | import en binding PC | Externa/global |

Regla: PC consume estas capas, pero no se documentan como propiedad PC.

## Composición visual PC

### Shell administrativo

`components/layout/app-shell.tsx` aparece como núcleo de navegación y composición visual. Las páginas de backoffice lo importan para mantener navegación, encabezados y layout consistente.

Responsabilidades confirmadas:

- Renderizar navegación administrativa.
- Conectar módulos del registry con navegación visible.
- Integrar marca/assets del producto.
- Proveer contenedor común para pantallas de backoffice.

### Componentes UI confirmados

| Familia | Archivos representativos | Uso |
|---|---|---|
| Cards/secciones | `components/ui/section-card.tsx`, `components/ui/bulk-action-card.tsx` | Resúmenes, bloques operativos y acciones masivas |
| Tablas/listas | componentes UI de tablas I11 y proveedores | Superficies densas de backoffice |
| Landing | `components/landing/**` | Comunicación de producto/ecosistema |
| Backoffice | `components/backoffice/**` | Vistas administrativas específicas |
| Catálogo/inventario/operación | `components/catalog/**`, `components/inventory/**`, `components/operations/**` | UI por dominio |
| Sync | `components/sync/**` | Estado, cola, rejected/conflicts |
| Suppliers | `components/suppliers/**` | Proveedores, compras, recepción y reportes |
| License | `components/license/**` | Gates/licenciamiento visible |

## Assets públicos confirmados

El snapshot contiene 6 assets públicos reales en `products/pc/app/public/**`.

| Asset | Estado |
|---|---|
| `public/brand/prisma-logo-main.png` | Presente |
| `public/brand/prisma-mark.svg` | Presente |
| `public/landing/prisma-ecosystem.svg` | Presente |
| `public/landing/prisma-pc-dashboard.svg` | Presente |
| `public/landing/prisma-tablet-pos.svg` | Presente |
| `public/landing/prisma-system-map.svg` | Presente |

## Asset manifest y huecos visuales

`analysis/pc_public_asset_manifest.json` lista 10 assets, pero solo 6 están presentes en el snapshot. Faltan 4 assets que no deben inventarse:

| Asset faltante | Riesgo |
|---|---|
| `public/brand/prisma-logo-official.png` | Marca puede romperse si el código lo referencia |
| `public/landing/prisma-multisucursal-control-total.png` | Imagen landing ausente |
| `public/landing/prisma-pc-controla-operacion.png` | Imagen landing ausente |
| `public/landing/prisma-pos-vende-con-orden.png` | Imagen landing ausente |

Ronda 2 corrige este hallazgo documentándolo como pendiente, sin crear assets falsos.

## Visual OS global en contexto

El ZIP incluye contexto global de Visual OS en `global_context/config/prisma-visual-os/**` y `global_context/docs/design/**`. Ese contexto ayuda a entender el contrato visual, pero no debe copiarse como implementación PC. Para PC solo se confirma:

- Binding local `prisma-visual-os-pc-binding.css`.
- Imports hacia capas globales.
- Data attributes PC.
- CSS específico de PC y suppliers.

## Riesgos visuales

| Riesgo | Estado |
|---|---|
| Dependencias visuales externas ausentes en snapshot parcial | Pendiente de repo completo |
| Assets faltantes respecto al manifest | Pendiente de corrección o confirmación |
| Validación visual final | Pendiente de ejecutar en repo completo |
| Mobile/Tablet visual ownership | Fuera de alcance, no tocado |

## Verificación visual detectada

Herramientas de `tools/**` incluyen verificadores visuales y smoke checks. La ejecución completa no se puede confirmar con el ZIP aislado por dependencias externas faltantes.

## Conclusión visual

PC posee la composición visual de backoffice: shell, páginas, componentes, CSS local y bindings de superficie. No posee los tokens globales, Shared UI ni Visual OS global. La entrega de staging conserva esa frontera para evitar que el atlas se vuelva una barda pintada encima de la casa del vecino.