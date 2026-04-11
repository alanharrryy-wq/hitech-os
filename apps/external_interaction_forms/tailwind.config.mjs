/** @type {import('tailwindcss').Config} */
const config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "rgb(var(--forms-canvas) / <alpha-value>)",
        panel: "rgb(var(--forms-panel) / <alpha-value>)",
        soft: "rgb(var(--forms-soft) / <alpha-value>)",
        ink: "rgb(var(--forms-ink) / <alpha-value>)",
        muted: "rgb(var(--forms-muted) / <alpha-value>)",
        line: "rgb(var(--forms-line) / <alpha-value>)",
        accent: "rgb(var(--forms-accent) / <alpha-value>)",
        accentSoft: "rgb(var(--forms-accent-soft) / <alpha-value>)",
        success: "rgb(var(--forms-success) / <alpha-value>)",
        danger: "rgb(var(--forms-danger) / <alpha-value>)"
      },
      boxShadow: {
        shell: "0 28px 70px rgba(15, 16, 23, 0.16)",
        soft: "0 10px 28px rgba(18, 22, 33, 0.1)"
      },
      borderRadius: {
        shell: "24px"
      }
    }
  },
  plugins: []
};

export default config;
