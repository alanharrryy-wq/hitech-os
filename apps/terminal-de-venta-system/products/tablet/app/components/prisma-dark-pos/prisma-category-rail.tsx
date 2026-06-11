"use client";

import { useState } from "react";
import { categories } from "./prisma-dark-pos-data";
import { PrismaIcon } from "./prisma-dark-pos-icons";
import styles from "./prisma-dark-pos.module.css";

function emitCategoryAction(action: string, label?: string) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent("prisma:pos-category-action", {
    detail: { action, label, source: "prisma-dark-pos-category-rail", ts: new Date().toISOString() }
  }));
}

export function PrismaCategoryRail() {
  const [activeLabel, setActiveLabel] = useState(categories.find((category) => category.active)?.label ?? categories[0]?.label ?? "");

  return (
    <section className={styles.categoryRail} aria-label="Categorías" data-prisma-hardening="category-actions-260611">
      {categories.map((category) => {
        const isActive = activeLabel === category.label;
        return (
          <button
            key={category.label}
            className={isActive ? styles.categoryActive : styles.categoryItem}
            type="button"
            aria-pressed={isActive}
            onClick={() => { setActiveLabel(category.label); emitCategoryAction("select", category.label); }}
          >
            <span className={styles.categoryCircle}>
              <PrismaIcon name={category.icon} size={22} />
            </span>
            <span className={styles.categoryLabel}>{category.label}</span>
          </button>
        );
      })}

      <button className={styles.categoryNext} type="button" aria-label="Ver más categorías" onClick={() => emitCategoryAction("more")}>
        <span className={styles.categoryCircle}>
          <PrismaIcon name="arrow-right" size={21} />
        </span>
      </button>
    </section>
  );
}
