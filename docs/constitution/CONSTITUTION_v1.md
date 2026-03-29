# HITECH OS — CONSTITUTION v1.0 (DRAFT)
**Generated:** 2026-03-01 07:06:54 America/Mexico_City  
**Status:** DRAFT (No enforcement)  
**Principle:** *Menos fricción, más sistema, cero paja.*

---

## 0) Invariants (Do Not Change)
### PROJECT_REASON (Invariable)
Construir un sistema operativo visual y técnico que permita crear productos premium, gobernados, escalables y hermosos sin colapsar a escala.

### FINAL_GOAL (Invariable)
Un sistema híbrido estructural + experiencial que combine:
- Arquitectura de tokens escalable (3 capas)
- Gobernanza técnica progresiva (lint → deprecations → enforcement)
- QA visual estabilizado
- Premium white UI con glass inteligente y glow sutil
- Dashboard intelligence estructurado (overview → filter → details + historia)
- Tooling **OFF BY DEFAULT** hasta aprobar Constitución.

### ANTI-GOALS (Ley)
- No rediseño superficial sin estructura.
- No enforcement antes de Constitución.
- No blur/glow como decoración vacía.
- No burocracia.

---

## 1) Identity — The Hybrid System (Architectural DNA)
HITECH OS es un sistema **híbrido estratificado**:

### Layer A — Base (Values)
Valores puros: color, spacing, typography, radii, motion primitives.  
**Regla:** Base no referencia nada.

### Layer B — Semantic (Intent)
Tokens de intención que referencian Base.  
Ej: `surface.primary`, `text.muted`, `motion.enter`.

### Layer C — Component Contracts
Tokens específicos por componente que referencian Semantics.  
Ej: `Card.surface`, `Button.focusGlow`.

**Reglas duras:**
- Component **NO** referencia Base.
- Semantic **NO** referencia Component.
- Inline values están prohibidos fuera de prototipos.

La taxonomía canónica vive en **Tables as Law** (`docs/constitution/tables/TBL_*.json`).

---

## 2) Modularity & Expansion Law
Cada componente debe:
- Estar encapsulado (API clara)
- Ser localizable por nombre
- Poder crecer **10x LOC** sin romper el resto

**Prohibido:** lógica cruzada sin contrato.

---

## 3) Premium White System (Experience Constitution)
### 3.1 White Premium (No es “blanco”)
White premium = jerarquía por luz, aire estructurado, contraste suave pero firme.

### 3.2 Glass Inteligente (Permitido con intención)
**Glass solo cuando:**
- Existe elevación real (no decorativa)
- No compite con el contenido
- Tiene límites de blur, saturación y contraste

**Prohibido:** glass como wallpaper.

### 3.3 Glow Sutil (Solo señalización)
Glow se usa únicamente para:
- Focus
- Estado activo
- Señalización crítica

**Prohibido:** glow para “hacerlo ver fancy”.

### 3.4 Motion Funcional (No ornamental)
Motion debe:
- Explicar jerarquía
- Indicar transición lógica
- Reforzar intención

**Reduced motion:** obligatorio (modo estable).

---

## 4) Dashboard Intelligence (Narrative Contract)
Todo dashboard HOS sigue el orden estructural:
1) **Overview** — KPIs + estado
2) **Filter** — control/segmentación
3) **Details** — drilldown + historia

**Regla:** el sistema guía; el usuario no “caza” datos.

---

## 5) Visual QA & VRT (Stability Constitution)
- Baselines explícitos
- Pixel strict (por default cuando VRT esté activo)
- Ignore dinámicos declarados (no “tolerancia escondida”)
- Motion deshabilitado en snapshots
- Reduced motion always-on en QA

---

## 6) Governance Activation Order (OFF by default)
La escalera oficial de gobernanza:
1) Lint Warning
2) Deprecation Notice
3) Build Warning
4) Build Error
5) Codemod Required

**Ley:** Nada se vuelve blocking hasta que esta Constitución pase a **ACTIVE**.

---

## 7) Tables as Law (Machine-Executable)
Las tablas son contratos JSON versionados:
- Source of truth: `docs/constitution/tables/<TABLE_ID>.json`
- Schema: `docs/constitution/tables/_schema/table_spec.schema.json`
- Validator: `tools/hos/constitution/validate_tables.py`
- Render: `tools/hos/constitution/render_tables_md.py`

---

## 8) Change Management (SemVer + Deprecations)
- Cambios breaking → bump de major
- Deprecation primero, enforcement después
- Codemods recomendados para migraciones

---

## 9) Short-Term Goals / Current Objectives (EN)
- Define the hybrid architectural identity of HITECH OS (DONE in this constitution).
- Write the formal Constitution v1 (this document) and approve it.
- Establish governance activation order and keep enforcement OFF by default.
- Design the white premium blueprint for Keystone as the initial lab.
- Formalize dashboard intelligence layer and VRT policy.

---

## Appendix A — Registry
Ver `docs/constitution/tables/REGISTRY.json` para el listado canónico de tablas.

## Appendix B — Rendered Tables
Ver `docs/constitution/TABLES_RENDERED.md` (generado desde JSON).
