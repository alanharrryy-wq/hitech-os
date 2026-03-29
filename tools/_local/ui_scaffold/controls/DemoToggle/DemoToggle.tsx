import "./DemoToggle.styles.css";
import { useId } from "react";

export interface DemoToggleProps {
  readonly label: string;
  readonly checked: boolean;
  readonly onChange: (next: boolean) => void;
  readonly disabled?: boolean;
  readonly hint?: string;
}

export function DemoToggle(props: DemoToggleProps): JSX.Element {
  const { label, checked, onChange, disabled = false, hint } = props;
  const id = useId();
  return (
    <label className="demotoggle-root" htmlFor={id} data-control-kind="toggle">
      <span className="demotoggle-copy">
        <span className="demotoggle-label">{label}</span>
        {hint ? <span className="demotoggle-hint">{hint}</span> : null}
      </span>
      <input
        id={id}
        className="demotoggle-input"
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.currentTarget.checked)}
      />
      <span className="demotoggle-track" aria-hidden="true">
        <span className="demotoggle-thumb" />
      </span>
    </label>
  );
}

