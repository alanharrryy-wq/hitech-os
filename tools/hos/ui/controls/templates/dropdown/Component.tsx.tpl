import "./{{COMPONENT_NAME}}.styles.css";
import { useId } from "react";

export interface {{COMPONENT_NAME}}Option {
  readonly value: string;
  readonly label: string;
}

export interface {{COMPONENT_NAME}}Props {
  readonly label: string;
  readonly value: string;
  readonly options: readonly {{COMPONENT_NAME}}Option[];
  readonly onChange: (next: string) => void;
  readonly hint?: string;
}

export function {{COMPONENT_NAME}}(props: {{COMPONENT_NAME}}Props): JSX.Element {
  const { label, value, options, onChange, hint } = props;
  const id = useId();
  return (
    <label className="{{component_name}}-root" htmlFor={id} data-control-kind="{{CONTROL_KIND}}">
      <span className="{{component_name}}-label">{label}</span>
      {hint ? <span className="{{component_name}}-hint">{hint}</span> : null}
      <select
        id={id}
        className="{{component_name}}-select"
        value={value}
        onChange={(event) => onChange(event.currentTarget.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

