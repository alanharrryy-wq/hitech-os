import "./{{COMPONENT_NAME}}.styles.css";
import { useId } from "react";

export interface {{COMPONENT_NAME}}Props {
  readonly label: string;
  readonly checked: boolean;
  readonly onChange: (next: boolean) => void;
  readonly disabled?: boolean;
  readonly hint?: string;
}

export function {{COMPONENT_NAME}}(props: {{COMPONENT_NAME}}Props): JSX.Element {
  const { label, checked, onChange, disabled = false, hint } = props;
  const id = useId();
  return (
    <label className="{{component_name}}-root" htmlFor={id} data-control-kind="{{CONTROL_KIND}}">
      <span className="{{component_name}}-copy">
        <span className="{{component_name}}-label">{label}</span>
        {hint ? <span className="{{component_name}}-hint">{hint}</span> : null}
      </span>
      <input
        id={id}
        className="{{component_name}}-input"
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onChange={(event) => onChange(event.currentTarget.checked)}
      />
      <span className="{{component_name}}-track" aria-hidden="true">
        <span className="{{component_name}}-thumb" />
      </span>
    </label>
  );
}

