import { forwardRef, useCallback, type ButtonHTMLAttributes, type KeyboardEvent } from "react";
import { cn } from "../../../lib/cn.js";
import { FOCUS_RING_CLASS } from "../../../lib/focus-ring.js";

export interface ToggleSwitchProps
  extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "onChange" | "role"> {
  readonly checked: boolean;
  readonly onCheckedChange: (next: boolean) => void;
  readonly label?: string;
}

export const ToggleSwitch = forwardRef<HTMLButtonElement, ToggleSwitchProps>(function ToggleSwitch(
  { className, checked, onCheckedChange, disabled = false, label, id, onKeyDown, ...props },
  ref
) {
  const toggle = useCallback(() => {
    if (!disabled) {
      onCheckedChange(!checked);
    }
  }, [checked, disabled, onCheckedChange]);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent<HTMLButtonElement>) => {
      onKeyDown?.(event);
      if (event.defaultPrevented) {
        return;
      }

      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    },
    [onKeyDown, toggle]
  );

  return (
    <button
      ref={ref}
      id={id}
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      disabled={disabled}
      className={cn("ui-toggle-switch", FOCUS_RING_CLASS, className)}
      data-state={checked ? "on" : "off"}
      onClick={toggle}
      onKeyDown={handleKeyDown}
      {...props}
    >
      <span className="ui-toggle-switch__thumb" aria-hidden="true" />
    </button>
  );
});
