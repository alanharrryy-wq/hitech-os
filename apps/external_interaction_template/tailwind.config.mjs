/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        canvas: "rgb(var(--color-canvas) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        panel: "rgb(var(--color-panel) / <alpha-value>)",
        elevated: "rgb(var(--color-elevated) / <alpha-value>)",
        accent: "rgb(var(--color-accent) / <alpha-value>)",
        success: "rgb(var(--color-success) / <alpha-value>)",
        warning: "rgb(var(--color-warning) / <alpha-value>)",
        danger: "rgb(var(--color-danger) / <alpha-value>)",
        text: "rgb(var(--color-text) / <alpha-value>)",
        heading: "rgb(var(--color-heading) / <alpha-value>)",
        muted: "rgb(var(--color-muted) / <alpha-value>)",
        subtle: "rgb(var(--color-subtle) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        strong: "rgb(var(--color-border-strong) / <alpha-value>)"
      },
      boxShadow: {
        soft: "0 10px 30px rgba(2, 8, 20, 0.24), inset 0 1px 0 rgba(255,255,255,0.02)",
        floating: "0 20px 54px rgba(2, 8, 20, 0.38), inset 0 1px 0 rgba(255,255,255,0.03)",
        inset: "inset 0 1px 0 rgba(255,255,255,0.04)",
        focus: "0 0 0 1px rgba(112, 163, 255, 0.35), 0 0 0 4px rgba(112, 163, 255, 0.14)"
      },
      backdropBlur: {
        xs: "2px"
      }
    }
  },
  plugins: []
};

export default config;
