/** @type {import('tailwindcss').Config} */
const config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
    "../../packages/ui-kit/src/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: "hsl(var(--ui-bg))",
        "surface-1": "hsl(var(--ui-surface-1))",
        "surface-2": "hsl(var(--ui-surface-2))",
        accent: "hsl(var(--ui-accent))"
      }
    }
  },
  plugins: []
};

export default config;
