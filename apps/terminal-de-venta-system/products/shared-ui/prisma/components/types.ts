import type { ReactNode } from "react";
export type PrismaSurface = "tablet" | "pc" | "mobile" | "chart-lab" | "kiosk" | "customer-display" | "warehouse-scanner" | "manager-console" | "training-mode" | "demo-mode" | "public-display";
export type PrismaTone = "default" | "success" | "warning" | "danger" | "info";

type PrismaDomProps = {
  className?: string;
  id?: string;
  role?: string;
  tabIndex?: number;
  href?: string;
  type?: "button" | "submit" | "reset";
  disabled?: boolean;
  "aria-label"?: string;
  "aria-live"?: "off" | "polite" | "assertive";
  onClick?: (...args: any[]) => void;
  [key: string]: any;
};

export type PrismaBaseProps<T extends HTMLElement = HTMLElement> = PrismaDomProps & { surface?: PrismaSurface; tone?: PrismaTone; title?: ReactNode; eyebrow?: ReactNode; children?: ReactNode; };
export type PrismaActionButtonProps = PrismaDomProps & { href?: string; surface?: PrismaSurface; tone?: PrismaTone; children?: ReactNode; };
export function cx(...parts: Array<string | false | null | undefined>): string { return parts.filter(Boolean).join(" "); }
