import type { ImgHTMLAttributes } from "react";
import { cn } from "@hitech/ui-kit";

export interface HitechLogoProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, "src" | "alt"> {
  readonly alt?: string;
}

export function HitechLogo({ className, alt = "HITECH", ...props }: HitechLogoProps) {
  return (
    <img
      src="/brand/hitech-logo.svg"
      alt={alt}
      className={cn("hitech-logo h-9 w-auto", className)}
      decoding="async"
      loading="eager"
      {...props}
    />
  );
}
