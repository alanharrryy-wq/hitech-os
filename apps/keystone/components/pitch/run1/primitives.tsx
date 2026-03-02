"use client";

import type { ReactNode } from "react";
import {
  Badge,
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
  cn
} from "@hitech/ui-kit";

export interface NeonButtonProps {
  readonly children: ReactNode;
  readonly disabled?: boolean;
  readonly onClick?: () => void;
  readonly variant?: "solid" | "outline" | "subtle" | "ghost";
  readonly className?: string;
}

export function NeonButton({
  children,
  disabled,
  onClick,
  variant = "solid",
  className
}: NeonButtonProps) {
  return (
    <Button
      variant={variant}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        "transition-all duration-200",
        "shadow-[0_0_0_0_hsl(var(--ui-accent)/0)] hover:shadow-[0_0_20px_hsl(var(--ui-accent)/0.35)]",
        "active:scale-[0.98]",
        className
      )}
    >
      {children}
    </Button>
  );
}

export interface ChipProps {
  readonly children: ReactNode;
  readonly tone?: "neutral" | "accent" | "success" | "warning" | "danger";
  readonly className?: string;
}

export function Chip({ children, tone = "neutral", className }: ChipProps) {
  return (
    <Badge
      tone={tone}
      className={cn(
        "rounded-full border border-[hsl(var(--ui-border-1))] px-2.5 py-1 text-[11px] tracking-[0.04em]",
        className
      )}
    >
      {children}
    </Badge>
  );
}

export interface ToggleProps {
  readonly checked: boolean;
  readonly onChange: (next: boolean) => void;
  readonly label: string;
  readonly disabled?: boolean;
}

export function Toggle({ checked, onChange, label, disabled = false }: ToggleProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={cn(
        "group flex items-center gap-3 rounded-md border border-[hsl(var(--ui-border-1))] bg-[hsl(var(--ui-surface-1)/0.85)] px-3 py-2 text-left transition-all",
        "hover:border-[hsl(var(--ui-accent)/0.5)]",
        disabled ? "cursor-not-allowed opacity-60" : "cursor-pointer"
      )}
    >
      <span
        className={cn(
          "relative inline-flex h-5 w-9 items-center rounded-full transition-colors duration-200",
          checked ? "bg-[hsl(var(--ui-accent))]" : "bg-[hsl(var(--ui-surface-3))]"
        )}
      >
        <span
          className={cn(
            "absolute left-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform duration-200",
            checked ? "translate-x-4" : "translate-x-0"
          )}
        />
      </span>
      <span className="text-xs font-medium text-[hsl(var(--ui-text-1))]">{label}</span>
    </button>
  );
}

export interface DropdownOption {
  readonly value: string;
  readonly label: string;
}

export interface DropdownFieldProps {
  readonly label: string;
  readonly value: string;
  readonly options: readonly DropdownOption[];
  readonly onValueChange: (value: string) => void;
}

export function DropdownField({ label, value, options, onValueChange }: DropdownFieldProps) {
  return (
    <label className="grid gap-1.5">
      <span className="text-[11px] uppercase tracking-[0.09em] text-[hsl(var(--ui-text-3))]">
        {label}
      </span>
      <Select value={value} onValueChange={onValueChange}>
        <SelectTrigger>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </label>
  );
}

export interface InfoTooltipProps {
  readonly trigger: ReactNode;
  readonly content: ReactNode;
}

export function InfoTooltip({ trigger, content }: InfoTooltipProps) {
  return (
    <TooltipProvider delayDuration={120}>
      <Tooltip>
        <TooltipTrigger asChild>{trigger}</TooltipTrigger>
        <TooltipContent sideOffset={6}>{content}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
