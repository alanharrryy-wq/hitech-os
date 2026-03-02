import { useId, useMemo, type ChangeEvent } from "react";
import { cn } from "../../../lib/cn.js";

export interface SliderProps {
  readonly id?: string;
  readonly label?: string;
  readonly min?: number;
  readonly max?: number;
  readonly step?: number;
  readonly value: number;
  readonly onValueChange: (value: number) => void;
  readonly detents?: readonly number[];
  readonly showValue?: boolean;
  readonly disabled?: boolean;
  readonly className?: string;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function Slider({
  id,
  label,
  min = 0,
  max = 100,
  step = 1,
  value,
  onValueChange,
  detents,
  showValue = true,
  disabled = false,
  className
}: SliderProps) {
  const generatedId = useId();
  const controlId = id ?? `ui-slider-${generatedId}`;

  const safeValue = clamp(value, min, max);
  const progress = ((safeValue - min) / Math.max(max - min, 1)) * 100;

  const normalizedDetents = useMemo(() => {
    if (!detents || detents.length === 0) {
      return [] as number[];
    }

    return detents
      .map((entry) => clamp(entry, min, max))
      .sort((left, right) => left - right);
  }, [detents, max, min]);

  return (
    <div className={cn("ui-slider", className)} style={{ ["--ui-slider-detents" as string]: normalizedDetents.length || 1 }}>
      {(label || showValue) ? (
        <div className="flex items-center justify-between gap-2">
          {label ? (
            <label htmlFor={controlId} className="text-xs font-semibold uppercase tracking-[0.08em] text-[hsl(var(--ui-text-3))]">
              {label}
            </label>
          ) : <span />}
          {showValue ? <output className="text-xs font-semibold text-[hsl(var(--ui-text-2))]">{safeValue}</output> : null}
        </div>
      ) : null}

      <div className="ui-slider__track" aria-hidden="true">
        <div
          className="absolute inset-y-0 left-0 rounded-full ui-premium-gradient-043"
          style={{ width: `${progress}%` }}
        />
      </div>

      <input
        id={controlId}
        type="range"
        min={min}
        max={max}
        step={step}
        value={safeValue}
        disabled={disabled}
        className="w-full accent-[hsl(var(--ui-accent))]"
        onChange={(event: ChangeEvent<HTMLInputElement>) => {
          onValueChange(Number(event.currentTarget.value));
        }}
      />

      {normalizedDetents.length > 0 ? (
        <div className="ui-slider__detents" aria-hidden="true">
          {normalizedDetents.map((entry) => (
            <span key={entry} className="ui-slider__detent" />
          ))}
        </div>
      ) : null}
    </div>
  );
}
