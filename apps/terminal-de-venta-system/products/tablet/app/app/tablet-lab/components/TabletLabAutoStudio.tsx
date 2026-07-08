"use client";

import { useEffect, useMemo, useState, type CSSProperties, type ReactNode } from "react";
import styles from "../TabletLabCapsule.module.css";

type PresetTone = "neutral" | "cyan" | "mint" | "amber" | "coral" | "lavender" | "blue";
type PresetRecord = {
  id: string;
  name: string;
  basePreset: string;
  section: string;
  widgetGroup: string;
  effectGroup: string;
  viewport: string;
  stateMode: string;
  tone: PresetTone;
  glassAlpha: number;
  blur: number;
  saturate: number;
  contrast: number;
  tintStrength: number;
  glow: number;
  radius: number;
  shadow: number;
  density: number;
  columns: number;
  backgroundMode: string;
  tabctl7ModelVersion?: string;
  tabctl7Layer?: string;
  tabctl7Role?: string;
  tabctl7Part?: string;
  tabctl7Kind?: string;
  tabctl7Change?: string;
  tabctl7Material?: string;
  tabctl7MaterialLabel?: string;
  tabctl7ColorMode?: string;
  tabctl7Scope?: string;
  tabctl7Inheritance?: string;
  tabctl7Controls?: string[];
  tabctl7ZeroPolicy?: string;
  createdAt: string;
  updatedAt: string;
};

type Knobs = {
  glassAlpha: number;
  blur: number;
  saturate: number;
  contrast: number;
  frostVeil: number;
  borderAlpha: number;
  innerHighlight: number;
  edgeShine: number;
  specularGlow: number;
  tintStrength: number;
  gradientAngle: number;
  accentStrength: number;
  warmth: number;
  coolness: number;
  mutedInk: number;
  elevation: number;
  shadow: number;
  contactShadow: number;
  layerDistance: number;
  stackOffset: number;
  panelLift: number;
  modalDepth: number;
  hoverLift: number;
  pressDepth: number;
  activeGlow: number;
  selectionHalo: number;
  motionIntensity: number;
  parallaxTiny: number;
  reducedMotion: number;
  backgroundFreeze: number;
  backgroundScale: number;
  backgroundBlur: number;
  atmosphericVeil: number;
  vignetteSoft: number;
  lightLeak: number;
  horizonPosition: number;
  parallaxMax: number;
  panelGap: number;
  cardDensity: number;
  rowHeight: number;
  chipCompression: number;
  toolbarCompactness: number;
  gridColumns: number;
  railWidth: number;
  headerHeight: number;
  textGlow: number;
  inkContrast: number;
  mutedContrast: number;
  labelTracking: number;
  numericEmphasis: number;
  microcopyOpacity: number;
  headingWeight: number;
  tableTone: number;
  columnPressure: number;
  headerStickiness: number;
  zebraSoftness: number;
  dividerAlpha: number;
  rowHoverGlow: number;
  actionColumnVisibility: number;
  buttonHeight: number;
  buttonRadius: number;
  buttonGlow: number;
  borderBrightness: number;
  pressInset: number;
  disabledFrost: number;
  dangerWarmth: number;
  primarySaturation: number;
  heroCompactness: number;
  cardTranslucency: number;
  railTranslucency: number;
  modalGlassStrength: number;
  warningToneStrength: number;
  inspectorDensity: number;
  metricEmphasis: number;
};

/* TABCTL7V2_SUPREMO_MODEL_START */
const TABCTL7V2_MODEL_VERSION = "tabctl7v2-supreme-0707-1918-rollback-guard";

type Tabctl7RoleKind = "panel" | "text" | "numericText" | "button" | "buttonText" | "chip" | "input" | "table" | "tableCell" | "background" | "icon" | "modal" | "toast" | "chart" | "nav" | "dock" | "skeleton" | "qr" | "timeline" | "matrix";
type Tabctl7RoleSpec = { role: string; part: string; kind: Tabctl7RoleKind; states: string[]; changeTypes: string[]; controls: Array<keyof Knobs>; help: string };
type Tabctl7LayerSpec = { layer: string; roles: Tabctl7RoleSpec[] };
type Tabctl7GroupSpec = { group: string; components: string[]; layers: Tabctl7LayerSpec[]; presets: string[] };
type Tabctl7MaterialSpec = { id: string; label: string; description: string; alpha: number; frost: number; blurDelta: number; glow: number; border: number };
type Tabctl7ControlSpec = { key: keyof Knobs; label: string; effectGroup: string; kinds: Tabctl7RoleKind[]; changeTypes: string[]; states: string[]; zeroOff?: boolean; help: string };

const tabctl7AllStates = ["Default", "Hover", "Focus", "Focus visible", "Pressed", "Selected", "Disabled", "Loading", "Empty", "Success", "Warning", "Danger", "Critical", "Offline", "Dragging", "Dirty", "Locked", "Expanded", "Collapsed", "Error"];
const tabctl7ChangeTypes = ["Material", "Color", "Texto", "Número/precio", "Botón", "Borde y luz", "Sombra y profundidad", "Forma y espacio", "Fondo", "Tabla", "Estado", "Movimiento", "Accesibilidad", "Override local"];
const tabctl7ColorModes = ["Solid token", "2-color gradient", "3-color gradient", "State color mix", "Semantic token", "Auto contrast", "Muted premium", "Neon accent", "Danger semantic", "Success semantic", "Monochrome ink"];
const tabctl7Scopes = ["Sólo esta parte", "Todos los roles de este tipo", "Toda esta capa", "Todo este componente", "Todo este grupo visual", "Preset completo", "Sólo estado actual", "Todos los estados compatibles"];
const tabctl7InheritanceModes = ["Heredar del padre", "Override local", "Copiar estilo", "Pegar estilo", "Reset rol", "Reset capa", "Bloquear rol", "Liberar rol"];
const tabctl7Materials: Tabctl7MaterialSpec[] = [
  { id: "frosted-glass", label: "Frosted glass", description: "Vidrio lechoso balanceado", alpha: 0.24, frost: 0.34, blurDelta: 0, glow: 0.16, border: 0.28 },
  { id: "liquid-glass", label: "Liquid glass", description: "Gota con borde óptico y brillo vivo", alpha: 0.18, frost: 0.18, blurDelta: 4, glow: 0.36, border: 0.44 },
  { id: "neon-glass", label: "Neon glass", description: "Glass nocturno con halo", alpha: 0.16, frost: 0.12, blurDelta: 2, glow: 0.58, border: 0.38 },
  { id: "ceramic-soft", label: "Ceramic soft", description: "Más mate que transparente", alpha: 0.42, frost: 0.52, blurDelta: -6, glow: 0.08, border: 0.22 },
  { id: "paper-matte", label: "Paper matte", description: "Lectura premium", alpha: 0.62, frost: 0.68, blurDelta: -10, glow: 0.04, border: 0.16 },
  { id: "brushed-metal", label: "Brushed metal", description: "Metal cepillado", alpha: 0.30, frost: 0.24, blurDelta: -2, glow: 0.20, border: 0.36 },
  { id: "carbon-satin", label: "Carbon satin", description: "Carbono satinado", alpha: 0.22, frost: 0.16, blurDelta: -4, glow: 0.18, border: 0.30 },
  { id: "holographic-veil", label: "Holographic veil", description: "Velo tornasol", alpha: 0.20, frost: 0.22, blurDelta: 2, glow: 0.42, border: 0.34 },
  { id: "ghost-surface", label: "Ghost surface", description: "Casi invisible", alpha: 0.08, frost: 0.06, blurDelta: -8, glow: 0.00, border: 0.10 },
  { id: "danger-glass", label: "Danger glass", description: "Coral de riesgo", alpha: 0.26, frost: 0.28, blurDelta: 0, glow: 0.30, border: 0.42 },
  { id: "warm-acrylic", label: "Warm acrylic", description: "Acrílico cálido", alpha: 0.36, frost: 0.40, blurDelta: -2, glow: 0.22, border: 0.26 },
  { id: "cold-acrylic", label: "Cold acrylic", description: "Acrílico frío", alpha: 0.32, frost: 0.36, blurDelta: 0, glow: 0.24, border: 0.28 },
  { id: "ink-plate", label: "Ink plate", description: "Placa oscura legible", alpha: 0.74, frost: 0.14, blurDelta: -16, glow: 0.08, border: 0.18 },
  { id: "soft-plastic", label: "Soft plastic", description: "Plástico táctil", alpha: 0.44, frost: 0.46, blurDelta: -6, glow: 0.10, border: 0.20 },
];
const role = (roleName: string, part: string, kind: Tabctl7RoleKind, controls: Array<keyof Knobs>, states: string[], changeTypes: string[], help: string): Tabctl7RoleSpec => ({ role: roleName, part, kind, controls, states, changeTypes, help });
const commonPanelRoles = [role("Superficie primaria", "base", "panel", ["glassAlpha","blur","frostVeil","borderAlpha","edgeShine","shadow","buttonRadius"], ["Default","Hover","Selected","Disabled"], ["Material","Borde y luz","Sombra y profundidad","Forma y espacio","Estado"], "Superficie con material seleccionable y cero-apaga-real."), role("Heading text", "heading", "text", ["inkContrast","headingWeight","textGlow","labelTracking"], ["Default","Hover","Selected"], ["Texto","Color","Estado"], "Texto principal independiente de panel."), role("Metric / number", "number", "numericText", ["numericEmphasis","inkContrast","textGlow"], ["Default","Success","Warning","Danger"], ["Número/precio","Color","Estado"], "Número, precio o total con énfasis propio.")];
const tabctl7Taxonomy: Record<string, Tabctl7GroupSpec> = {
  "Panel Set": { group: "Panel Set", components: ["HeroPanel", "MetricPanel", "CommandPanel", "WarningPanel", "InspectorPanel"], presets: ["Hero limpio", "Rail frosted", "Warning suave"], layers: [{ layer: "Canvas", roles: [role("Fondo atmosférico", "background", "background", ["backgroundBlur","backgroundScale","atmosphericVeil","vignetteSoft","lightLeak"], ["Default","Loading"], ["Fondo","Color","Accesibilidad"], "Fondo ambiental del laboratorio.")] }, { layer: "Panel shell", roles: commonPanelRoles }]},
  "POS Product Set": { group: "POS Product Set", components: ["ProductCard", "ImageWell", "PriceBlock", "BadgeLayer", "QuickAdd"], presets: ["Producto claro premium", "Promo glow", "Foto protagonista", "Bajo stock elegante"], layers: [{ layer: "Canvas", roles: [role("Fondo atmosférico", "canvas", "background", ["backgroundBlur","backgroundScale","atmosphericVeil","vignetteSoft","lightLeak","horizonPosition"], ["Default","Loading"], ["Fondo","Color"], "Ambiente detrás de cards.")] }, { layer: "Card base", roles: commonPanelRoles }, { layer: "Image area", roles: [role("Panel de imagen", "image-shell", "panel", ["glassAlpha","blur","gradientAngle","accentStrength","edgeShine"], ["Default","Hover","Loading"], ["Material","Fondo","Borde y luz"], "Zona de imagen o placeholder."), role("Overlay label", "label", "text", ["inkContrast","labelTracking","textGlow"], ["Default","Hover"], ["Texto","Color"], "Etiqueta sobre imagen.")] }, { layer: "Price zone", roles: [role("Price number", "price", "numericText", ["numericEmphasis","inkContrast","textGlow","labelTracking"], ["Default","Promo","Selected"], ["Número/precio","Color","Estado"], "Precio con glow propio."), role("Currency symbol", "currency", "numericText", ["numericEmphasis","mutedContrast","microcopyOpacity"], ["Default","Muted"], ["Número/precio","Texto"], "Símbolo y centavos.")] }, { layer: "Badges layer", roles: [role("Stock badge", "stock", "chip", ["tintStrength","borderAlpha","buttonGlow","chipCompression"], ["Success","Warning","Danger"], ["Estado","Color","Borde y luz"], "Inventario por estado."), role("Promo badge", "promo", "chip", ["accentStrength","edgeShine","activeGlow","selectionHalo"], ["Default","Promo","Selected"], ["Estado","Color","Borde y luz"], "Promo semántica.")] }, { layer: "Action area", roles: [role("Add button", "cta", "button", ["buttonHeight","buttonRadius","buttonGlow","pressDepth","disabledFrost","primarySaturation"], ["Default","Hover","Pressed","Disabled","Loading"], ["Botón","Estado","Movimiento","Forma y espacio"], "CTA táctil del producto."), role("Add button text", "cta-label", "buttonText", ["inkContrast","headingWeight","labelTracking","textGlow"], ["Default","Hover","Disabled"], ["Texto","Color"], "Texto del CTA separado del fondo.")] }]},
  "Checkout Rail Set": { group: "Checkout Rail Set", components: ["RailShell", "CartLine", "Totals", "TenderPills", "ChargeActions"], presets: ["Rail sólido", "Pago hero", "Carrito compacto", "Danger suave"], layers: [{ layer: "Rail shell", roles: [role("Panel lateral", "shell", "panel", ["railWidth","railTranslucency","blur","borderAlpha","shadow"], ["Default","Expanded","Offline"], ["Material","Forma y espacio","Sombra y profundidad"], "Rail más sólido que card.")] }, { layer: "Cart line", roles: [role("Row surface", "row", "panel", ["glassAlpha","rowHeight","dividerAlpha","rowHoverGlow"], ["Default","Hover","Selected"], ["Material","Tabla","Estado"], "Línea de carrito."), role("Product name", "row-name", "text", ["inkContrast","mutedContrast","microcopyOpacity"], ["Default","Selected"], ["Texto","Color"], "Nombre de producto."), role("Line total", "line-total", "numericText", ["numericEmphasis","textGlow","inkContrast"], ["Default","Dirty","Selected"], ["Número/precio","Estado"], "Total por línea.")] }, { layer: "Actions", roles: [role("Charge button", "cta", "button", ["buttonHeight","buttonGlow","activeGlow","pressDepth","primarySaturation"], ["Default","Hover","Pressed","Loading","Disabled"], ["Botón","Estado","Movimiento"], "CTA de cobro."), role("Void button", "danger", "button", ["dangerWarmth","disabledFrost","borderAlpha","pressDepth"], ["Default","Hover","Danger","Disabled"], ["Botón","Estado","Color"], "Botón peligroso controlado.")] }]},
  "Turno/Caja Set": { group: "Turno/Caja Set", components: ["StatusShell", "CommandArea", "CashMetrics", "AlertZone"], presets: ["Turno limpio", "Diferencia warning", "Cierre exitoso", "Caja crítica"], layers: [{ layer: "Status shell", roles: [role("Panel principal", "shell", "panel", ["glassAlpha","blur","borderAlpha","shadow"], ["Closed","Open","Counting"], ["Material","Estado"], "Superficie de estado."), role("Estado de caja", "state", "text", ["inkContrast","headingWeight","textGlow","warningToneStrength"], ["Closed","Open","Counting","Critical"], ["Texto","Estado","Color"], "Estado operativo visible.")] }, { layer: "Cash metrics", roles: [role("Expected cash", "cash", "numericText", ["numericEmphasis","inkContrast","textGlow"], ["Default","Balanced"], ["Número/precio","Color"], "Dinero esperado."), role("Difference number", "difference", "numericText", ["warningToneStrength","numericEmphasis","activeGlow"], ["Success","Warning","Critical"], ["Número/precio","Estado","Color"], "Diferencia con semántica dura.")] }]},
  "Table Set": { group: "Table Set", components: ["TableShell", "Toolbar", "Header", "Rows", "Footer"], presets: ["Key value", "Ops compact", "Ledger dense", "Exception red"], layers: [{ layer: "Table shell", roles: [role("Table surface", "shell", "table", ["tableTone","rowHeight","dividerAlpha","zebraSoftness","headerStickiness"], ["Default","Dense","Selected"], ["Tabla","Material","Estado"], "Tabla completa."), role("Toolbar search", "search", "input", ["glassAlpha","borderAlpha","inkContrast","buttonRadius"], ["Default","Focus","Disabled"], ["Texto","Borde y luz","Forma y espacio"], "Input de búsqueda.")] }, { layer: "Rows", roles: [role("Primary cell", "td-main", "tableCell", ["inkContrast","rowHeight","dividerAlpha"], ["Default","Hover","Selected"], ["Texto","Tabla","Estado"], "Celda primaria."), role("Numeric cell", "td-number", "numericText", ["numericEmphasis","inkContrast","columnPressure"], ["Default","Warning","Success"], ["Número/precio","Tabla"], "Celda numérica."), role("Action cell", "td-action", "button", ["buttonHeight","buttonRadius","buttonGlow","actionColumnVisibility"], ["Default","Hover","Disabled"], ["Botón","Tabla"], "Acción por fila.")] }]},
  "Button Set": { group: "Button Set", components: ["Primary", "Secondary", "Danger", "Ghost", "Icon", "Segmented", "Split"], presets: ["CTA hero", "Ghost calm", "Danger premium", "Segmented selected"], layers: [{ layer: "Button row", roles: [role("Grupo de botones", "row", "panel", ["panelGap","glassAlpha","borderAlpha"], ["Default","Dense"], ["Forma y espacio","Material"], "Agrupación mínima.")] }, { layer: "Actions", roles: [role("Primary action", "primary", "button", ["buttonHeight","buttonRadius","buttonGlow","pressDepth","primarySaturation"], ["Default","Hover","Pressed","Loading","Disabled"], ["Botón","Movimiento","Estado"], "Acción principal."), role("Danger action", "danger", "button", ["dangerWarmth","buttonGlow","pressDepth","disabledFrost"], ["Default","Hover","Pressed","Disabled"], ["Botón","Estado","Color"], "Acción destructiva elegante."), role("Button text", "label", "buttonText", ["inkContrast","headingWeight","labelTracking","textGlow"], ["Default","Hover","Disabled"], ["Texto","Color"], "Label del botón.")] }]},
  "Form Widgets": { group: "Form Widgets", components: ["Input", "MoneyInput", "Stepper", "Select", "Textarea", "Validation"], presets: ["Input focus", "Money premium", "Validation soft"], layers: [{ layer: "Input", roles: [role("Input surface", "surface", "input", ["glassAlpha","borderAlpha","buttonRadius","blur"], ["Default","Focus","Error","Disabled"], ["Material","Borde y luz","Estado"], "Superficie de input."), role("Placeholder", "placeholder", "text", ["mutedContrast","microcopyOpacity"], ["Default","Focus"], ["Texto","Accesibilidad"], "Placeholder legible."), role("Currency value", "money", "numericText", ["numericEmphasis","inkContrast","textGlow"], ["Default","Focus","Error"], ["Número/precio","Estado"], "Dinero con tabularidad.")] }]},
  "Modal States": { group: "Modal States", components: ["Backdrop", "ModalShell", "Title", "Body", "Actions"], presets: ["Confirm premium", "Danger modal", "Loading modal"], layers: [{ layer: "Modal backdrop", roles: [role("Backdrop veil", "backdrop", "background", ["backgroundBlur","atmosphericVeil","vignetteSoft"], ["Default","Loading"], ["Fondo","Accesibilidad"], "Fondo detrás del modal.")] }, { layer: "Modal shell", roles: [role("Modal panel", "shell", "modal", ["modalGlassStrength","blur","shadow","buttonRadius","borderAlpha"], ["Default","Danger","Loading"], ["Material","Estado","Sombra y profundidad"], "Panel modal."), role("Title", "title", "text", ["inkContrast","headingWeight","textGlow"], ["Default","Danger"], ["Texto","Color"], "Título modal."), role("Confirm button", "confirm", "button", ["buttonHeight","buttonGlow","primarySaturation","pressDepth"], ["Default","Hover","Pressed","Disabled"], ["Botón","Estado"], "Confirmación.")] }]},
  "Metric Widgets": { group: "Metric Widgets", components: ["MoneyMetric", "CountMetric", "StockMetric", "LicenseStatus", "SyncStatus"], presets: ["Metric hero", "Sync calm", "License alert"], layers: [{ layer: "Metric card", roles: [role("Metric surface", "shell", "panel", ["glassAlpha","blur","borderAlpha","shadow"], ["Default","Selected","Offline"], ["Material","Estado"], "Tarjeta de métrica."), role("Metric number", "number", "numericText", ["metricEmphasis","numericEmphasis","textGlow","inkContrast"], ["Default","Success","Warning","Danger"], ["Número/precio","Estado"], "Número hero."), role("Metric label", "label", "text", ["mutedContrast","labelTracking","microcopyOpacity"], ["Default"], ["Texto"], "Etiqueta de métrica.")] }]},
  "Navigation/Dock": { group: "Navigation/Dock", components: ["BottomDock", "NavItem", "ActiveIndicator", "Icon"], presets: ["Dock glass", "Active glow", "Compact nav"], layers: [{ layer: "Dock shell", roles: [role("Bottom dock", "dock", "dock", ["glassAlpha","blur","borderAlpha","shadow","panelGap"], ["Default","Expanded"], ["Material","Forma y espacio"], "Dock inferior preservado."), role("Nav item", "item", "nav", ["buttonHeight","buttonRadius","activeGlow","selectionHalo"], ["Default","Hover","Selected","Disabled"], ["Botón","Estado","Movimiento"], "Item de navegación."), role("Nav label", "label", "text", ["inkContrast","labelTracking","textGlow"], ["Default","Selected"], ["Texto","Estado"], "Texto de navegación.")] }]},
  "Carga mixta": { group: "Carga mixta", components: ["Panel", "Table", "ProductCard", "Checkout", "Buttons", "Chips", "Modal"], presets: ["Stress balanced", "Stress high contrast", "Stress neon"], layers: [{ layer: "Stress targets", roles: [role("Target seleccionado", "selected", "matrix", ["selectionHalo","activeGlow","borderAlpha","inspectorDensity"], ["Default","Selected","Hover"], ["Estado","Override local","Accesibilidad"], "Aplica sólo al target elegido."), role("Mixed numeric", "number", "numericText", ["numericEmphasis","textGlow","inkContrast"], ["Default","Warning"], ["Número/precio","Estado"], "Números del stress test."), role("Mixed action", "button", "button", ["buttonGlow","buttonRadius","pressDepth"], ["Default","Hover","Pressed"], ["Botón","Movimiento"], "Botones del stress test.")] }]},
  "Matriz de efectos": { group: "Matriz de efectos", components: ["ApplicabilityMatrix", "Coverage", "Rules"], presets: ["Debug matrix"], layers: [{ layer: "Coverage matrix", roles: [role("Aplicabilidad", "matrix", "matrix", ["inspectorDensity","rowHeight","dividerAlpha"], ["Default"], ["Tabla","Accesibilidad"], "Mapa de perilla contra target."), role("Risk rule", "rule", "text", ["inkContrast","warningToneStrength","microcopyOpacity"], ["Default","Warning"], ["Texto","Estado"], "Regla de riesgo visible.")] }]},
};
const tabctl7Controls: Tabctl7ControlSpec[] = [
  { key: "glassAlpha", label: "Material alpha", effectGroup: "Glass", kinds: ["panel","button","chip","input","modal","dock","table"], changeTypes: ["Material","Estado"], states: tabctl7AllStates, zeroOff: true, help: "Transparencia real." },
  { key: "blur", label: "Backdrop blur", effectGroup: "Glass", kinds: ["panel","button","chip","input","modal","dock","table","background"], changeTypes: ["Material","Fondo"], states: tabctl7AllStates, zeroOff: true, help: "Blur del fondo detrás." },
  { key: "frostVeil", label: "Frost veil", effectGroup: "Glass", kinds: ["panel","button","chip","input","modal","dock"], changeTypes: ["Material","Color"], states: tabctl7AllStates, zeroOff: true, help: "Velo lechoso." },
  { key: "borderAlpha", label: "Border alpha", effectGroup: "Glass", kinds: ["panel","button","chip","input","table","modal","dock"], changeTypes: ["Borde y luz","Estado","Accesibilidad"], states: tabctl7AllStates, zeroOff: true, help: "Borde real y focus." },
  { key: "edgeShine", label: "Edge shine", effectGroup: "Glass", kinds: ["panel","button","chip","modal","dock"], changeTypes: ["Borde y luz","Material"], states: tabctl7AllStates, zeroOff: true, help: "Brillo de borde." },
  { key: "tintStrength", label: "Tint strength", effectGroup: "Color", kinds: ["panel","button","chip","input","table","modal","background"], changeTypes: ["Color","Material","Estado"], states: tabctl7AllStates, help: "Intensidad del tinte." },
  { key: "gradientAngle", label: "Gradient angle", effectGroup: "Color", kinds: ["panel","button","chip","background","modal"], changeTypes: ["Color","Fondo"], states: tabctl7AllStates, help: "Ángulo de degradado." },
  { key: "accentStrength", label: "Accent strength", effectGroup: "Color", kinds: ["panel","button","chip","text","numericText","icon"], changeTypes: ["Color","Estado"], states: tabctl7AllStates, help: "Fuerza del acento." },
  { key: "inkContrast", label: "Ink contrast", effectGroup: "Typography", kinds: ["text","numericText","buttonText","tableCell","nav"], changeTypes: ["Texto","Número/precio","Accesibilidad","Color"], states: tabctl7AllStates, help: "Contraste visual." },
  { key: "headingWeight", label: "Heading weight", effectGroup: "Typography", kinds: ["text","buttonText","nav"], changeTypes: ["Texto","Botón"], states: tabctl7AllStates, help: "Peso del texto." },
  { key: "textGlow", label: "Text glow", effectGroup: "Typography", kinds: ["text","numericText","buttonText","nav","icon"], changeTypes: ["Texto","Número/precio","Estado"], states: tabctl7AllStates, zeroOff: true, help: "Glow del texto." },
  { key: "labelTracking", label: "Letter spacing", effectGroup: "Typography", kinds: ["text","buttonText","nav","tableCell"], changeTypes: ["Texto","Accesibilidad"], states: tabctl7AllStates, help: "Espaciado." },
  { key: "numericEmphasis", label: "Numeric emphasis", effectGroup: "Typography", kinds: ["numericText","tableCell"], changeTypes: ["Número/precio","Estado"], states: tabctl7AllStates, help: "Énfasis numérico." },
  { key: "buttonHeight", label: "Button height", effectGroup: "Buttons", kinds: ["button","dock","nav"], changeTypes: ["Botón","Forma y espacio","Accesibilidad"], states: tabctl7AllStates, help: "Altura táctil." },
  { key: "buttonRadius", label: "Radius", effectGroup: "Buttons", kinds: ["button","panel","chip","input","modal","dock"], changeTypes: ["Forma y espacio","Botón","Material"], states: tabctl7AllStates, help: "Radio/cápsula." },
  { key: "buttonGlow", label: "Button glow", effectGroup: "Buttons", kinds: ["button","chip","dock","nav"], changeTypes: ["Botón","Estado","Borde y luz"], states: tabctl7AllStates, zeroOff: true, help: "Luz del botón." },
  { key: "pressDepth", label: "Press depth", effectGroup: "Buttons", kinds: ["button","nav","dock"], changeTypes: ["Movimiento","Botón","Estado"], states: tabctl7AllStates, zeroOff: true, help: "Profundidad al presionar." },
  { key: "activeGlow", label: "Active glow", effectGroup: "Motion", kinds: ["button","chip","nav","numericText","panel"], changeTypes: ["Estado","Movimiento","Borde y luz"], states: tabctl7AllStates, zeroOff: true, help: "Glow activo." },
  { key: "selectionHalo", label: "Selection halo", effectGroup: "Motion", kinds: ["panel","button","chip","tableCell","nav","matrix"], changeTypes: ["Estado","Override local"], states: tabctl7AllStates, zeroOff: true, help: "Halo de selección." },
  { key: "backgroundBlur", label: "Background blur", effectGroup: "Background", kinds: ["background","panel","modal"], changeTypes: ["Fondo","Material"], states: tabctl7AllStates, zeroOff: true, help: "Blur ambiental." },
  { key: "atmosphericVeil", label: "Atmospheric veil", effectGroup: "Background", kinds: ["background","modal","panel"], changeTypes: ["Fondo","Accesibilidad"], states: tabctl7AllStates, zeroOff: true, help: "Velo de legibilidad." },
  { key: "rowHeight", label: "Row height", effectGroup: "Tables", kinds: ["table","tableCell"], changeTypes: ["Tabla","Forma y espacio"], states: tabctl7AllStates, help: "Alto de fila." },
  { key: "dividerAlpha", label: "Divider alpha", effectGroup: "Tables", kinds: ["table","tableCell","matrix"], changeTypes: ["Tabla","Borde y luz"], states: tabctl7AllStates, zeroOff: true, help: "Separadores." },
  { key: "inspectorDensity", label: "Inspector density", effectGroup: "Density", kinds: ["matrix","panel","table"], changeTypes: ["Accesibilidad","Forma y espacio","Override local"], states: tabctl7AllStates, help: "Densidad del inspector." },
];
function tabctl7GroupFor(group: string) { return tabctl7Taxonomy[group] ?? tabctl7Taxonomy["POS Product Set"] ?? Object.values(tabctl7Taxonomy)[0]; }
function tabctl7Slug(value: string) { return value.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || "default"; }
/* TABCTL7V2_SUPREMO_MODEL_END */

const STORAGE_KEY = "prisma.tabletLab.tabctl7v2.savedPresets.v1";

const presetNames = [
  "Light Cloudglass",
  "Panel Foundry",
  "Button Rig",
  "Table Pressure",
  "Checkout Focus",
  "POS Grid Air",
  "Ledger Blue",
  "Warning Soft",
  "License Lavender",
  "Glass Dense",
  "Ambient Pastel",
  "High Contrast Soft",
];

const sections = ["Overview", "Panels", "Buttons", "Tables", "Forms", "POS Kit", "Checkout", "Turno/Caja", "States", "Recipes", "Tokens", "Carga visual"];
const widgetGroups = ["Panel Set", "Button Set", "Table Set", "POS Product Set", "Checkout Rail Set", "Turno/Caja Set", "Metric Widgets", "Form Widgets", "Modal States", "Navigation/Dock", "Carga mixta", "Matriz de efectos"];
const effectGroups = ["Material", "Glass", "Color", "Shape", "Depth", "State", "Motion", "Background", "Accessibility", "Density", "Typography", "Tables", "Buttons", "Panels", "Scope"];
const viewports = ["Tablet 1024 x 768", "Tablet 1180 x 820", "Tablet 1366 x 1024", "Wide browser", "Compact stress"];
const states = ["Default", "Hover", "Focus", "Pressed", "Selected", "Disabled", "Loading", "Empty", "Success", "Warning", "Danger", "Critical", "Offline", "Dragging", "Dirty", "Locked", "Expanded", "Collapsed", "Error"];
const tones: PresetTone[] = ["neutral", "cyan", "mint", "amber", "coral", "lavender", "blue"];

const initialKnobs: Knobs = {
  glassAlpha: 24,
  blur: 22,
  saturate: 122,
  contrast: 104,
  frostVeil: 24,
  borderAlpha: 30,
  innerHighlight: 22,
  edgeShine: 18,
  specularGlow: 18,
  tintStrength: 22,
  gradientAngle: 126,
  accentStrength: 38,
  warmth: 26,
  coolness: 30,
  mutedInk: 72,
  elevation: 46,
  shadow: 24,
  contactShadow: 30,
  layerDistance: 36,
  stackOffset: 20,
  panelLift: 22,
  modalDepth: 52,
  hoverLift: 12,
  pressDepth: 10,
  activeGlow: 38,
  selectionHalo: 34,
  motionIntensity: 18,
  parallaxTiny: 1,
  reducedMotion: 0,
  backgroundFreeze: 100,
  backgroundScale: 105,
  backgroundBlur: 0,
  atmosphericVeil: 20,
  vignetteSoft: 10,
  lightLeak: 34,
  horizonPosition: 48,
  parallaxMax: 2,
  panelGap: 14,
  cardDensity: 48,
  rowHeight: 48,
  chipCompression: 48,
  toolbarCompactness: 70,
  gridColumns: 3,
  railWidth: 300,
  headerHeight: 70,
  textGlow: 34,
  inkContrast: 86,
  mutedContrast: 72,
  labelTracking: 10,
  numericEmphasis: 66,
  microcopyOpacity: 76,
  headingWeight: 72,
  tableTone: 38,
  columnPressure: 6,
  headerStickiness: 50,
  zebraSoftness: 20,
  dividerAlpha: 28,
  rowHoverGlow: 24,
  actionColumnVisibility: 80,
  buttonHeight: 44,
  buttonRadius: 18,
  buttonGlow: 26,
  borderBrightness: 44,
  pressInset: 10,
  disabledFrost: 50,
  dangerWarmth: 44,
  primarySaturation: 70,
  heroCompactness: 76,
  cardTranslucency: 60,
  railTranslucency: 54,
  modalGlassStrength: 64,
  warningToneStrength: 40,
  inspectorDensity: 62,
  metricEmphasis: 62,
};

const knobGroups: Record<string, Array<{ key: keyof Knobs; label: string; min: number; max: number; step?: number; suffix?: string }>> = {
  Material: [
    { key: "glassAlpha", label: "Material alpha", min: 0, max: 72, suffix: "%" },
    { key: "blur", label: "Material blur", min: 0, max: 34, suffix: "px" },
    { key: "frostVeil", label: "Frost veil", min: 0, max: 80, suffix: "%" },
    { key: "saturate", label: "Saturation", min: 0, max: 180, suffix: "%" },
    { key: "contrast", label: "Contrast", min: 0, max: 140, suffix: "%" },
    { key: "borderAlpha", label: "Boundary alpha", min: 0, max: 72, suffix: "%" },
    { key: "edgeShine", label: "Edge shine", min: 0, max: 88, suffix: "%" },
    { key: "innerHighlight", label: "Inner highlight", min: 0, max: 88, suffix: "%" },
  ],
  Shape: [
    { key: "buttonRadius", label: "Corner radius", min: 0, max: 34, suffix: "px" },
    { key: "panelGap", label: "Panel gap", min: 4, max: 32, suffix: "px" },
    { key: "cardDensity", label: "Card density", min: 20, max: 90, suffix: "%" },
    { key: "rowHeight", label: "Row height", min: 32, max: 76, suffix: "px" },
    { key: "chipCompression", label: "Chip compression", min: 20, max: 90, suffix: "%" },
    { key: "railWidth", label: "Rail width", min: 240, max: 420, suffix: "px" },
    { key: "headerHeight", label: "Header height", min: 46, max: 104, suffix: "px" },
  ],
  State: [
    { key: "hoverLift", label: "Hover lift", min: 0, max: 24, suffix: "px" },
    { key: "pressDepth", label: "Press depth", min: 0, max: 18, suffix: "px" },
    { key: "activeGlow", label: "Active glow", min: 0, max: 90, suffix: "%" },
    { key: "selectionHalo", label: "Selection halo", min: 0, max: 92, suffix: "%" },
    { key: "disabledFrost", label: "Disabled frost", min: 0, max: 100, suffix: "%" },
    { key: "dangerWarmth", label: "Danger warmth", min: 0, max: 88, suffix: "%" },
  ],
  Accessibility: [
    { key: "inkContrast", label: "Ink contrast", min: 48, max: 100, suffix: "%" },
    { key: "mutedContrast", label: "Muted contrast", min: 34, max: 96, suffix: "%" },
    { key: "microcopyOpacity", label: "Microcopy opacity", min: 30, max: 100, suffix: "%" },
    { key: "borderAlpha", label: "Non-text boundary", min: 0, max: 86, suffix: "%" },
    { key: "selectionHalo", label: "Focus/selected halo", min: 0, max: 92, suffix: "%" },
    { key: "reducedMotion", label: "Reduced motion", min: 0, max: 1, step: 1 },
  ],
  Scope: [
    { key: "inspectorDensity", label: "Inspector density", min: 20, max: 92, suffix: "%" },
    { key: "panelGap", label: "Scope spacing", min: 4, max: 32, suffix: "px" },
    { key: "borderAlpha", label: "Target boundary", min: 0, max: 86, suffix: "%" },
    { key: "selectionHalo", label: "Target halo", min: 0, max: 92, suffix: "%" },
    { key: "activeGlow", label: "State glow", min: 0, max: 90, suffix: "%" },
  ],


  Glass: [
    { key: "glassAlpha", label: "Glass alpha", min: 0, max: 72, suffix: "%" },
    { key: "blur", label: "Backdrop blur", min: 0, max: 34, suffix: "px" },
    { key: "saturate", label: "Saturation", min: 0, max: 160, suffix: "%" },
    { key: "contrast", label: "Contrast", min: 0, max: 122, suffix: "%" },
    { key: "frostVeil", label: "Frost veil", min: 0, max: 80, suffix: "%" },
    { key: "borderAlpha", label: "Border alpha", min: 0, max: 72, suffix: "%" },
    { key: "innerHighlight", label: "Inner highlight", min: 0, max: 82, suffix: "%" },
    { key: "edgeShine", label: "Edge shine", min: 0, max: 72, suffix: "%" },
    { key: "specularGlow", label: "Specular glow", min: 0, max: 88, suffix: "%" },
  ],
  Color: [
    { key: "tintStrength", label: "Tint strength", min: 0, max: 84, suffix: "%" },
    { key: "gradientAngle", label: "Gradient angle", min: 0, max: 360, suffix: "°" },
    { key: "accentStrength", label: "Accent strength", min: 0, max: 90, suffix: "%" },
    { key: "warmth", label: "Warmth", min: 0, max: 80, suffix: "%" },
    { key: "coolness", label: "Coolness", min: 0, max: 80, suffix: "%" },
    { key: "mutedInk", label: "Muted ink", min: 42, max: 96, suffix: "%" },
  ],
  Depth: [
    { key: "elevation", label: "Elevation", min: 0, max: 90, suffix: "%" },
    { key: "shadow", label: "Shadow spread", min: 0, max: 88, suffix: "%" },
    { key: "contactShadow", label: "Contact shadow", min: 0, max: 72, suffix: "%" },
    { key: "layerDistance", label: "Layer distance", min: 0, max: 80, suffix: "%" },
    { key: "stackOffset", label: "Stack offset", min: 0, max: 42, suffix: "px" },
    { key: "panelLift", label: "Panel lift", min: 0, max: 36, suffix: "px" },
    { key: "modalDepth", label: "Modal depth", min: 0, max: 92, suffix: "%" },
  ],
  Motion: [
    { key: "hoverLift", label: "Hover lift", min: 0, max: 24, suffix: "px" },
    { key: "pressDepth", label: "Press depth", min: 0, max: 18, suffix: "px" },
    { key: "activeGlow", label: "Active glow", min: 0, max: 80, suffix: "%" },
    { key: "selectionHalo", label: "Selection halo", min: 0, max: 80, suffix: "%" },
    { key: "motionIntensity", label: "Motion intensity", min: 0, max: 60, suffix: "%" },
    { key: "parallaxTiny", label: "Parallax tiny", min: 0, max: 4, suffix: "px" },
    { key: "reducedMotion", label: "Reduced motion", min: 0, max: 1, step: 1 },
  ],
  Background: [
    { key: "backgroundFreeze", label: "Background freeze", min: 0, max: 100, suffix: "%" },
    { key: "backgroundScale", label: "Background scale", min: 100, max: 116, suffix: "%" },
    { key: "backgroundBlur", label: "Background blur", min: 0, max: 8, suffix: "px" },
    { key: "atmosphericVeil", label: "Atmospheric veil", min: 0, max: 86, suffix: "%" },
    { key: "vignetteSoft", label: "Vignette soft", min: 0, max: 72, suffix: "%" },
    { key: "lightLeak", label: "Light leak", min: 0, max: 76, suffix: "%" },
    { key: "horizonPosition", label: "Horizon position", min: 20, max: 80, suffix: "%" },
    { key: "parallaxMax", label: "Parallax max", min: 0, max: 4, suffix: "px" },
  ],
  Density: [
    { key: "panelGap", label: "Panel gap", min: 8, max: 28, suffix: "px" },
    { key: "cardDensity", label: "Card density", min: 24, max: 80, suffix: "%" },
    { key: "rowHeight", label: "Row height", min: 38, max: 64, suffix: "px" },
    { key: "chipCompression", label: "Chip compression", min: 18, max: 82, suffix: "%" },
    { key: "toolbarCompactness", label: "Toolbar compact", min: 32, max: 92, suffix: "%" },
    { key: "gridColumns", label: "Grid columns", min: 2, max: 5, step: 1 },
    { key: "railWidth", label: "Rail width", min: 240, max: 380, suffix: "px" },
    { key: "headerHeight", label: "Header height", min: 72, max: 128, suffix: "px" },
  ],
  Typography: [
    { key: "textGlow", label: "Text glow", min: 0, max: 80, suffix: "%" },
    { key: "inkContrast", label: "Ink contrast", min: 56, max: 100, suffix: "%" },
    { key: "mutedContrast", label: "Muted contrast", min: 42, max: 92, suffix: "%" },
    { key: "labelTracking", label: "Label tracking", min: 0, max: 28, suffix: "%" },
    { key: "numericEmphasis", label: "Numeric emphasis", min: 30, max: 92, suffix: "%" },
    { key: "microcopyOpacity", label: "Microcopy opacity", min: 36, max: 100, suffix: "%" },
    { key: "headingWeight", label: "Heading weight", min: 40, max: 90, suffix: "%" },
  ],
  Tables: [
    { key: "tableTone", label: "Table tone", min: 0, max: 90, suffix: "%" },
    { key: "rowHeight", label: "Row height", min: 38, max: 64, suffix: "px" },
    { key: "columnPressure", label: "Column pressure", min: 2, max: 12, step: 1 },
    { key: "headerStickiness", label: "Header stickiness", min: 0, max: 100, suffix: "%" },
    { key: "zebraSoftness", label: "Zebra softness", min: 0, max: 62, suffix: "%" },
    { key: "dividerAlpha", label: "Divider alpha", min: 0, max: 70, suffix: "%" },
    { key: "rowHoverGlow", label: "Row hover glow", min: 0, max: 68, suffix: "%" },
    { key: "actionColumnVisibility", label: "Actions visible", min: 0, max: 100, suffix: "%" },
  ],
  Buttons: [
    { key: "buttonHeight", label: "Button height", min: 38, max: 58, suffix: "px" },
    { key: "buttonRadius", label: "Button radius", min: 10, max: 28, suffix: "px" },
    { key: "buttonGlow", label: "Button glow", min: 0, max: 80, suffix: "%" },
    { key: "borderBrightness", label: "Border brightness", min: 0, max: 90, suffix: "%" },
    { key: "pressInset", label: "Press inset", min: 0, max: 20, suffix: "px" },
    { key: "disabledFrost", label: "Disabled frost", min: 0, max: 80, suffix: "%" },
    { key: "dangerWarmth", label: "Danger warmth", min: 0, max: 80, suffix: "%" },
    { key: "primarySaturation", label: "Primary saturation", min: 20, max: 100, suffix: "%" },
  ],
  Panels: [
    { key: "heroCompactness", label: "Hero compact", min: 30, max: 92, suffix: "%" },
    { key: "cardTranslucency", label: "Card translucency", min: 24, max: 86, suffix: "%" },
    { key: "railTranslucency", label: "Rail translucency", min: 24, max: 86, suffix: "%" },
    { key: "modalGlassStrength", label: "Modal glass", min: 20, max: 92, suffix: "%" },
    { key: "warningToneStrength", label: "Warning tone", min: 0, max: 86, suffix: "%" },
    { key: "inspectorDensity", label: "Inspector density", min: 20, max: 92, suffix: "%" },
    { key: "metricEmphasis", label: "Metric emphasis", min: 20, max: 92, suffix: "%" },
  ],
};

type KnobApplicabilityRule = { effectGroup: string; targets: string[]; description: string; inactiveBehavior: string };

const knobApplicability = {
  "glassAlpha": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "blur": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "saturate": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "contrast": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "frostVeil": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "borderAlpha": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "innerHighlight": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "edgeShine": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "specularGlow": {
    "effectGroup": "Glass",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "material/transparency/backdrop/border/highlight controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "tintStrength": {
    "effectGroup": "Color",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "tone/tint/temperature/ink controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "gradientAngle": {
    "effectGroup": "Color",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "tone/tint/temperature/ink controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "accentStrength": {
    "effectGroup": "Color",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "tone/tint/temperature/ink controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "warmth": {
    "effectGroup": "Color",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "tone/tint/temperature/ink controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "coolness": {
    "effectGroup": "Color",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "tone/tint/temperature/ink controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "mutedInk": {
    "effectGroup": "Color",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "tone/tint/temperature/ink controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "elevation": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta",
      "Button Set",
      "POS Product Set",
      "Form Widgets",
      "Navigation/Dock"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "shadow": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta",
      "Button Set",
      "POS Product Set",
      "Form Widgets",
      "Navigation/Dock"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "contactShadow": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta",
      "Button Set",
      "POS Product Set",
      "Form Widgets",
      "Navigation/Dock"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "layerDistance": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Modal States",
      "Checkout Rail Set",
      "Carga mixta"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "stackOffset": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Modal States",
      "Checkout Rail Set",
      "Carga mixta"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "panelLift": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta",
      "Button Set",
      "POS Product Set",
      "Form Widgets",
      "Navigation/Dock"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "modalDepth": {
    "effectGroup": "Depth",
    "targets": [
      "Panel Set",
      "Modal States",
      "Checkout Rail Set",
      "Carga mixta"
    ],
    "description": "elevation/shadow/layer-distance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "hoverLift": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "pressDepth": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "activeGlow": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "selectionHalo": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "motionIntensity": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "parallaxTiny": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "reducedMotion": {
    "effectGroup": "Motion",
    "targets": [
      "Panel Set",
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "interactive motion and focus affordance controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "backgroundFreeze": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "backgroundScale": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "backgroundBlur": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "atmosphericVeil": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "vignetteSoft": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "lightLeak": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "horizonPosition": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "parallaxMax": {
    "effectGroup": "Background",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "canvas atmospheric image/veil controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "panelGap": {
    "effectGroup": "Density",
    "targets": [
      "Panel Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "cardDensity": {
    "effectGroup": "Density",
    "targets": [
      "Panel Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "rowHeight": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "chipCompression": {
    "effectGroup": "Density",
    "targets": [
      "Panel Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "toolbarCompactness": {
    "effectGroup": "Density",
    "targets": [
      "Panel Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "gridColumns": {
    "effectGroup": "Density",
    "targets": [
      "POS Product Set",
      "Panel Set",
      "Metric Widgets",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "railWidth": {
    "effectGroup": "Density",
    "targets": [
      "Checkout Rail Set",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "headerHeight": {
    "effectGroup": "Density",
    "targets": [
      "Panel Set",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "spacing/row/grid/rail/header controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "textGlow": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "inkContrast": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "mutedContrast": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "labelTracking": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "numericEmphasis": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "microcopyOpacity": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "headingWeight": {
    "effectGroup": "Typography",
    "targets": [
      "Panel Set",
      "Button Set",
      "Table Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "ink/microcopy/numerical emphasis controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "tableTone": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "columnPressure": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "headerStickiness": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "zebraSoftness": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "dividerAlpha": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "rowHoverGlow": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "actionColumnVisibility": {
    "effectGroup": "Tables",
    "targets": [
      "Table Set",
      "Carga mixta"
    ],
    "description": "CloudTable-only row/column/action controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "buttonHeight": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "buttonRadius": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "buttonGlow": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "borderBrightness": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "pressInset": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "disabledFrost": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "dangerWarmth": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "primarySaturation": {
    "effectGroup": "Buttons",
    "targets": [
      "Button Set",
      "POS Product Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Form Widgets",
      "Modal States",
      "Navigation/Dock",
      "Carga mixta"
    ],
    "description": "action/button-only touch and state controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "heroCompactness": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "cardTranslucency": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "railTranslucency": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "modalGlassStrength": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "warningToneStrength": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "inspectorDensity": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  },
  "metricEmphasis": {
    "effectGroup": "Panels",
    "targets": [
      "Panel Set",
      "Checkout Rail Set",
      "Turno/Caja Set",
      "Metric Widgets",
      "Modal States",
      "Carga mixta"
    ],
    "description": "panel-family-only compactness/translucency/semantics controls",
    "inactiveBehavior": "disabled in UI with 'sin impacto aquí' hint; value is preserved for other widget groups"
  }
} as Record<keyof Knobs, KnobApplicabilityRule>;

function knobRule(key: keyof Knobs): KnobApplicabilityRule | null {
  return knobApplicability[key] ?? null;
}

function knobAppliesToWidget(key: keyof Knobs, group: string) {
  const rule = knobRule(key);
  if (!rule) return true;
  return rule.targets.includes(group);
}

function uniqueTargetsForEffect(group: string) {
  const targets = new Set<string>();
  for (const item of knobGroups[group] ?? []) {
    const rule = knobRule(item.key);
    for (const target of rule?.targets ?? []) targets.add(target);
  }
  return Array.from(targets);
}

const toneSeed: Record<PresetTone, string> = {
  neutral: "120 137 154",
  cyan: "46 190 255",
  mint: "52 211 153",
  amber: "245 158 11",
  coral: "244 63 94",
  lavender: "167 139 250",
  blue: "59 130 246",
};

function isoNow() {
  return new Date().toISOString();
}

function makeId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) return crypto.randomUUID();
  return `preset-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function safePresetName(value: string | null, fallback: string) {
  const trimmed = (value ?? "").trim().slice(0, 52);
  return trimmed || fallback;
}

function readSavedPresets(): PresetRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((item) => item && typeof item.id === "string") : [];
  } catch {
    return [];
  }
}

function persistSavedPresets(records: PresetRecord[]) {
  if (typeof window === "undefined") return false;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(records.slice(0, 64)));
    return true;
  } catch {
    return false;
  }
}

function useImmersiveRuntimeGuard() {
  useEffect(() => {
    document.documentElement.setAttribute("data-tablet-lab-immersive", "true");
    document.body.setAttribute("data-tablet-lab-immersive", "true");

    const topTokens = ["Sucursal principal", "Tablet Caja", "Operador", "Operación diaria", "En línea", "Control Atlas"];
    const bottomTokens = ["Vender", "Turno", "Inventario", "Ventas", "Devol", "Pendientes", "Licencia"];

    const removeUpperNavigation = () => {
      const nodes = Array.from(document.querySelectorAll<HTMLElement>("header, nav, [class*='topbar'], [class*='top-bar'], [class*='tabletHeader'], [class*='surfaceHeader'], [data-tablet-top-nav], [data-prisma-top-nav]"));
      for (const node of nodes) {
        if (node.closest('[data-component="TabletLabAutoStudio"]')) continue;
        const text = node.textContent ?? "";
        const topScore = topTokens.reduce((score, token) => score + (text.includes(token) ? 1 : 0), 0);
        const bottomScore = bottomTokens.reduce((score, token) => score + (text.includes(token) ? 1 : 0), 0);
        const box = node.getBoundingClientRect();
        const looksUpper = box.top < Math.max(160, window.innerHeight * 0.28);
        if (topScore >= 2 && bottomScore < 3 && looksUpper) {
          node.setAttribute("data-tabctl3-runtime-removed", "tablet-top-navigation");
          node.remove();
        }
      }
    };

    removeUpperNavigation();
    const timers = [window.setTimeout(removeUpperNavigation, 80), window.setTimeout(removeUpperNavigation, 420)];
    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
      document.documentElement.removeAttribute("data-tablet-lab-immersive");
      document.body.removeAttribute("data-tablet-lab-immersive");
    };
  }, []);
}

function ControlSelect({ label, value, options, onChange }: { label: string; value: string; options: string[]; onChange: (next: string) => void }) {
  return (
    <label className={styles.controlSelect}>
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)} aria-label={label}>
        {options.map((option) => (
          <option value={option} key={option}>{option}</option>
        ))}
      </select>
    </label>
  );
}

function Knob({
  item,
  value,
  onChange,
  active,
  scope,
}: {
  item: { key: keyof Knobs; label: string; min: number; max: number; step?: number; suffix?: string };
  value: number;
  onChange: (value: number) => void;
  active: boolean;
  scope: string;
}) {
  return (
    <label
      className={`${styles.knob} ${active ? styles.knobActive : styles.knobInactive}`}
      data-knob={item.key}
      data-applicability={active ? "active" : "inactive"}
      title={scope}
    >
      <span className={styles.knobLabel}>
        {item.label}
        <em>{active ? "aplica" : "sin impacto"}</em>
      </span>
      <input
        type="range"
        min={item.min}
        max={item.max}
        step={item.step ?? 1}
        value={value}
        disabled={!active}
        onChange={(event) => onChange(Number(event.target.value))}
        aria-label={item.label}
      />
      <output>{active ? `${value}${item.suffix ?? ""}` : "sin impacto"}</output>
    </label>
  );
}

function GlassCard({ title, subtitle, tone = "cyan", children, emphasis = "standard" }: { title: string; subtitle: string; tone?: PresetTone; children?: ReactNode; emphasis?: "standard" | "hero" | "rail" | "warning" }) {
  return (
    <article className={`${styles.glassCard} ${styles[`tone_${tone}`]} ${styles[`emphasis_${emphasis}`]}`} data-component="GlassCard" data-tone={tone} data-variant={emphasis}>
      <div className={styles.cardTopline}>{subtitle}</div>
      <h3>{title}</h3>
      {children}
    </article>
  );
}

function PanelPreview() {
  return (
    <div className={styles.previewGrid} data-component="PanelPreview">
      <GlassCard title="HeroPanel" subtitle="compact command" tone="cyan" emphasis="hero">
        <p>Header operativo con logo, estado y CTA sin marquesina gorda.</p>
        <div className={styles.metricRow}><b>92%</b><span>glass readiness</span></div>
      </GlassCard>
      <GlassCard title="MetricPanel" subtitle="money/count/status" tone="mint"><p>Ventas, efectivo esperado, sincronía, stock o licencia.</p></GlassCard>
      <GlassCard title="CommandPanel" subtitle="primary operation" tone="amber"><button className={styles.primaryAction}>Abrir turno</button></GlassCard>
      <GlassCard title="WarningPanel" subtitle="risk state" tone="coral" emphasis="warning"><p>Diferencia crítica, offline o bloqueo de venta.</p></GlassCard>
      <GlassCard title="InspectorPanel" subtitle="details rail" tone="lavender"><p>Detalle editable o sólo lectura sin abrir otra ruta.</p></GlassCard>
    </div>
  );
}

function ButtonPreview() {
  const buttons = ["PrimaryAction", "SecondaryAction", "GhostAction", "DangerAction", "SuccessAction", "IconAction", "SplitAction", "SegmentedAction"];
  return <div className={styles.buttonMatrix} data-component="ButtonPreview">{buttons.map((item, index) => <button key={item} className={index === 3 ? styles.dangerAction : index === 4 ? styles.successAction : index === 2 ? styles.ghostAction : styles.primaryAction}>{item}</button>)}</div>;
}

function TablePreview() {
  const rows = [
    ["KeyValueTable", "2 cols", "Caja lista", "mint"],
    ["MiniOpsTable", "4 cols", "Pagos cortos", "cyan"],
    ["ActionTable", "6 cols", "Ventas/clientes", "blue"],
    ["LedgerTable", "9 cols", "Auditoría", "lavender"],
    ["ExceptionTable", "5 cols", "Riesgos", "coral"],
  ];
  return (
    <div className={styles.tableShell} data-component="TablePreview" data-variant="pressure-matrix">
      <div className={styles.tableToolbar}><strong>CloudTable pressure system</strong><span>search · filters · sort · export · overflow</span></div>
      <table>
        <thead><tr><th>Tipo</th><th>Columnas</th><th>Uso</th><th>Tono</th><th>Acciones</th></tr></thead>
        <tbody>{rows.map((row) => <tr key={row[0]}><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td><span className={styles.statusChip}>{row[3]}</span></td><td>Aplicar · Ver</td></tr>)}</tbody>
      </table>
    </div>
  );
}

function PosPreview() {
  return (
    <div className={styles.posGrid} data-component="POSProductPreview">
      {['Café frío', 'Pan dulce', 'Muffin', 'Té jazmín', 'Combo lunch', 'Agua mineral'].map((item, index) => (
        <article className={styles.productTile} key={item}>
          <div className={styles.productImage}>{item.slice(0, 2).toUpperCase()}</div>
          <strong>{item}</strong><span>${(42 + index * 11).toFixed(2)}</span><button className={styles.quickAdd}>+ Agregar</button>
        </article>
      ))}
    </div>
  );
}

function CheckoutPreview() {
  return (
    <div className={styles.checkoutPreview} data-component="CheckoutRailPreview">
      <GlassCard title="CheckoutRail" subtitle="cart + tender + total" tone="cyan" emphasis="rail">
        {['Café frío x2', 'Pan dulce x1', 'Combo lunch x1'].map((line, index) => <div className={styles.cartLine} key={line}><span>{line}</span><b>${(index + 2) * 48}.00</b></div>)}
        <div className={styles.totalHero}><span>Total</span><strong>$286.00</strong></div>
        <button className={styles.primaryAction}>Cobrar</button>
      </GlassCard>
      <GlassCard title="TenderSelector" subtitle="cash/card/mixed" tone="mint"><div className={styles.pillRow}><span>Efectivo</span><span>Tarjeta</span><span>Mixto</span></div></GlassCard>
    </div>
  );
}

function ShiftPreview() {
  return (
    <div className={styles.previewGrid} data-component="ShiftPreview">
      <GlassCard title="ClosedRegisterCard" subtitle="Caja cerrada" tone="blue"><p>Sin turno abierto. La venta queda bloqueada hasta iniciar caja.</p><button className={styles.primaryAction}>Abrir turno</button></GlassCard>
      <GlassCard title="CashDifferencePanel" subtitle="diferencia" tone="amber"><div className={styles.metricRow}><b>$0.00</b><span>diferencia esperada</span></div></GlassCard>
      <GlassCard title="CloseShiftDangerZone" subtitle="cierre crítico" tone="coral"><button className={styles.dangerAction}>Cerrar turno</button></GlassCard>
    </div>
  );
}

function MetricPreview() {
  return <div className={styles.previewGrid}>{['MoneyMetric', 'CountMetric', 'StockMetric', 'LicenseStatus', 'SyncStatus', 'OperatorBadge', 'TerminalBadge'].map((item, index) => <GlassCard key={item} title={item} subtitle="widget" tone={tones[index % tones.length]}><div className={styles.metricRow}><b>{index % 2 ? 'OK' : '$' + (index + 1) * 120}</b><span>mock visual</span></div></GlassCard>)}</div>;
}

function FormsPreview() {
  return (
    <div className={styles.formPreview} data-component="FormPreview">
      <label><span>SearchInput</span><input placeholder="Buscar producto, cliente o licencia" /></label>
      <label><span>MoneyInput</span><input placeholder="$0.00" inputMode="decimal" /></label>
      <label><span>SelectPill</span><select><option>Terminal Caja 1</option><option>Terminal Patio</option></select></label>
      <label><span>TextareaGlass</span><textarea placeholder="Nota visual de referencia" /></label>
      <p className={styles.validationMessage}>ValidationMessage: listo para error, warning o success sin depender de backend.</p>
    </div>
  );
}

function ModalPreview() {
  return <div className={styles.modalStage} data-component="ModalStatePreview"><GlassCard title="ClosedRegisterModal" subtitle="modal glass" tone="lavender" emphasis="rail"><p>La caja está cerrada. Abre turno para continuar con venta.</p><div className={styles.buttonMatrix}><button className={styles.ghostAction}>Cancelar</button><button className={styles.primaryAction}>Abrir turno</button></div></GlassCard></div>;
}

function NavigationPreview() {
  return <div className={styles.previewGrid}><GlassCard title="BottomDock" subtitle="navegación principal" tone="cyan"><p>La navegación superior se retira de la composición del laboratorio. El dock inferior manda.</p></GlassCard><BottomNav /></div>;
}

function MixedPreview() {
  return <div className={styles.mixedPreview} data-component="MixedStressTest"><PanelPreview /><TablePreview /><CheckoutPreview /></div>;
}

function EffectMatrixPreview() {
  const visibleWidgetGroups = widgetGroups.filter((group) => group !== "Matriz de efectos");
  return (
    <div className={styles.effectMatrix} data-component="EffectApplicabilityMatrix" data-variant="predefined-knob-targets">
      <div className={styles.tableToolbar}>
        <strong>Matriz de aplicabilidad</strong>
        <span>cada perilla se activa sólo donde tiene impacto declarado</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Effect group</th>
            <th>Knobs</th>
            <th>Targets declarados</th>
            <th>Regla</th>
          </tr>
        </thead>
        <tbody>
          {effectGroups.map((group) => {
            const items = knobGroups[group] ?? [];
            const targets = uniqueTargetsForEffect(group);
            return (
              <tr key={group}>
                <td><b>{group}</b></td>
                <td>{items.map((item) => item.label).join(" · ")}</td>
                <td>{targets.filter((target) => visibleWidgetGroups.includes(target)).join(" · ")}</td>
                <td>{group === "Tables" ? "sólo tablas" : group === "Buttons" ? "sólo acciones/botones" : group === "Background" ? "canvas completo" : "targets explícitos"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function WidgetPreview({ group }: { group: string }) {
  if (group === "Matriz de efectos") return <EffectMatrixPreview />;
  if (group === "Button Set") return <ButtonPreview />;
  if (group === "Table Set") return <TablePreview />;
  if (group === "POS Product Set") return <PosPreview />;
  if (group === "Checkout Rail Set") return <CheckoutPreview />;
  if (group === "Turno/Caja Set") return <ShiftPreview />;
  if (group === "Metric Widgets") return <MetricPreview />;
  if (group === "Form Widgets") return <FormsPreview />;
  if (group === "Modal States") return <ModalPreview />;
  if (group === "Navigation/Dock") return <NavigationPreview />;
  if (group === "Carga mixta") return <MixedPreview />;
  return <PanelPreview />;
}

function BottomNav() {
  const items = [
    ["Vender", "/pos"],
    ["Turno", "/turno"],
    ["Inventario", "/inventario"],
    ["Ventas", "/ventas"],
    ["Devol.", "/devoluciones"],
    ["Pendientes", "/pendientes"],
    ["Licencia", "/licencia"],
  ];
  return <nav className={styles.bottomNav} aria-label="Navegación principal Tablet" data-component="TabletBottomNavigation" data-variant="preserved-local-dock">{items.map(([label, href]) => <a key={label} href={href}>{label}</a>)}</nav>;
}

export function TabletLabAutoStudio() {
  useImmersiveRuntimeGuard();
  const [preset, setPreset] = useState(presetNames[0]);
  const [section, setSection] = useState(sections[0]);
  const [widgetGroup, setWidgetGroup] = useState(widgetGroups[0]);
  const [effectGroup, setEffectGroup] = useState(effectGroups[0]);
  const [viewport, setViewport] = useState(viewports[1]);
  const [stateMode, setStateMode] = useState(states[0]);
  const [tone, setTone] = useState<PresetTone>("cyan");
  const [backgroundMode, setBackgroundMode] = useState("Frozen atmospheric");
  const [knobs, setKnobs] = useState<Knobs>(initialKnobs);
  const [saved, setSaved] = useState<PresetRecord[]>([]);
  const [savedOpen, setSavedOpen] = useState(false);

  const [tabctl7Layer, setTabctl7Layer] = useState("Card base");
  const [tabctl7Role, setTabctl7Role] = useState("Superficie primaria");
  const [tabctl7Change, setTabctl7Change] = useState("Material");
  const [tabctl7Material, setTabctl7Material] = useState("liquid-glass");
  const [tabctl7ColorMode, setTabctl7ColorMode] = useState(tabctl7ColorModes[1]);
  const [tabctl7Scope, setTabctl7Scope] = useState(tabctl7Scopes[0]);
  const [tabctl7Inheritance, setTabctl7Inheritance] = useState(tabctl7InheritanceModes[0]);

  const tabctl7Group = tabctl7GroupFor(widgetGroup);
  const tabctl7Layers = tabctl7Group.layers.map((item) => item.layer);
  const tabctl7CurrentLayer = tabctl7Group.layers.find((item) => item.layer === tabctl7Layer) ?? tabctl7Group.layers[0];
  const tabctl7Roles = tabctl7CurrentLayer.roles.map((item) => item.role);
  const tabctl7CurrentRole = tabctl7CurrentLayer.roles.find((item) => item.role === tabctl7Role) ?? tabctl7CurrentLayer.roles[0];
  const tabctl7MaterialSpec = tabctl7Materials.find((item) => item.id === tabctl7Material) ?? tabctl7Materials[0];
  const tabctl7VisibleControls = tabctl7Controls.filter((control) => control.kinds.includes(tabctl7CurrentRole.kind) && control.changeTypes.includes(tabctl7Change));
  const tabctl7SuggestedEffects = Array.from(new Set(tabctl7VisibleControls.map((control) => control.effectGroup)));
  const tabctl7ZeroSummary = [knobs.blur === 0 ? "blur off" : null, knobs.borderAlpha === 0 ? "border off" : null, knobs.buttonGlow === 0 && knobs.textGlow === 0 && knobs.specularGlow === 0 ? "glow off" : null, knobs.glassAlpha === 0 ? "alpha off" : null].filter(Boolean).join(" · ") || "ceros con apagado real";

  useEffect(() => {
    const group = tabctl7GroupFor(widgetGroup);
    const firstLayer = group.layers[0];
    const nextLayer = group.layers.find((item) => item.layer === tabctl7Layer) ?? firstLayer;
    if (nextLayer.layer !== tabctl7Layer) { setTabctl7Layer(nextLayer.layer); setTabctl7Role(nextLayer.roles[0]?.role ?? ""); return; }
    if (!nextLayer.roles.some((item) => item.role === tabctl7Role)) setTabctl7Role(nextLayer.roles[0]?.role ?? "");
  }, [widgetGroup, tabctl7Layer, tabctl7Role]);


  const [storageStatus, setStorageStatus] = useState("localStorage listo");

  useEffect(() => {
    setSaved(readSavedPresets());
  }, []);

  const styleVars = useMemo(() => ({
    "--tabctl3-alpha": `${knobs.glassAlpha / 100}`,
    "--tabctl3-blur": `${knobs.blur}px`,
    "--tabctl3-saturate": `${knobs.saturate}%`,
    "--tabctl3-contrast": `${knobs.contrast}%`,
    "--tabctl3-border-alpha": `${knobs.borderAlpha / 100}`,
    "--tabctl3-highlight": `${knobs.innerHighlight / 100}`,
    "--tabctl3-edge": `${knobs.edgeShine / 100}`,
    "--tabctl3-glow": `${knobs.specularGlow / 100}`,
    "--tabctl3-tint": toneSeed[tone],
    "--tabctl3-tint-strength": `${knobs.tintStrength / 100}`,
    "--tabctl3-angle": `${knobs.gradientAngle}deg`,
    "--tabctl3-shadow": `${knobs.shadow / 100}`,
    "--tabctl3-frost": `${knobs.frostVeil / 100}`,
    "--tabctl3-light-leak": `${knobs.lightLeak / 100}`,
    "--tabctl3-radius": `${knobs.buttonRadius + 8}px`,
    "--tabctl3-gap": `${knobs.panelGap}px`,
    "--tabctl3-row": `${knobs.rowHeight}px`,
    "--tabctl3-columns": String(knobs.gridColumns),
    "--tabctl3-rail": `${knobs.railWidth}px`,
    "--tabctl3-text-glow": `${knobs.textGlow / 100}`,
    "--tabctl3-bg-scale": `${knobs.backgroundScale / 100}`,
    "--tabctl3-bg-blur": `${knobs.backgroundBlur}px`,
    "--tabctl3-veil": `${knobs.atmosphericVeil / 100}`,
    "--tabctl3-vignette": `${knobs.vignetteSoft / 100}`,
    "--tabctl3-header": `${knobs.headerHeight}px`,
    "--tabctl3-button-height": `${knobs.buttonHeight}px`,
    "--tabctl3-button-glow": `${knobs.buttonGlow / 100}`,
    "--tabctl3-border-brightness": `${knobs.borderBrightness / 100}`,
    "--tabctl3-press-inset": `${knobs.pressInset}px`,
    "--tabctl3-disabled-frost": `${knobs.disabledFrost / 100}`,
    "--tabctl3-danger-warmth": `${knobs.dangerWarmth / 100}`,
    "--tabctl3-primary-saturation": `${knobs.primarySaturation}%`,
    "--tabctl3-table-tone": `${knobs.tableTone / 100}`,
    "--tabctl3-column-pressure": `${knobs.columnPressure}`,
    "--tabctl3-header-stickiness": `${knobs.headerStickiness / 100}`,
    "--tabctl3-zebra": `${knobs.zebraSoftness / 100}`,
    "--tabctl3-divider-alpha": `${knobs.dividerAlpha / 100}`,
    "--tabctl3-row-hover": `${knobs.rowHoverGlow / 100}`,
    "--tabctl3-action-column": `${knobs.actionColumnVisibility / 100}`,
    "--tabctl3-card-density": `${knobs.cardDensity / 100}`,
    "--tabctl3-chip-compression": `${knobs.chipCompression / 100}`,
    "--tabctl3-toolbar-compactness": `${knobs.toolbarCompactness / 100}`,
    "--tabctl3-ink-contrast": `${knobs.inkContrast / 100}`,
    "--tabctl3-muted-contrast": `${knobs.mutedContrast / 100}`,
    "--tabctl3-label-tracking": `${knobs.labelTracking / 100}`,
    "--tabctl3-numeric-emphasis": `${knobs.numericEmphasis / 100}`,
    "--tabctl3-microcopy": `${knobs.microcopyOpacity / 100}`,
    "--tabctl3-heading-weight": `${Math.round(400 + knobs.headingWeight * 5)}`,
    "--tabctl3-card-translucency": `${knobs.cardTranslucency / 100}`,
    "--tabctl3-rail-translucency": `${knobs.railTranslucency / 100}`,
    "--tabctl3-modal-glass": `${knobs.modalGlassStrength / 100}`,
    "--tabctl3-warning-tone": `${knobs.warningToneStrength / 100}`,
    "--tabctl3-metric-emphasis": `${knobs.metricEmphasis / 100}`,
    "--tabctl7-material-alpha": `${tabctl7MaterialSpec.alpha}`,
    "--tabctl7-material-frost": `${tabctl7MaterialSpec.frost}`,
    "--tabctl7-material-blur-delta": `${tabctl7MaterialSpec.blurDelta}px`,
    "--tabctl7-material-glow": `${tabctl7MaterialSpec.glow}`,
    "--tabctl7-material-border": `${tabctl7MaterialSpec.border}`,
  }) as CSSProperties, [knobs, tone, tabctl7MaterialSpec]);

  const currentRecipe = useMemo<PresetRecord>(() => ({
    id: "draft",
    name: `${preset} / ${widgetGroup}`,
    basePreset: preset,
    section,
    widgetGroup,
    effectGroup,
    viewport,
    stateMode,
    tone,
    glassAlpha: knobs.glassAlpha,
    blur: knobs.blur,
    saturate: knobs.saturate,
    contrast: knobs.contrast,
    tintStrength: knobs.tintStrength,
    glow: knobs.specularGlow,
    radius: knobs.buttonRadius + 8,
    shadow: knobs.shadow,
    density: knobs.cardDensity,
    columns: knobs.gridColumns,
    backgroundMode,
    tabctl7ModelVersion: TABCTL7V2_MODEL_VERSION,
    tabctl7Layer: tabctl7CurrentLayer.layer,
    tabctl7Role: tabctl7CurrentRole.role,
    tabctl7Part: tabctl7CurrentRole.part,
    tabctl7Kind: tabctl7CurrentRole.kind,
    tabctl7Change,
    tabctl7Material,
    tabctl7MaterialLabel: tabctl7MaterialSpec.label,
    tabctl7ColorMode,
    tabctl7Scope,
    tabctl7Inheritance,
    tabctl7Controls: tabctl7VisibleControls.map((control) => control.key),
    tabctl7ZeroPolicy: "zero-means-off",
    createdAt: isoNow(),
    updatedAt: isoNow(),
  }), [preset, section, widgetGroup, effectGroup, viewport, stateMode, tone, knobs, backgroundMode, tabctl7CurrentLayer.layer, tabctl7CurrentRole, tabctl7Change, tabctl7Material, tabctl7MaterialSpec, tabctl7ColorMode, tabctl7Scope, tabctl7Inheritance, tabctl7VisibleControls]);

  const updateKnob = (key: keyof Knobs, value: number) => setKnobs((prev) => ({ ...prev, [key]: value }));

  const currentKnobItems = knobGroups[effectGroup] ?? [];
  const activeKnobCount = currentKnobItems.filter((item) => knobAppliesToWidget(item.key, widgetGroup)).length;

  const savePreset = () => {
    const name = safePresetName(window.prompt("Nombre del preset visual", currentRecipe.name), currentRecipe.name);
    const now = isoNow();
    const next: PresetRecord = { ...currentRecipe, id: makeId(), name, createdAt: now, updatedAt: now };
    const records = [next, ...saved].slice(0, 64);
    setSaved(records);
    setStorageStatus(persistSavedPresets(records) ? "Preset guardado en localStorage" : "No se pudo persistir; quedó en memoria");
  };

  const applyPreset = (record: PresetRecord) => {
    setPreset(record.basePreset);
    setSection(record.section);
    setWidgetGroup(record.widgetGroup);
    setEffectGroup(record.effectGroup);
    setViewport(record.viewport);
    setStateMode(record.stateMode);
    setTone(record.tone);
    setBackgroundMode(record.backgroundMode);
    setTabctl7Layer(record.tabctl7Layer ?? tabctl7Layer);
    setTabctl7Role(record.tabctl7Role ?? tabctl7Role);
    setTabctl7Change(record.tabctl7Change ?? tabctl7Change);
    setTabctl7Material(record.tabctl7Material ?? tabctl7Material);
    setTabctl7ColorMode(record.tabctl7ColorMode ?? tabctl7ColorMode);
    setTabctl7Scope(record.tabctl7Scope ?? tabctl7Scope);
    setTabctl7Inheritance(record.tabctl7Inheritance ?? tabctl7Inheritance);
    setKnobs((prev) => ({
      ...prev,
      glassAlpha: record.glassAlpha,
      blur: record.blur,
      saturate: record.saturate,
      contrast: record.contrast,
      tintStrength: record.tintStrength,
      specularGlow: record.glow,
      buttonRadius: Math.max(10, record.radius - 8),
      shadow: record.shadow,
      cardDensity: record.density,
      gridColumns: record.columns,
    }));
  };

  const deletePreset = (id: string) => {
    const records = saved.filter((item) => item.id !== id);
    setSaved(records);
    setStorageStatus(persistSavedPresets(records) ? "Preset eliminado" : "Eliminado en memoria; localStorage no disponible");
  };

  const duplicatePreset = (record: PresetRecord) => {
    const now = isoNow();
    const clone = { ...record, id: makeId(), name: `${record.name} copia`, createdAt: now, updatedAt: now };
    const records = [clone, ...saved].slice(0, 64);
    setSaved(records);
    persistSavedPresets(records);
  };

  const copyRecipe = async (record: PresetRecord = currentRecipe) => {
    const recipe = { ...record, modelVersion: TABCTL7V2_MODEL_VERSION, layoutRule: "minimal-containers-controls-outside-canvas", transparentZero: true, targetGrammar: "Grupo→Capa→Rol→Tipo→Estado→Material→Color→Control→Alcance→Herencia" };
    const text = JSON.stringify(recipe, null, 2);
    try {
      await navigator.clipboard.writeText(text);
      setStorageStatus("JSON copiado al portapapeles");
    } catch {
      setStorageStatus("No se pudo copiar JSON; usa Export JSON visual");
    }
  };

  const clearPresets = () => {
    if (!window.confirm("¿Limpiar todos los presets guardados de este navegador?")) return;
    setSaved([]);
    persistSavedPresets([]);
    setStorageStatus("Presets limpiados");
  };

  return (
    <section className={styles.autoStudio} style={styleVars} data-component="TabletLabAutoStudio" data-preset={preset} data-widget-group={widgetGroup} data-effect-group={effectGroup} data-state-mode={stateMode} data-viewport={viewport} data-layout="tabctl7v2-supreme-role-state-material-scope" data-tabctl7-version={TABCTL7V2_MODEL_VERSION} data-tabctl7-layer={tabctl7Slug(tabctl7CurrentLayer.layer)} data-tabctl7-role={tabctl7Slug(tabctl7CurrentRole.role)} data-tabctl7-kind={tabctl7CurrentRole.kind} data-tabctl7-change={tabctl7Slug(tabctl7Change)} data-tabctl7-material={tabctl7Material} data-tabctl7-color-mode={tabctl7Slug(tabctl7ColorMode)} data-tabctl7-scope={tabctl7Slug(tabctl7Scope)} data-tabctl7-inheritance={tabctl7Slug(tabctl7Inheritance)} data-tabctl7-zero-blur={knobs.blur === 0 ? "off" : "on"} data-tabctl7-zero-glow={(knobs.buttonGlow === 0 && knobs.textGlow === 0 && knobs.specularGlow === 0) ? "off" : "on"} data-tabctl7-zero-border={knobs.borderAlpha === 0 ? "off" : "on"}>
      <header className={styles.slimHeader} data-component="SlimAtlasHeader">
        <div className={styles.logoLine}>
          <div className={styles.logoMark} aria-hidden="true">P</div>
          <div>
            <p className={styles.eyebrow}>LAB aislado · TABCTL7 v2 Supremo · roles/estados/materiales · 0 deps nuevas · /tablet-lab</p>
            <h1>Tablet Cloudglass Atlas · TABCTL7 v2</h1>
          </div>
        </div>
      </header>

      <div className={styles.workbench} data-component="MinimalWorkbench">
        <aside className={styles.controlColumn} data-component="ControlColumnOutsideCanvas">
          <div className={styles.selectStack} data-component="ControlDropdownBank">
            <ControlSelect label="Preset" value={preset} options={[...presetNames, ...saved.map((item) => item.name)]} onChange={(next) => {
              const savedPreset = saved.find((item) => item.name === next);
              if (savedPreset) applyPreset(savedPreset); else setPreset(next);
            }} />
            <ControlSelect label="Section" value={section} options={sections} onChange={setSection} />
            <ControlSelect label="Widget group" value={widgetGroup} options={widgetGroups} onChange={setWidgetGroup} />
            <ControlSelect label="Effects" value={effectGroup} options={effectGroups} onChange={setEffectGroup} />
            <ControlSelect label="Viewport" value={viewport} options={viewports} onChange={setViewport} />
            <ControlSelect label="State" value={stateMode} options={states} onChange={setStateMode} />
            <ControlSelect label="Tone" value={tone} options={tones} onChange={(value) => setTone(value as PresetTone)} />
          </div>



          <div className={styles.tabctl7TargetPanel} data-component="Tabctl7V2TargetStudio" data-tabctl7-kind={tabctl7CurrentRole.kind}>
            <div className={styles.tabctl7PanelTitle}><strong>Target TABCTL7 v2</strong><span>{TABCTL7V2_MODEL_VERSION}</span></div>
            <div className={styles.tabctl7TargetGrid}>
              <ControlSelect label="Capa" value={tabctl7CurrentLayer.layer} options={tabctl7Layers} onChange={(next) => { const layer = tabctl7Group.layers.find((item) => item.layer === next); setTabctl7Layer(next); setTabctl7Role(layer?.roles[0]?.role ?? ""); }} />
              <ControlSelect label="Rol / parte" value={tabctl7CurrentRole.role} options={tabctl7Roles} onChange={setTabctl7Role} />
              <ControlSelect label="Qué cambiar" value={tabctl7Change} options={tabctl7ChangeTypes} onChange={setTabctl7Change} />
              <ControlSelect label="Material" value={tabctl7Material} options={tabctl7Materials.map((item) => item.id)} onChange={setTabctl7Material} />
              <ControlSelect label="Color mode" value={tabctl7ColorMode} options={tabctl7ColorModes} onChange={setTabctl7ColorMode} />
              <ControlSelect label="Alcance" value={tabctl7Scope} options={tabctl7Scopes} onChange={setTabctl7Scope} />
              <ControlSelect label="Herencia" value={tabctl7Inheritance} options={tabctl7InheritanceModes} onChange={setTabctl7Inheritance} />
            </div>
            <div className={styles.tabctl7RoleCard}><strong>{tabctl7CurrentRole.role}</strong><span>{tabctl7CurrentRole.kind} · {tabctl7CurrentRole.part}</span><p>{tabctl7CurrentRole.help}</p><small>{tabctl7MaterialSpec.label}: {tabctl7MaterialSpec.description}</small></div>
            <div className={styles.tabctl7ContextBar} aria-label="Resumen de target TABCTL7"><span>{tabctl7CurrentLayer.layer}</span><span>{tabctl7CurrentRole.kind}</span><span>{tabctl7Change}</span><span>{tabctl7Scope}</span><span>{tabctl7ZeroSummary}</span></div>
            <div className={styles.tabctl7ControlCloud} aria-label="Controles aplicables TABCTL7">
              {tabctl7VisibleControls.length === 0 ? <em>Este cambio no aplica a este rol; cambia rol o tipo de cambio.</em> : tabctl7VisibleControls.slice(0, 14).map((control) => (<button key={`${control.key}-${control.effectGroup}`} type="button" className={styles.tabctl7ControlChip} onClick={() => setEffectGroup(control.effectGroup)} title={control.help}>{control.label}<small>{control.effectGroup}</small></button>))}
            </div>
            <div className={styles.tabctl7SuggestionRow}><span>{tabctl7VisibleControls.length} controles aplicables</span><span>{tabctl7SuggestedEffects.length ? `packs: ${tabctl7SuggestedEffects.join(" · ")}` : "sin pack activo"}</span></div>
          </div>

          <div className={styles.knobPanel} data-component="CompactKnobPanel" data-effect-group={effectGroup}>
            <div className={styles.panelHeader}>
              <strong>{effectGroup} controls</strong>
              <span>{activeKnobCount}/{currentKnobItems.length} activas · {storageStatus}</span>
            </div>
            <div className={styles.applicabilityHint} data-component="EffectApplicabilityHint">
              <strong>{widgetGroup}</strong>
              <span>{effectGroup}</span>
              <small>Las perillas sin target declarado quedan visibles pero no editables para evitar controles de humo.</small>
            </div>
            <div className={styles.knobGrid}>
              {currentKnobItems.map((item) => {
                const active = knobAppliesToWidget(item.key, widgetGroup);
                const targets = knobRule(item.key)?.targets ?? [];
                return (
                  <Knob
                    key={item.key}
                    item={item}
                    value={knobs[item.key]}
                    active={active}
                    scope={active ? `Aplica a ${widgetGroup}` : `Sin impacto en ${widgetGroup}. Targets: ${targets.join(", ")}`}
                    onChange={(value) => updateKnob(item.key, value)}
                  />
                );
              })}
            </div>
            <ControlSelect label="Widget preview" value={widgetGroup} options={widgetGroups} onChange={setWidgetGroup} />
            <ControlSelect label="Background" value={backgroundMode} options={["Frozen atmospheric", "Tiny parallax", "Soft washed", "Veil heavy", "Glass contrast"]} onChange={setBackgroundMode} />
            <div className={styles.knobActions}>
              <button className={styles.primaryAction} onClick={savePreset}>Guardar preset</button>
              <button className={styles.ghostAction} onClick={() => copyRecipe()}>Copiar JSON</button>
            </div>
          </div>
        </aside>

        <section className={styles.previewCanvas} data-component="AtmosphericFixedCanvas" data-background-mode={backgroundMode} data-widget-group={widgetGroup}>
          <div className={styles.canvasBackground} aria-hidden="true" />
          <div className={styles.previewHeader}>
            <div><span>{section}</span><h2>{widgetGroup}</h2></div>
            <p>{viewport} · {stateMode} · tone {tone}</p>
          </div>
          <div className={styles.previewScroller}><WidgetPreview group={widgetGroup} /></div>
        </section>
      </div>

      <section className={styles.savedPanel} data-component="SavedPresetTable" data-saved-preset-count={saved.length}>
        <button className={styles.savedToggle} aria-expanded={savedOpen} onClick={() => setSavedOpen((value) => !value)}>
          <span>Saved presets</span><b>{saved.length}</b><em>{savedOpen ? "Cerrar" : "Abrir"}</em>
        </button>
        {savedOpen && (
          <div className={styles.savedTableWrap}>
            <table className={styles.savedTable}>
              <thead><tr><th>Nombre</th><th>Base</th><th>Widget group</th><th>Target</th><th>Material</th><th>Tone</th><th>Alpha</th><th>Blur</th><th>Density</th><th>Cols</th><th>Fecha</th><th>Acciones</th></tr></thead>
              <tbody>
                {saved.length === 0 ? <tr><td colSpan={12}>Sin presets guardados todavía. Ajusta perillas y toca “Guardar preset”.</td></tr> : saved.map((item) => (
                  <tr key={item.id} data-saved-preset={item.id}>
                    <td>{item.name}</td><td>{item.basePreset}</td><td>{item.widgetGroup}</td><td>{item.tabctl7Role ?? "—"}</td><td>{item.tabctl7MaterialLabel ?? item.tabctl7Material ?? "—"}</td><td>{item.tone}</td><td>{item.glassAlpha}%</td><td>{item.blur}px</td><td>{item.density}</td><td>{item.columns}</td><td>{new Date(item.updatedAt).toLocaleDateString()}</td>
                    <td className={styles.rowActions}><button onClick={() => applyPreset(item)} aria-label={`Aplicar ${item.name}`}>Aplicar</button><button onClick={() => duplicatePreset(item)} aria-label={`Duplicar ${item.name}`}>Duplicar</button><button onClick={() => copyRecipe(item)} aria-label={`Copiar JSON de ${item.name}`}>JSON</button><button onClick={() => deletePreset(item.id)} aria-label={`Eliminar ${item.name}`}>🗑</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {saved.length > 0 && <button className={styles.dangerAction} onClick={clearPresets}>Limpiar presets</button>}
          </div>
        )}
      </section>

      <BottomNav />
    </section>
  );
}
