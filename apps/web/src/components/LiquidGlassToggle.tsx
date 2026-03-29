/* HITECH_LIQUID_GLASS_TOGGLE_MINI */
import * as React from "react";

type Props = {
  value?: boolean;
  onChange?: (next: boolean) => void;
  title?: string;
};

export function LiquidGlassToggleMini(props: Props) {
  const { value, onChange, title } = props;
  const [internal, setInternal] = React.useState(false);
  const isControlled = typeof value === "boolean";
  const on = isControlled ? (value as boolean) : internal;

  function toggle() {
    const next = !on;
    if (!isControlled) setInternal(next);
    onChange?.(next);
  }

  return (
    <button
      className="lg-mini"
      type="button"
      aria-pressed={on}
      onClick={toggle}
      title={title ?? "Toggle"}
    >
      <span className="lg-mini-blob" aria-hidden="true" />
      <span className="lg-mini-glass" aria-hidden="true" />
      <span className="lg-mini-thumb" aria-hidden="true" />
    </button>
  );
}
