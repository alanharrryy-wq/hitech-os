.{{component_name}}-root {
  display: grid;
  gap: var(--ui-core-space-2, 8px);
  color: var(--ui-text-1, rgba(16, 24, 40, 1));
}

.{{component_name}}-label {
  font-size: 0.95rem;
  font-weight: 600;
}

.{{component_name}}-hint {
  font-size: 0.8rem;
  color: var(--ui-text-2, rgba(71, 84, 103, 1));
}

.{{component_name}}-select {
  border: 1px solid var(--ui-border-1, rgba(208, 213, 221, 0.85));
  background: var(--ui-surface-1, rgba(255, 255, 255, 0.92));
  color: var(--ui-text-1, rgba(16, 24, 40, 1));
  border-radius: var(--ui-core-radius-md, 12px);
  padding: var(--ui-core-space-2, 8px) var(--ui-core-space-3, 12px);
}

.{{component_name}}-select:focus-visible {
  outline: 2px solid color-mix(in srgb, hsl(var(--ui-accent, 222 89% 55%)) 42%, transparent);
  outline-offset: 1px;
}

