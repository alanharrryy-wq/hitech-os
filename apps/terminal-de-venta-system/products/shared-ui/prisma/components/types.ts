import type { AnchorHTMLAttributes, ButtonHTMLAttributes, HTMLAttributes, ReactNode } from "react";
export type PrismaSurface = "tablet" | "pc" | "mobile" | "chart-lab" | "kiosk" | "customer-display" | "warehouse-scanner" | "manager-console" | "training-mode" | "demo-mode" | "public-display";
export type PrismaTone = "default" | "success" | "warning" | "danger" | "info";
export type PrismaBaseProps<T extends HTMLElement = HTMLElement> = HTMLAttributes<T> & { surface?: PrismaSurface; tone?: PrismaTone; title?: ReactNode; eyebrow?: ReactNode; children?: ReactNode; };
export type PrismaActionButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & AnchorHTMLAttributes<HTMLAnchorElement> & { href?: string; surface?: PrismaSurface; tone?: PrismaTone; children?: ReactNode; };
export function cx(...parts: Array<string | false | null | undefined>): string { return parts.filter(Boolean).join(" "); }
