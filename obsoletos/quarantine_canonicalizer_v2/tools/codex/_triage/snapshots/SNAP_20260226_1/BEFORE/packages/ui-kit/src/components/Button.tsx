import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({ children, className, variant = "primary", ...rest }: PropsWithChildren<ButtonProps>) {
  const classes = ["ui-button", `ui-button--${variant}`, className].filter(Boolean).join(" ");

  return (
    <button className={classes} {...rest}>
      {children}
    </button>
  );
}
