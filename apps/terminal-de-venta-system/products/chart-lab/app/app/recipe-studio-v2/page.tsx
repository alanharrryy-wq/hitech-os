"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "./prisma-recipe-studio-v2.module.css";

type RecipeKey = "chart" | "visual" | "motion" | "background" | "surface";

type StudioState = Record<RecipeKey, string>;

const RECIPE_ENDPOINTS: Record<RecipeKey, string> = {
  chart: "/surface-visual-governor/recipe-export/latest/chart.recipe.json",
  visual: "/surface-visual-governor/recipe-export/latest/visual.recipe.json",
  motion: "/surface-visual-governor/recipe-export/latest/motion.recipe.json",
  background: "/surface-visual-governor/recipe-export/latest/background.recipe.json",
  surface: "/surface-visual-governor/recipe-export/latest/surface.compatibility.json"
};

const DEFAULT_TEXT: StudioState = {
  chart: "{}",
  visual: "{}",
  motion: "{}",
  background: "{}",
  surface: "{}"
};

const DENIED_PUBLIC_TERMS = ["F:" + "\\", "C:" + "\\", "." + "sqlite", "." + "sqlite3", "tablet" + "-pos" ];
const POS_DENIED_TERMS = ["storm-cloud-operations-real.jpg", "obsidian-cloud-motion.svg", "webgl", "pixi", "@react-three", "backdrop-filter", "blur("];

function prettyJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function validateRecipe(key: RecipeKey, text: string) {
  const findings: string[] = [];
  const warnings: string[] = [];
  let parsed: unknown = null;

  try {
    parsed = JSON.parse(text);
  } catch (error) {
    findings.push(`Invalid JSON in ${key}: ${(error as Error).message}`);
  }

  const lower = text.toLowerCase();
  for (const term of DENIED_PUBLIC_TERMS) {
    if (lower.includes(term.toLowerCase())) {
      findings.push(`Public recipe leak guard blocked term: ${term}`);
    }
  }

  if (key === "surface") {
    for (const term of POS_DENIED_TERMS) {
      if (lower.includes(term.toLowerCase()) && !lower.includes("denied") && !lower.includes("blocked")) {
        findings.push(`POS/checkout budget guard saw active unsafe term: ${term}`);
      }
    }
  }

  if (key === "background" && lower.includes("storm-cloud-operations-real.jpg")) {
    warnings.push("Storm atmosphere is allowed only for reference/demo/chart-lab contexts, never POS/checkout active shells.");
  }

  return {
    key,
    status: findings.length ? "FAIL" : "PASS",
    findings,
    warnings,
    parsedType: parsed && typeof parsed === "object" ? "object" : typeof parsed
  };
}

export default function RecipeStudioV2Page() {
  const [active, setActive] = useState<RecipeKey>("visual");
  const [recipes, setRecipes] = useState<StudioState>(DEFAULT_TEXT);
  const [loadStatus, setLoadStatus] = useState("Ready to load Chart Lab recipe export.");

  useEffect(() => {
    let cancelled = false;
    async function loadRecipes() {
      setLoadStatus("Loading latest recipe export…");
      const next: StudioState = { ...DEFAULT_TEXT };
      for (const key of Object.keys(RECIPE_ENDPOINTS) as RecipeKey[]) {
        try {
          const response = await fetch(RECIPE_ENDPOINTS[key], { cache: "no-store" });
          if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
          const json = await response.json();
          next[key] = prettyJson(json);
        } catch (error) {
          next[key] = prettyJson({
            schema: "prisma.surface.visual.governor.recipe-studio-v2.fallback",
            key,
            warning: `Could not load ${RECIPE_ENDPOINTS[key]}`,
            message: String((error as Error).message || error)
          });
        }
      }
      if (!cancelled) {
        setRecipes(next);
        setLoadStatus("Loaded latest recipe export. Validate before copy/export.");
      }
    }
    loadRecipes();
    return () => { cancelled = true; };
  }, []);

  const validations = useMemo(() => {
    return (Object.keys(recipes) as RecipeKey[]).map((key) => validateRecipe(key, recipes[key]));
  }, [recipes]);

  const activeValidation = validations.find((item) => item.key === active);
  const passCount = validations.filter((item) => item.status === "PASS").length;
  const failCount = validations.filter((item) => item.status === "FAIL").length;

  async function copyBundle() {
    const bundle = {
      schema: "prisma.surface.visual.governor.chart_lab.recipe_studio_v2.bundle",
      created_by: "Chart Lab Recipe Studio V2",
      governor: "route budget enforcer compatible",
      status: failCount ? "needs_review" : "ready_for_governed_export",
      recipes: Object.fromEntries(
        (Object.keys(recipes) as RecipeKey[]).map((key) => {
          try { return [key, JSON.parse(recipes[key])]; }
          catch { return [key, { parse_error: true, raw: recipes[key] }]; }
        })
      ),
      validation: validations
    };
    await navigator.clipboard.writeText(prettyJson(bundle));
    setLoadStatus("Copied governed recipe bundle to clipboard.");
  }

  return (
    <main className={styles.shell} data-governor="recipe-studio-v2 route-budget-enforcer chart-lab">
      <section className={styles.hero}>
        <div>
          <p className={styles.eyebrow}>PRISMA Surface Visual Governor · Chart Lab</p>
          <h1>Recipe Studio V2</h1>
          <p>
            Edita, valida y empaqueta recetas del Chart Lab antes de promoverlas a PC, Tablet, Mobile, POS o Checkout.
            El taller ya no vende pintura al tanteo: ahora pesa la cubeta y revisa el recibo.
          </p>
        </div>
        <div className={styles.scoreCard} aria-label="Route budget enforcer summary">
          <span>{passCount} PASS</span>
          <strong>{failCount} FAIL</strong>
          <small>{loadStatus}</small>
        </div>
      </section>

      <section className={styles.grid}>
        <aside className={styles.rail} aria-label="Recipe selector">
          {(Object.keys(RECIPE_ENDPOINTS) as RecipeKey[]).map((key) => (
            <button
              key={key}
              className={active === key ? styles.activeButton : styles.recipeButton}
              onClick={() => setActive(key)}
              type="button"
            >
              <span>{key}.recipe</span>
              <small>{validations.find((item) => item.key === key)?.status || "PENDING"}</small>
            </button>
          ))}
          <button className={styles.copyButton} onClick={copyBundle} type="button">
            Copy governed bundle
          </button>
        </aside>

        <section className={styles.editorPanel}>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.eyebrow}>Active recipe</p>
              <h2>{active}.recipe.json</h2>
            </div>
            <span className={activeValidation?.status === "PASS" ? styles.passPill : styles.failPill}>
              {activeValidation?.status || "PENDING"}
            </span>
          </div>
          <textarea
            className={styles.editor}
            spellCheck={false}
            value={recipes[active]}
            onChange={(event) => setRecipes((current) => ({ ...current, [active]: event.target.value }))}
            aria-label={`${active} recipe JSON editor`}
          />
        </section>

        <aside className={styles.auditPanel} aria-label="Route budget audit">
          <p className={styles.eyebrow}>Route Budget Enforcer</p>
          <h2>Validation</h2>
          <div className={styles.validationList}>
            {validations.map((item) => (
              <article key={item.key} className={item.status === "PASS" ? styles.passBox : styles.failBox}>
                <strong>{item.key}</strong>
                <span>{item.status}</span>
                {item.findings.length ? <p>{item.findings.join(" · ")}</p> : <p>Budget-safe JSON. No public leak tokens.</p>}
                {item.warnings.map((warning) => <small key={warning}>{warning}</small>)}
              </article>
            ))}
          </div>
        </aside>
      </section>
    </main>
  );
}
