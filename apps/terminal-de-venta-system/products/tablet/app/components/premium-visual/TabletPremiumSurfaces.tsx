
import type { ComponentPropsWithoutRef, ElementType, ReactNode } from "react";
import { Slot } from "@radix-ui/react-slot";
import { motion } from "motion/react";
import styles from "./tablet-premium-surfaces.module.css";

type SurfaceTone = "panel" | "card" | "liquid" | "pill" | "banner";

type SurfaceProps<T extends ElementType> = {
  as?: T;
  tone?: SurfaceTone;
  children: ReactNode;
  className?: string;
} & Omit<ComponentPropsWithoutRef<T>, "as" | "children" | "className">;

function joinClassNames(...values: Array<string | undefined | false>) {
  return values.filter(Boolean).join(" ");
}

export function TabletBackgroundAwareSurface<T extends ElementType = "section">({
  as,
  tone = "panel",
  className,
  children,
  ...props
}: SurfaceProps<T>) {
  const Tag = (as ?? "section") as ElementType;
  return (
    <Tag
      className={joinClassNames(styles.surface, styles[tone], className)}
      data-prisma-component="TabletBackgroundAwareSurface"
      data-prisma-recipe={`tablet-${tone}`}
      {...props}
    >
      <span className={styles.edgeGlow} aria-hidden="true" />
      {children}
    </Tag>
  );
}

export function TabletSurfacePanel(props: Omit<SurfaceProps<"section">, "tone">) {
  return <TabletBackgroundAwareSurface as="section" tone="panel" {...props} />;
}

export function TabletGlassCard({ className, ...props }: Omit<SurfaceProps<"article">, "tone">) {
  return (
    <motion.article
      className={joinClassNames(styles.surface, styles.card, className)}
      data-prisma-component="TabletGlassCard"
      data-prisma-recipe="operational-card"
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.992 }}
      transition={{ duration: 0.16 }}
      {...props}
    />
  );
}

export function TabletStateBanner(props: Omit<SurfaceProps<"aside">, "tone">) {
  return <TabletBackgroundAwareSurface as="aside" tone="banner" {...props} />;
}

export function TabletActionButton({
  asChild,
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<typeof motion.button> & { asChild?: boolean; children: ReactNode }) {
  const Comp = asChild ? Slot : motion.button;
  return (
    <Comp
      className={joinClassNames(styles.actionButton, className)}
      data-prisma-component="TabletActionButton"
      data-prisma-recipe="action-button"
      whileHover={asChild ? undefined : { y: -1 }}
      whileTap={asChild ? undefined : { scale: 0.985 }}
      transition={asChild ? undefined : { duration: 0.14 }}
      {...props}
    >
      {children}
    </Comp>
  );
}

export function TabletRouteFrame({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={joinClassNames(styles.routeFrame, className)} data-prisma-component="TabletRouteFrame">
      {children}
    </div>
  );
}

export function TabletLayerBudget({ children }: { children: ReactNode }) {
  return <div className={styles.layerBudget} data-prisma-layer-budget="tablet-premium-library-effects-1006">{children}</div>;
}
