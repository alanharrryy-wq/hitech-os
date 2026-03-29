.{{component_name}}-root {
  --bg: var(--ui-surface-1, rgba(255, 255, 255, 0.95));
  --fg: var(--ui-text-1, rgba(16, 24, 40, 1));
  --muted: var(--ui-text-2, rgba(71, 84, 103, 1));
  --border: var(--ui-border-1, rgba(208, 213, 221, 0.85));
  --accent: hsl(var(--ui-accent, 222 89% 55%));
  --radius: var(--ui-core-radius-md, 12px);
  --space: var(--ui-core-space-3, 12px);
  --space-xs: var(--ui-core-space-2, 8px);
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: var(--space);
  color: var(--fg);
}

.{{component_name}}-copy {
  display: grid;
  gap: var(--space-xs);
}

.{{component_name}}-label {
  font-size: 0.95rem;
  font-weight: 600;
}

.{{component_name}}-hint {
  font-size: 0.8rem;
  color: var(--muted);
}

.{{component_name}}-input {
  position: absolute;
  inline-size: 1px;
  block-size: 1px;
  opacity: 0;
  pointer-events: none;
}

.{{component_name}}-track {
  inline-size: 46px;
  block-size: 26px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--bg);
  display: inline-flex;
  align-items: center;
  padding: 2px;
  transition: all var(--ui-core-duration-fast, 120ms) ease;
}

.{{component_name}}-thumb {
  inline-size: 20px;
  block-size: 20px;
  border-radius: 50%;
  background: white;
  box-shadow: var(--ui-shadow-1, 0 6px 16px rgba(15, 23, 42, 0.12));
  transform: translateX(0);
  transition: transform var(--ui-core-duration-fast, 120ms) ease;
}

.{{component_name}}-input:checked + .{{component_name}}-track {
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 15%, white);
}

.{{component_name}}-input:checked + .{{component_name}}-track .{{component_name}}-thumb {
  transform: translateX(20px);
}

.{{component_name}}-input:focus-visible + .{{component_name}}-track {
  outline: 2px solid color-mix(in srgb, var(--accent) 42%, transparent);
  outline-offset: 2px;
}

.{{component_name}}-input:disabled + .{{component_name}}-track {
  opacity: 0.6;
}

