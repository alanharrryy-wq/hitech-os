import type { ReactNode } from "react";
import styles from "./prisma-command-dock.module.css";

type PrismaCommandDockProps = {
  children: ReactNode;
  className?: string;
  [key: string]: any;
};

export function PrismaCommandDock({ children, className, ...props }: PrismaCommandDockProps) {
  const classes = className ? `${styles.dock} ${className}` : styles.dock;

  return (
    <nav {...props} className={classes} data-prisma-component="PrismaCommandDock" data-prisma-effect="dock-active-glow">
      {children}
    </nav>
  );
}
